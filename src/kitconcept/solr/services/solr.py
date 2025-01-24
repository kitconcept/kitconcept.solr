from .solr_highlighting_utils import SolrHighlightingUtils
from .solr_params import SolrParams
from .solr_utils import escape
from .solr_utils import get_facet_fields_result
from .solr_utils import replace_colon
from .solr_utils import replace_reserved
from .solr_utils import SolrConfig
from AccessControl.SecurityManagement import getSecurityManager
from collective.solr.interfaces import ISolrConnectionManager
from itertools import zip_longest
from plone.restapi.services import Service
from Products.CMFPlone.utils import base_hasattr
from zope.component import queryUtility
from zope.interface import alsoProvides

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
        groups = ["user:%s" % x for x in user.getGroups()]
        if groups:
            roles = roles + groups
    roles.append("user:%s" % user.getId())
    # Roles with spaces need to be quoted
    roles = [
        (
            '"%s"' % escape(replace_colon(r))
            if " " in r
            else escape(replace_colon(r))
        )
        for r in roles
    ]
    return "allowedRolesAndUsers:(%s)" % " OR ".join(roles)


re_relative_path = re.compile("^/+")
re_is_excluding = re.compile("/$")


class SolrSearch(Service):
    def reply(self):
        solr_config = SolrConfig()
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection
            )

        params = SolrParams(self.context, self.request, solr_config)

        # Get the solr connection
        manager = queryUtility(ISolrConnectionManager)
        manager.setSearchTimeout()
        connection = manager.getConnection()

        # Note that both escaping and lowercasing reserved words is essential
        # against injection attacks.
        # We only lowercase AND, OR, NOT, but keep e.g. and or And
        # Also only lowercase a full word, and keep OReo intact.
        #
        # In addition. support empty search to search all terms, in case this
        # is configured.
        term = (
            "(" + escape(replace_reserved(params.query)) + ")"
            if params.query
            else "*"
        )

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
            "q": f"+(Title:{term}^5 OR Description:{term}^2 OR id:{term}^0.75 OR text_prefix:{term}^0.75 OR text_suffix:{term}^0.75 OR default:{term} OR body_text:{term} OR SearchableText:{term} OR Subject:{term} OR searchwords:({term})^1000) -showinsearch:False",  # noqa
            "wt": "json",
            "hl": "true",
            "hl.fl": "content",  # content only used for highlighting, the field is not indexed # noqa
            "fq": [security_filter()] + params.extra_fq(self.context),
            "fl": solr_config.field_list,
            "facet": "true",
            "facet.contains.ignoreCase": "true",
            "facet.field": list(
                map(
                    lambda info: params.facet_conditions.ex_field_facet(
                        info["name"]
                    )
                    + info["name"],
                    params.facet_fields,
                )
            ),
        }

        if params.start is not None:
            d["start"] = params.start
        if params.rows is not None:
            d["rows"] = params.rows
        if params.sort is not None:
            d["sort"] = params.sort
        if params.group_select is not None:
            d["fq"] = d["fq"] + [
                solr_config.select_condition(params.group_select)
            ]
        ex_all_facets = params.facet_conditions.ex_all_facets(
            extending=["typefilter"]
        )
        d["facet.query"] = list(
            map(
                lambda filter_condition: ex_all_facets + filter_condition,
                solr_config.filters,
            )
        )

        d.update(params.facet_conditions.contains_query)
        d.update(
            params.facet_conditions.more_query(
                params.facet_fields, multiplier=2
            )
        )

        highlighting_utils = SolrHighlightingUtils(solr_config)
        d["hl"] = "true" if highlighting_utils.enabled else "false"
        d["hl.fl"] = highlighting_utils.fields

        raw_result = connection.search(**d).read()

        result = json.loads(raw_result)
        # Add portal path to the result. This can be used by
        # the front-end to calculate the @id from the path_string
        # for each item.
        result["portal_path"] = params.portal_path
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
            params.facet_fields,
            params.facet_conditions.more_dict(
                params.facet_fields, multiplier=1
            ),
        )
        # Add highlighting information to the result
        highlighting_utils.enhance_items(
            result.get("response", {}).get("docs", []),
            result.get("highlighting", {}),
        )

        # Solr response is pruned of the unnecessary parts, unless explicitly requested.
        if not params.keep_full_solr_response:
            if "facet_counts" in result:
                del result["facet_counts"]
            if "highlighting" in result:
                del result["highlighting"]
        # Embellish result with supplemental information for the front-end
        if params.group_select is not None:
            layouts = solr_config.select_layouts(params.group_select)
            result["layouts"] = layouts
        return result
