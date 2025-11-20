from .solr import security_filter
from collective.solr.interfaces import ISolrConnectionManager
from kitconcept.solr.services.solr_utils import escape
from kitconcept.solr.services.solr_utils import replace_reserved
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryUtility

import json
import urllib


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
        d = {
            "q": (
                f"+suggest:{term}^10 OR +suggest_ngram:{term} OR +searchwords:{term}^1000 OR +suggest_searchwords_ngram:{term}"
            ),
            "fq": [
                security_filter(),
                "-showinsearch:False",
                "-portal_type:Image -portal_type:Glossary -portal_type:FAQ -portal_type:(FAQ Item) -portal_type:(FAQ Category) -portal_type:Link",
            ],
            "defType": "lucene",
        }

        if lang:
            d["fq"] = d["fq"] + ["Language:(" + escape(lang) + ")"]

        d["fq"] = " AND ".join(d["fq"])
        querystring = urllib.parse.urlencode(d)
        url = "{}/{}".format(connection.solrBase, "suggest?%s" % querystring)
        try:
            res = connection.doGet(url, {"Accept": "application/json"})
            data = json.loads(res.read())
        finally:
            if not connection.persistent:
                connection.conn.close()
        return data

    def serialize_brain(self, brain):
        if brain["portal_type"] in ["Member"]:
            obj = brain.getObject()
            data = getMultiAdapter((obj, self.request), ISerializeToJson)()
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
