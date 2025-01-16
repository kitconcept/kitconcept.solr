import re
from functools import reduce
from .solr_utils import escape
from .solr_utils import FacetConditions
from .solr_utils_extra import SolrExtraConditions
from plone import api
from zExceptions import BadRequest
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager

re_relative_path = re.compile("^/+")
re_is_excluding = re.compile("/$")


class SolrParams:

    def __init__(self, context, request, solr_config):
        form = request.form
        self.query = form.get("q", None)
        self.start = form.get("start", None)
        self.rows = form.get("rows", None)
        self.sort = form.get("sort", None)
        group_select = form.get("group_select", None)
        self.path_prefix = form.get("path_prefix", "")
        self.portal_type = form.get("portal_type", None)
        self.lang = form.get("lang", None)
        self.keep_full_solr_response = (
            form.get("keep_full_solr_response", "").lower() == "true"
        )

        # search in multilingual path_prefix by default - unless lang is specified
        is_multilinqual_txt = form.get(
            "is_multilingual", "true" if self.lang is None else "false"
        )
        self.is_multilingual = is_multilinqual_txt.lower() == "true"
        portal = api.portal.get()
        portal_path_segments = portal.getPhysicalPath()
        self.portal_path = "/".join(portal_path_segments)

        self.facet_conditions = FacetConditions.from_encoded(
            form.get("facet_conditions", None)
        )

        self.extra_conditions = SolrExtraConditions.from_encoded(
            form.get("extra_conditions", None)
        )

        if not self.path_prefix:
            # The path_prefix can optionally be used, but the root url is
            # used as default, in case path_prefix is undefined.
            context_path_segments = context.getPhysicalPath()
            # Acuqire relative path
            path_prefix_segments = context_path_segments[
                len(portal_path_segments) :
            ]
            self.path_prefix = "/".join(path_prefix_segments)

        if self.lang and self.is_multilingual:
            raise BadRequest(
                "Property 'lang` and `is_multilingual` are mutually exclusive"
            )

        if group_select is not None:
            try:
                self.group_select = int(group_select)
            except ValueError:
                raise BadRequest(
                    "Property 'group_select` must be an integer, if specified"
                )
        elif len(solr_config.filters) > 0:
            # By default select group 0 (unless there are no filters defined)
            self.group_select = 0

        self.facet_fields = (
            solr_config.select_facet_fields(group_select)
            if group_select is not None
            else []
        )

    def extra_fq(self, context):
        fq = []
        if self.path_prefix:
            is_excluding = re_is_excluding.search(self.path_prefix)
            if self.is_multilingual:
                # All the translation folders have to be queried, if the
                # multilingual option is selected. (By default.)
                relative_path = re_relative_path.sub("", self.path_prefix)
                folder = context.unrestrictedTraverse(relative_path)
                if ITranslatable.providedBy(folder):
                    translations = (
                        ITranslationManager(folder).get_translations().values()
                    )
                else:
                    # Untranslated
                    translations = [folder]
                path_list = map(
                    lambda o: "/".join(o.getPhysicalPath()), translations
                )
            else:
                # Not multilingual. Search stricly in the given path.
                if is_excluding:
                    self.path_prefix = self.path_prefix[:-1]
                path_list = [self.portal_path + self.path_prefix]
            if is_excluding:
                # Expressions with a trailing / will exclude the
                # parent folder and include everything else.
                path_expr = reduce(
                    lambda sum, path: sum
                    + [f"path_string:{escape(path + '/')}*"],
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
                fq += ["(" + " OR ".join(path_expr) + ")"]
        if self.portal_type:
            # Convert to Type condition.
            fq += [
                "Type:("
                + " OR ".join(
                    map(lambda txt: '"' + escape(txt) + '"', self.portal_type)
                )
                + ")"
            ]
        if self.lang:
            fq += ["Language:(" + escape(self.lang) + ")"]
        fq += self.facet_conditions.field_conditions_solr

        # extra_conditions = [
        #     [
        #         "start",
        #         "date-range",
        #         {"ge": "2021-07-19T13:00:00Z", "le": "2025-07-19T13:00:00Z"},
        #     ],
        # ]

        query_list = self.extra_conditions.query_list()
        fq += query_list

        return fq
