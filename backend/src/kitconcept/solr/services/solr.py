from AccessControl.SecurityManagement import getSecurityManager
from collective.solr.interfaces import ISolrConnectionManager
from itertools import zip_longest
from kitconcept.solr.services.solr_utils import escape
from kitconcept.solr.services.solr_utils import FacetConditions
from kitconcept.solr.services.solr_utils import get_facet_fields_result
from kitconcept.solr.services.solr_utils import replace_colon
from kitconcept.solr.services.solr_utils import replace_reserved
from kitconcept.solr.services.solr_utils import SolrConfig
from plone import api
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.base.utils import base_hasattr
from plone.dexterity.content import DexterityContent
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.publisher.http import HTTPRequest

import json
import plone.protect.interfaces
import re


def security_filter():
    user = getSecurityManager().getUser()
    roles = user.getRoles()
    if "Anonymous" in roles:
        return "allowedRolesAndUsers:Anonymous"
    roles = list(roles)
    roles.append("Anonymous")
    if base_hasattr(user, "getGroups"):
        groups = [f"user:{x}" for x in user.getGroups()]
        if groups:
            roles = roles + groups
    roles.append(f"user:{user.getId()}")
    # Roles with spaces need to be quoted
    roles = [
        (f'"{escape(replace_colon(r))}"' if " " in r else escape(replace_colon(r)))
        for r in roles
    ]
    return f"allowedRolesAndUsers:({' OR '.join(roles)})"


re_relative_path = re.compile("^/+")
re_is_excluding = re.compile("/$")


class SolrSearch(Service):
    context: DexterityContent
    request: HTTPRequest
    _facet_conditions: FacetConditions | None = None

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

    def _path_prefix(self, portal_path: list[str]) -> str:
        """Get the path prefix for the search."""

        if not (path_prefix := self.request.form.get("path_prefix", "")):
            # The path_prefix can optionally be used, but the root url is
            # used as default, in case path_prefix is undefined.
            context_path_segments = self.context.getPhysicalPath()
            # Acuqire relative path
            path_prefix_segments = context_path_segments[len(portal_path) :]
            path_prefix = "/".join(path_prefix_segments)
        return path_prefix

    def _group_select(self, solr_config: SolrConfig) -> int | None:
        group_select = self.request.form.get("group_select")
        if group_select is not None:
            try:
                group_select = int(group_select)
            except ValueError as exc:
                raise BadRequest(
                    "Property 'group_select` must be an integer, if specified"
                ) from exc
        elif len(solr_config.filters) > 0:
            # By default select group 0 (unless there are no filters defined)
            group_select = 0
        return group_select

    @property
    def facet_conditions(self) -> FacetConditions:
        """Get the facet conditions from the request."""
        if self._facet_conditions is None:
            raw_value = self.request.form.get("facet_conditions")
            self._facet_conditions = FacetConditions.from_encoded(raw_value)
        return self._facet_conditions

    def _facet_fields(
        self, solr_config: SolrConfig, group_select: int | None
    ) -> list[dict]:
        """Get the facet fields to be used in the query."""
        facet_fields = (
            solr_config.select_facet_fields(group_select)
            if group_select is not None
            else []
        )
        return facet_fields

    def _base_query(
        self,
        solr_config: SolrConfig,
        query: str,
        facet_fields: list[dict],
        group_select: int | None,
        start,
        rows,
        sort,
    ) -> dict:
        """Create a base query for the Solr search."""
        # Note that both escaping and lowercasing reserved words is essential
        # against injection attacks.
        # We only lowercase AND, OR, NOT, but keep e.g. and or And
        # Also only lowercase a full word, and keep OReo intact.
        #
        # In addition. support empty search to search all terms, in case this
        # is configured.
        term = f"({escape(replace_reserved(query))})" if query else "*"

        # Search
        #  q: query parameter
        # fq: the "filter query" parameter allows to restrict the search by filtering
        #     the results
        #     we use the fq param to enforce the allowedRolesAndUsers filter criteria
        # hl: enable highlighting (if set to true)
        # hl.fl: specify the fields to highlight, field needs to have stored=true in
        #     solconf.xml
        # hl.fragsize: set in search.py in collective.solr with 'highlight_fragsize'
        #     param
        # fl: the "field list" parameter defines which fields to include in the response
        # facet: enable faceting (if set to true)
        # facet.field: the fields to facet on
        #
        # Importance:
        #
        # - Title * 5
        # - Description * 2
        # - SearchableText * 1
        # - default * 1
        # - body_text * 1
        # - Subject * 1
        # - ID * 0,75
        # - Text Prefix * 0,75
        # - Text Suffix * 0,75
        # - Text Substring * 0,5
        # - searchwords * 1000
        d = {
            "q": (
                f"+(Title:{term}^5 OR Description:{term}^2 OR id:{term}^0.75 "
                f"OR text_prefix:{term}^0.75 OR text_suffix:{term}^0.75 "
                f"OR default:{term} OR body_text:{term} OR SearchableText:{term} "
                f"OR Subject:{term} OR searchwords:({term})^1000) -showinsearch:False"
            ),
            "wt": "json",
            "hl": "true",
            "hl.fl": "content",  # only used for highlighting, field is not indexed
            "fq": [security_filter()],
            "fl": solr_config.field_list,
            "facet": "true",
            "facet.contains.ignoreCase": "true",
            "facet.field": [
                f"{'{!ex=conditionfilter}' if self.facet_conditions.solr else ''}"
                f"{info['name']}"
                for info in facet_fields
            ],
        }
        if start is not None:
            d["start"] = start
        if rows is not None:
            d["rows"] = rows
        if sort is not None:
            d["sort"] = sort

        if group_select is not None:
            d["fq"] = d["fq"] + [solr_config.select_condition(group_select)]
            prefix = (
                "{!ex=typefilter,conditionfilter}"
                if self.facet_conditions.solr
                else "{!ex=typefilter}"
            )
            d["facet.query"] = [f"{prefix}{query}" for query in solr_config.filters]
        return d

    def _apply_facet_conditions(self, query: dict, facet_fields: list[dict]) -> dict:
        """Apply the facet conditions to the query."""
        fc = self.facet_conditions
        # Handle facet conditions
        if fc.solr:
            query["fq"] = query["fq"] + ["{!tag=conditionfilter}" + fc.solr]
        query.update(fc.contains_query)
        query.update(fc.more_query(facet_fields, multiplier=2))
        return query

    def search_solr(self, query: dict) -> dict:
        """Search Solr for the given query."""
        # Get the solr connection
        manager = queryUtility(ISolrConnectionManager)
        manager.setSearchTimeout()
        connection = manager.getConnection()
        raw_result = connection.search(**query).read()
        result = json.loads(raw_result)
        return result

    def enhance_result(
        self,
        result: dict,
        solr_config,
        portal_path: str,
        facet_fields,
        keep_full_solr_response: bool,
        group_select,
    ) -> dict:
        """Enhance the Solr search result."""
        # Add portal path to the result. This can be used by
        # the front-end to calculate the @id from the path_string
        # for each item.
        result["portal_path"] = portal_path
        # Add the group counts in order. Needed because the
        # facet_queries dictionary will not preserve key order, when
        # marshalled to the client.
        # Also add the faces labels next to the corresponding counts.
        result["facet_groups"] = list(
            zip_longest(
                solr_config.labels,
                result["facet_counts"]["facet_queries"].values(),
            )
        )
        result["facet_fields"] = get_facet_fields_result(
            result["facet_counts"]["facet_fields"],
            facet_fields,
            self.facet_conditions.more_dict(facet_fields, multiplier=1),
        )
        # Solr response is pruned of the unnecessary parts, unless explicitly requested.
        if not keep_full_solr_response:
            del result["facet_counts"]
        # Embellish result with supplemental information for the front-end
        if group_select is not None:
            layouts = solr_config.select_layouts(group_select)
            result["layouts"] = layouts
        return result

    def reply(self):
        solr_config = SolrConfig()
        form: dict = self.request.form
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        query = form.get("q", "")
        start = form.get("start")
        rows = form.get("rows")
        sort = form.get("sort")
        portal_type = form.get("portal_type")
        keep_full_solr_response = (
            form.get("keep_full_solr_response", "").lower() == "true"
        )

        is_multilingual, lang = self._language_settings()
        portal = api.portal.get()
        portal_path_segments = portal.getPhysicalPath()
        portal_path = "/".join(portal_path_segments)
        path_prefix = self._path_prefix(portal_path_segments)

        group_select = self._group_select(solr_config)
        facet_fields = self._facet_fields(solr_config, group_select)

        d = self._base_query(
            solr_config, query, facet_fields, group_select, start, rows, sort
        )

        if path_prefix:
            is_excluding = re_is_excluding.search(path_prefix)
            if is_multilingual:
                # All the translation folders have to be queried, if the
                # multilingual option is selected. (By default.)
                relative_path = re_relative_path.sub("", path_prefix)
                folder = self.context.unrestrictedTraverse(relative_path)
                if ITranslatable.providedBy(folder):
                    translations = (
                        ITranslationManager(folder).get_translations().values()
                    )
                else:
                    # Untranslated
                    translations = [folder]
                path_list = ("/".join(o.getPhysicalPath()) for o in translations)
            else:
                # Not multilingual. Search stricly in the given path.
                if is_excluding:
                    path_prefix = path_prefix[:-1]
                path_list = [portal_path + path_prefix]
            if is_excluding:
                # Expressions with a trailing / will exclude the
                # parent folder and include everything else.
                path_expr = [f"path_string:{escape(path + '/')}*" for path in path_list]
            else:
                # Expression that include a folder must be split up to
                # two conditions, to avoid `/something` to match
                # '/something-else'.
                path_expr = [
                    expr
                    for path in path_list
                    for expr in (
                        f"path_string:{escape(path)}",
                        f"path_string:{escape(path + '/')}*",
                    )
                ]
            if len(path_expr) > 0:
                d["fq"] = d["fq"] + ["(" + " OR ".join(path_expr) + ")"]
        if portal_type:
            # Convert to Type condition.
            escaped = [f'"{escape(txt)}"' for txt in portal_type]
            d["fq"] = d["fq"] + [f"Type:({' OR '.join(escaped)})"]
        if lang:
            d["fq"] = d["fq"] + ["Language:(" + escape(lang) + ")"]

        d = self._apply_facet_conditions(d, facet_fields)

        # Run search and enhance the result
        result = self.enhance_result(
            self.search_solr(query=d),
            solr_config,
            portal_path,
            facet_fields,
            keep_full_solr_response,
            group_select,
        )
        return result
