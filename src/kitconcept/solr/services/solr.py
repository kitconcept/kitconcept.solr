from AccessControl.SecurityManagement import getSecurityManager
from collective.solr.interfaces import ISolrConnectionManager
from functools import reduce
from itertools import zip_longest
from kitconcept.solr.services.solr_utils import SolrConfig
from plone import api
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.services import Service
from Products.CMFPlone.utils import base_hasattr
from zExceptions import BadRequest
from zope.component import queryUtility
from zope.interface import alsoProvides

import json
import plone.protect.interfaces
import re


SPECIAL_CHARS = [
    "+",
    "-",
    #    "&&",
    #    "||",
    "&",
    "|",
    "!",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    "^",
    '"',
    "~",
    "*",
    "?",
    ":",
    "/",
]


def escape(term):
    for char in SPECIAL_CHARS:
        term = term.replace(char, "\\" + char)
    return term


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
    roles = ['"%s"' % escape(r) if " " in r else escape(r) for r in roles]
    return "allowedRolesAndUsers:(%s)" % " OR ".join(roles)


re_relative_path = re.compile("^/+")
re_is_excluding = re.compile("/$")


class SolrSearch(Service):
    def reply(self):
        solr_config = SolrConfig()
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        query = self.request.form.get("q", None)
        start = self.request.form.get("start", None)
        rows = self.request.form.get("rows", None)
        sort = self.request.form.get("sort", None)
        group_select = self.request.form.get("group_select", None)
        path_prefix = self.request.form.get("path_prefix", "")
        portal_type = self.request.form.get("portal_type", None)
        lang = self.request.form.get("lang", None)
        keep_full_solr_response = (
            self.request.form.get("keep_full_solr_response", "").lower() == "true"
        )

        # search in multilingual path_prefix by default - unless lang is specified
        is_multilinqual_txt = self.request.form.get(
            "is_multilingual", "true" if lang is None else "false"
        )
        is_multilingual = is_multilinqual_txt.lower() == "true"
        portal = api.portal.get()
        portal_path_segments = portal.getPhysicalPath()
        portal_path = "/".join(portal_path_segments)

        if not query:
            raise BadRequest("Property 'q' is required")

        if not path_prefix:
            # The path_prefix can optionally be used, but the root url is
            # used as default, in case path_prefix is undefined.
            context_path_segments = self.context.getPhysicalPath()
            # Acuqire relative path
            path_prefix_segments = context_path_segments[len(portal_path_segments) :]
            path_prefix = "/".join(path_prefix_segments)

        if lang and is_multilingual:
            raise BadRequest(
                "Property 'lang` and `is_multilingual` are mutually exclusive"
            )

        # Get the solr connection
        manager = queryUtility(ISolrConnectionManager)
        manager.setSearchTimeout()
        connection = manager.getConnection()

        # XXX: we need to filter the query to avoid injection attacks
        term = escape(query)

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
            "fq": [security_filter()],
            "fl": solr_config.field_list,
            "facet": "true",
        }
        if start is not None:
            d["start"] = start
        if rows is not None:
            d["rows"] = rows
        if sort is not None:
            d["sort"] = sort
        if group_select is not None:
            d["fq"] = d["fq"] + [solr_config.select_condition(int(group_select))]
        d["facet.query"] = solr_config.facet_query
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
                path_list = map(lambda o: "/".join(o.getPhysicalPath()), translations)
            else:
                # Not multilingual. Search stricly in the given path.
                if is_excluding:
                    path_prefix = path_prefix[:-1]
                path_list = [portal_path + path_prefix]
            if is_excluding:
                # Expressions with a trailing / will exclude the
                # parent folder and include everything else.
                path_expr = reduce(
                    lambda sum, path: sum + [f"path_string:{escape(path + '/')}*"],
                    path_list,
                    [],
                )
            else:
                # Expression that include a folder must be split up to
                # two conditions, to avoid `/something` to match
                # '/something-else'.
                path_expr = reduce(
                    lambda sum, path: sum
                    + [
                        f"path_string:{escape(path)}",
                        f"path_string:{escape(path + '/')}*",
                    ],
                    path_list,
                    [],
                )
            if len(path_expr) > 0:
                d["fq"] = d["fq"] + ["(" + " OR ".join(path_expr) + ")"]
        if portal_type:
            # Convert to Type condition.
            d["fq"] = d["fq"] + [
                "Type:("
                + " OR ".join(map(lambda txt: '"' + escape(txt) + '"', portal_type))
                + ")"
            ]
        if lang:
            d["fq"] = d["fq"] + ["Language:(" + escape(lang) + ")"]

        raw_result = connection.search(**d).read()

        result = json.loads(raw_result)
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
                solr_config.labels, result["facet_counts"]["facet_queries"].values()
            )
        )
        # Solr response is pruned of the unnecessary parts, unless explicitly requested.
        if not keep_full_solr_response:
            del result["facet_counts"]
        return result
