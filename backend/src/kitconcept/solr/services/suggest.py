from .solr import security_filter
from collective.solr.interfaces import ISolrConnectionManager
from kitconcept.solr.services.solr_utils import escape
from kitconcept.solr.services.solr_utils import replace_reserved
from kitconcept.solr.services.solr_utils_extra import SolrExtraConditions
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryUtility

import json
import urllib


# Portal types serialized in full instead of from the catalog brain, because
# the suggest dropdown renders more than title and type for them.
FULL_SERIALIZATION_TYPES = ("Member",)


class SolrSuggest(Service):
    def _language_settings(self) -> tuple[bool, str]:
        lang = self.request.form.get("lang")
        # search in multilingual path_prefix by default - unless lang is specified
        is_multilinqual_txt = self.request.form.get(
            "is_multilingual", "true" if lang is None else "false"
        )
        is_multilingual = is_multilinqual_txt.lower() == "true"
        if lang and is_multilingual:
            raise BadRequest(
                "Property 'lang` and `is_multilingual` are mutually exclusive"
            )
        return is_multilingual, lang

    def query_suggest(self, query):
        manager = queryUtility(ISolrConnectionManager)
        if manager is None:
            return {"error": "Solr is not installed or activated"}
        connection = manager.getConnection()
        if connection is None:
            return {"error": "Solr is not installed or activated"}
        data = {"error": "no response"}
        _, lang = self._language_settings()
        term = f"({escape(replace_reserved(query))})" if query else "*"

        # Optional filters, same mechanism and encoding as the @solr
        # endpoint's extra_conditions parameter (search dialog filter
        # chips, ticket 585): a base64 encoded JSON list of
        # [fieldname, kind, condition] rows.
        extra_conditions = SolrExtraConditions.from_encoded(
            self.request.form.get("extra_conditions")
        )
        extra_fq = extra_conditions.query_list()
        # An explicit type filter wins over the built-in exclusions:
        # the exclusion list keeps noise (e.g. images) out of the
        # default suggestions, but a user who filters for exactly such
        # a type must see it.
        has_type_filter = any(
            row and row[0] in ("portal_type", "Type")
            for row in extra_conditions.config
            if isinstance(row, (list, tuple))
        )
        type_exclusions = (
            []
            if has_type_filter
            else [
                (
                    "-portal_type:Image -portal_type:Glossary -portal_type:FAQ "
                    "-portal_type:(FAQ Item) -portal_type:(FAQ Category) "
                    "-portal_type:Link"
                )
            ]
        )

        d = {
            "q": (
                f"+suggest:{term}^10 OR +suggest_ngram:{term} "
                f"OR +searchwords:{term}^1000 OR +suggest_searchwords_ngram:{term}"
            ),
            "fq": [
                security_filter(),
                "-showinsearch:False",
                *type_exclusions,
                *extra_fq,
            ],
            "defType": "lucene",
        }

        if lang:
            d["fq"] = d["fq"] + ["Language:(" + escape(lang) + ")"]

        # Optional path scoping: restricts suggestions to a subtree,
        # e.g. a subsite or workspace, matching the local search.
        if path_prefix := self.request.form.get("path_prefix", "").strip():
            portal_path = "/".join(api.portal.get().getPhysicalPath())
            prefix = portal_path + path_prefix.rstrip("/")
            d["fq"] = d["fq"] + [f'path_parents:"{prefix}"']

        d["fq"] = " AND ".join(d["fq"])
        querystring = urllib.parse.urlencode(d)
        url = "{}/{}".format(connection.solrBase, f"suggest?{querystring}")
        try:
            res = connection.doGet(url, {"Accept": "application/json"})
            data = json.loads(res.read())
        finally:
            if not connection.persistent:
                connection.conn.close()
        return data

    def serialize_brain(self, brain):
        if brain["portal_type"] in FULL_SERIALIZATION_TYPES:
            obj = brain.getObject()
            # `include_items=False` matters for folderish types: plone.restapi
            # picks SerializeFolderToJson for them, which would otherwise run a
            # catalog query per suggestion and embed the whole child listing in
            # the response. The plain SerializeToJson accepts and ignores the
            # keyword, so no type check is needed here.
            # `include_expansion=False` drops the `@components` expansion
            # links (breadcrumbs, navigation, actions...), which the suggest
            # dropdown never follows.
            data = getMultiAdapter((obj, self.request), ISerializeToJson)(
                include_items=False, include_expansion=False
            )
            data["@id"] = obj.absolute_url()
            return data

        return getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

    def parse_response(self, data):
        if "error" in data or "response" not in data:
            error = {"suggestions": [], "error": "No response from solr"}
            if "error" in data:
                error["error"] = data["error"]
            return error
        uids = [doc["UID"] for doc in data["response"]["docs"]]
        brains = {brain["UID"]: brain for brain in api.content.find(UID=uids)}
        return [self.serialize_brain(brains[uid]) for uid in uids if uid in brains]

    def reply(self):
        query = self.request.form.get("query", "")
        data = self.query_suggest(query)
        data = self.parse_response(data)
        if isinstance(data, dict):
            return data
        return {"suggestions": data}
