from collections import defaultdict
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import INavigationSchema
from plone.restapi.bbb import safe_text
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from plone.restapi.services.navigation.get import Navigation


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class NavigationWithExcluded(Navigation):
    """Navigation expander that includes all items, even those excluded from navigation.

    This is specifically used for breadcrumbs in global search results where we need
    to show the breadcrumb titles for an item, regardless of whether intermediate items are
    marked as 'exclude_from_nav'.

    It inherits from the standard Navigation expander but overrides the settings
    to ensure show_excluded_items is always True.
    """

    def __call__(self, expand=False):
        if self.request.form.get(
            "expand.navigation_with_excluded.depth", False
        ):
            self.depth = int(
                self.request.form["expand.navigation_with_excluded.depth"]
            )
        else:
            self.depth = 1

        result = {
            "navigation_with_excluded": {
                "@id": f"{self.context.absolute_url()}/@navigation_with_excluded"
            }
        }
        if not expand:
            return result

        result["navigation_with_excluded"]["items"] = self.build_tree(
            self.navtree_path
        )
        return result

    @property
    @memoize_contextless
    def settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        return {
            "displayed_types": settings.displayed_types,
            "nonfolderish_tabs": settings.nonfolderish_tabs,
            "filter_on_workflow": settings.filter_on_workflow,
            "workflow_states_to_show": settings.workflow_states_to_show,
            # Always show excluded items
            "show_excluded_items": True,
        }

    @property
    @memoize
    def navtree(self):
        ret = defaultdict(list)
        navtree_path = self.navtree_path
        for tab in self.portal_tabs:
            entry = {}
            entry.update(
                {
                    "path": "/".join((navtree_path, tab["id"])),
                    "description": tab["description"],
                    "@id": tab["url"],
                }
            )
            if "review_state" in tab:
                entry["review_state"] = json_compatible(tab["review_state"])
            else:
                entry["review_state"] = None

            if "title" not in entry:
                entry["title"] = (
                    tab.get("name") or tab.get("description") or tab["id"]
                )
            else:
                # translate Home tab
                entry["title"] = translate(
                    entry["title"], domain="plone", context=self.request
                )

            entry["title"] = safe_text(entry["title"])
            ret[navtree_path].append(entry)

        query = {
            "path": {
                "query": self.navtree_path,
                "depth": self.depth,
            },
            "portal_type": {"query": self.settings["displayed_types"]},
            "Language": self.current_language,
            "is_default_page": False,
            "sort_on": "getObjPositionInParent",
        }

        if not self.settings["nonfolderish_tabs"]:
            query["is_folderish"] = True

        if self.settings["filter_on_workflow"]:
            query["review_state"] = list(
                self.settings["workflow_states_to_show"] or ()
            )

        # if not self.settings["show_excluded_items"]:
        #     query["exclude_from_nav"] = False

        context_path = "/".join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self.context, "portal_catalog")
        brains = portal_catalog.searchResults(**query)

        registry = getUtility(IRegistry)
        types_using_view = registry.get(
            "plone.types_use_view_action_in_listings", []
        )

        for brain in brains:
            brain_path = brain.getPath()
            brain_parent_path = brain_path.rpartition("/")[0]
            # if brain_parent_path == navtree_path:
            #     # This should be already provided by the portal_tabs_view
            #     # continue
            #     pass

            # if brain.exclude_from_nav and not f"{brain_path}/".startswith(
            #     f"{context_path}/"
            # ):
            #     # skip excluded items if they're not in our context path
            #     # continue
            #     pass
            url = brain.getURL()

            entry = {
                "path": brain_path,
                "@id": url,
                "title": safe_text(brain.Title),
                # "description": safe_text(brain.Description),
                # "review_state": json_compatible(brain.review_state),
                # "use_view_action_in_listings": brain.portal_type in types_using_view,
            }
            if "nav_title" in brain and brain.nav_title:
                entry.update({"title": brain.nav_title})

            self.customize_entry(entry, brain)
            ret[brain_parent_path].append(entry)
        return ret

    def render_item(self, item, path):
        if "path" in item:
            item_path = item["path"]
        else:
            # Path not found. Use the @id to build the path.
            item_path = (
                self.navtree_path + "/" + "/".join(item["@id"].split("/")[4:])
            )

        sub = self.build_tree(item_path, first_run=False)

        item.update({"items": sub})

        if "path" in item:
            del item["path"]
        return item


class NavigationWithExcludedGet(Service):
    """REST API endpoint that returns navigation data including excluded items.

    This service is used to get breadcrumb navigation data for search results,
    ensuring that the breadcrumb titles for any item can be displayed even if parent
    items are marked as excluded from navigation.
    """

    def reply(self):
        navigation_with_excluded = NavigationWithExcluded(
            self.context, self.request
        )
        return navigation_with_excluded(expand=True)[
            "navigation_with_excluded"
        ]
