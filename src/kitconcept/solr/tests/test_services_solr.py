from collective.solr.testing import activateAndReindex
from kitconcept.solr.services import solr_facet_utils
from kitconcept.solr.testing import KITCONCEPT_SOLR_FUNCTIONAL_TESTING
from kitconcept import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.namedfile.file import NamedBlobFile
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import ILanguage
from unittest import mock

import os
import transaction
import unittest


def get_path_strings(response):
    return list(
        map(lambda doc: doc["path_string"], response.json()["response"]["docs"])
    )


# Mock the configuration
#
# Note that the Document type has to be searched as Page,
# ie: portal_type=Document, but Type=Page.
solr_config = {
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
        {
            "label": "Pages",
            "filter": "Type:(Page)",
        },
        {
            "label": "News Items",
            "filter": 'Type:("News Item")',
        },
        {
            "label": "Pages and News Items",
            "filter": 'Type:(Page OR "News Item")',
        },
    ]
}


@mock.patch("kitconcept.solr.services.solr_facet_utils.solr_config", solr_config)
@mock.patch("kitconcept.solr.services.solr_facet_utils.filters", None)
class ServicesSolrFacetUtilsTestCase(unittest.TestCase):
    def test_get_filters(self):
        self.assertEqual(
            solr_facet_utils.get_filters(),
            [
                "Type(*)",
                "Type:(Page)",
                'Type:("News Item")',
                'Type:(Page OR "News Item")',
            ],
        )


@mock.patch("kitconcept.solr.services.solr_facet_utils.solr_config", solr_config)
@mock.patch("kitconcept.solr.services.solr_facet_utils.filters", None)
class ServicesSolrFacetsTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.portal.invokeFactory(
            "Image",
            id="noamchomsky",
            title="Prof. Dr. Noam Chomsky",
        )
        self.portal.noamchomsky.setSubject(["mymembersubject", "mymembersubjecttwo"])
        self.portal.invokeFactory(
            "Document",
            id="mydocument",
            title="My Document about Noam Chomsky",
        )
        self.portal.invokeFactory(
            "News Item",
            id="mynews",
            title="My News Item with Noam Chomsky",
        )
        transaction.commit()

    def test_group_select_1(self):
        """baseline test group=Page"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&group_select=1"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/mydocument", path_strings)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertNotIn("/plone/mynews", path_strings)

    def test_facet_all_group_default(self):
        response = self.api_session.get("%s/@solr?q=chomsky" % self.portal_url)
        self.assertIn("response", response.json())
        self.assertEqual(
            response.json().get("group_counts"),
            [3, 1, 1, 2],
        )
        path_strings = get_path_strings(response)
        self.assertIn("/plone/mydocument", path_strings)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)

    def test_facet_all_group(self):
        # "filter": "Type(*)",
        response = self.api_session.get(
            "%s/@solr?q=chomsky&group_select=0" % self.portal_url
        )
        self.assertIn("response", response.json())
        self.assertEqual(
            response.json().get("group_counts"),
            [3, 1, 1, 2],
        )
        path_strings = get_path_strings(response)
        self.assertIn("/plone/mydocument", path_strings)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)

    def test_facet_group_simple(self):
        # "filter": "Type:(Image)",
        response = self.api_session.get(
            "%s/@solr?q=chomsky&group_select=1" % self.portal_url
        )
        self.assertIn("response", response.json())
        self.assertEqual(
            response.json().get("group_counts"),
            [3, 1, 1, 2],
        )
        path_strings = get_path_strings(response)
        self.assertIn("/plone/mydocument", path_strings)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertNotIn("/plone/mynews", path_strings)

    def test_facet_group_composite(self):
        # "filter": "Type(Page OR News Item)",
        response = self.api_session.get(
            "%s/@solr?q=chomsky&group_select=3" % self.portal_url
        )
        self.assertIn("response", response.json())
        self.assertEqual(
            response.json().get("group_counts"),
            [3, 1, 1, 2],
        )
        path_strings = get_path_strings(response)
        self.assertIn("/plone/mydocument", path_strings)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)

    def test_portal_path(self):
        """portal_path is returned for the client"""
        response = self.api_session.get(f"{self.portal_url}/@solr?q=chomsky")
        self.assertEqual(response.json()["portal_path"], "/plone")

    def test_portal_path_on_object_context_with_prefix(self):
        """portal_path is always the root, even if called on object context"""
        api.content.create(
            container=self.portal,
            type="Document",
            id="myotherfolder",
            title="My other Folder",
        )
        transaction.commit()
        response = self.api_session.get(
            f"{self.portal_url}/myotherfolder/@solr?q=chomsky"
        )
        self.assertEqual(response.json()["portal_path"], "/plone")


class ServicesSolrLocalizedTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        api.content.create(
            container=self.portal,
            type="Image",
            id="noamchomsky",
            title="Prof. Dr. Noam Chomsky",
        )
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myfolder",
            title="My Folder to store everything about Noam Chomsky",
        )
        api.content.create(
            container=self.portal.myfolder,
            type="Document",
            id="mydocument",
            title="My Document about Noam Chomsky",
        )
        api.content.create(
            container=self.portal.myfolder,
            type="News Item",
            id="mynews",
            title="My News Item with Noam Chomsky",
        )
        transaction.commit()

    def test_solr_global(self):
        """search without a prefix"""
        response = self.api_session.get(f"{self.portal_url}/@solr?q=chomsky")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder", path_strings)

    def test_solr_local_including_parent(self):
        """search for all matching objects in a folder, including the parent"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder", path_strings)

    def test_solr_local_excluding_parent(self):
        """search for all matching objects in a folder, excluding the parent"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder/"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder", path_strings)

    def test_solr_local_site_root(self):
        """search for all objects in the site with a slash prefix"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder", path_strings)

    def test_solr_local_on_object_context(self):
        """search for all matching objects in a folder, including the parent.
        Called on object context, no path_prefix parameter."""
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myotherfolder",
            title="My other Folder",
        )
        transaction.commit()
        response = self.api_session.get(f"{self.portal_url}/myfolder/@solr?q=chomsky")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder", path_strings)

    def test_solr_local_on_object_context_with_prefix(self):
        """search for all matching objects in a folder, including the parent.
        Called on object context with path_prefix which overrides the context."""
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myotherfolder",
            title="My other Folder",
        )
        transaction.commit()
        response = self.api_session.get(
            f"{self.portal_url}/myotherfolder/@solr?q=chomsky&path_prefix=/myfolder"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder", path_strings)

    def test_portal_path_on_object_context_with_prefix(self):
        """search for all matching objects in a folder, including the parent.
        Called on object context with path_prefix which overrides the context."""
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myotherfolder",
            title="My other Folder",
        )
        transaction.commit()
        response = self.api_session.get(
            f"{self.portal_url}/myotherfolder/@solr?q=chomsky&path_prefix=/myfolder"
        )
        # portal_path depends on the portal path, independent from context.
        self.assertEqual(response.json()["portal_path"], "/plone")

    def setup_multilingual_content(self):
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myfolder_ca",
            title="My Folder to store everything about Noam Chomsky in Canadian",
        )
        api.content.create(
            container=self.portal.myfolder_ca,
            type="Document",
            id="mydocument",
            title="My Document about Noam Chomsky in Canadian",
        )
        ILanguage(self.portal.myfolder).set_language("en")
        ILanguage(self.portal.myfolder_ca).set_language("ca")
        ITranslationManager(self.portal.myfolder).register_translation(
            "ca", self.portal.myfolder_ca
        )
        transaction.commit()

    def test_solr_multilingual(self):
        """multilingual results"""
        self.setup_multilingual_content()
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder_ca/mydocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertIn("/plone/myfolder_ca", path_strings)
        # Any translated folder looks up all results
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder_ca"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertIn("/plone/myfolder_ca/mydocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertIn("/plone/myfolder_ca", path_strings)

    def test_solr_multilingual_disabled(self):
        """multilingual results disabled"""
        self.setup_multilingual_content()
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder"
            + "&is_multilingual=false"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder_ca/mydocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertNotIn("/plone/myfolder_ca", path_strings)
        # Any translated folder gives its own result
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder_ca"
            + "&is_multilingual=false"
        )
        self.assertIn("response", response.json())
        self.assertNotIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/myfolder/mydocument", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder_ca/mydocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertNotIn("/plone/myfolder_ca", path_strings)


def _get_file() -> NamedBlobFile:
    filepath = os.path.join(os.path.dirname(__file__), "joboffer.pdf")
    with open(filepath, "rb") as f_in:
        data = f_in.read()
    return NamedBlobFile(data, "application/pdf", "joboffer.pdf")


class ServicesSolrContentFieldsTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # Person
        api.content.create(
            container=self.portal,
            type="News Item",
            id="news1",
            title="News Item 1",
        )
        api.content.create(
            container=self.portal,
            type="News Item",
            id="news2",
            title="News Item 2",
            location="",
        )
        api.content.create(
            container=self.portal,
            type="News Item",
            id="news3",
            title="News Item 3",
            location="My location",
        )
        transaction.commit()

    def test_find_term_in_id_field(self):
        api.content.create(
            container=self.portal,
            type="Document",
            id="redandblue",
            title="This is a title",
        )
        transaction.commit()
        response = self.api_session.get(f"{self.portal_url}/@solr?q=red")
        self.assertIn("response", response.json())
        self.assertEqual(1, response.json()["response"]["numFound"])
        self.assertEqual(
            "This is a title",
            response.json()["response"]["docs"][0]["Title"],
        )

    def test_news_fields(self):
        """Fields in News Item"""
        response = self.api_session.get(f"{self.portal_url}/@solr?q=news")
        self.assertIn("response", response.json())
        self.assertEqual(3, response.json()["response"]["numFound"])
        self.assertTrue("location" not in response.json()["response"]["docs"][0])
        # self.assertTrue("location" not in response.json()["response"]["docs"][1])
        self.assertEqual(
            "",
            response.json()["response"]["docs"][1]["location"],
        )
        self.assertEqual(
            "My location",
            response.json()["response"]["docs"][2]["location"],
        )

    # XXX This should be passing!
    # After setting an attribute to "", it should be updated in the next search.
    @unittest.skip(
        reason="setting an index to empty does not currently update the field in the results"  # noqa
    )
    def test_news_fields_modify(self):
        """Emptying the field should reindex it"""
        response = self.api_session.get(f"{self.portal_url}/@solr?q=news")
        self.assertIn("response", response.json())
        self.assertEqual(3, response.json()["response"]["numFound"])
        self.assertEqual(
            "My location",
            response.json()["response"]["docs"][2]["location"],
        )
        # XXX Reality check... this should pass because this is working manually
        # through the app.
        self.portal.news3.location = "Another location"
        transaction.commit()
        response = self.api_session.get(f"{self.portal_url}/@solr?q=news")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)

        print(path_strings)
        self.assertEqual(3, response.json()["response"]["numFound"])
        self.assertEqual(
            "Another location",
            response.json()["response"]["docs"][2]["location"],
        )
        # Setting the attribute to empty should update the index
        # XXX This is currently broken manually. If I set the location to "" through
        # the app, the search still continues to return the previous value.
        self.portal.news3.location = ""
        transaction.commit()
        response = self.api_session.get(f"{self.portal_url}/@solr?q=news")
        self.assertIn("response", response.json())
        self.assertEqual(3, response.json()["response"]["numFound"])
        # print(response.json()["response"]["docs"])
        self.assertTrue("location" not in response.json()["response"]["docs"][2])


SECOND_USER_ID = "user2"
SECOND_USER_PW = "secret"

# Mock the configuration
#
# Note that the Document type has to be searched as Page,
# ie: portal_type=Document, but Type=Page.
solr_config_for_perms = {
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
        {
            "label": "Pages",
            "filter": "Type:(Page)",
        },
        {
            "label": "News Items",
            "filter": 'Type:("News Item")',
        },
        {
            "label": "Images and News Items",
            "filter": 'Type:(Image OR "News Item")',
        },
        {
            "label": "Pages and News Items",
            "filter": 'Type:(Page OR "News Item")',
        },
        {
            "label": "Contacts",
            "filter": "Type:(Image)",
        },
    ]
}


@mock.patch(
    "kitconcept.solr.services.solr_facet_utils.solr_config", solr_config_for_perms
)
@mock.patch("kitconcept.solr.services.solr_facet_utils.filters", None)
class ServicesSolrPermissionsTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Anonymous"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        # Solr will authenticate as a user who is not Manager
        self.api_session.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.portal.acl_users.userFolderAddUser(
            SECOND_USER_ID, SECOND_USER_PW, ["Manager"], []
        )
        login(self.portal, SECOND_USER_ID)
        api.content.create(
            container=self.portal,
            type="Image",
            id="noamchomsky",
            title="Image of Prof. Dr. Noam Chomsky",
        )
        self.portal.invokeFactory(
            "Document",
            id="chomskysdocument",
            title="Noam Chomsky's private document",
        )
        # api.content.transition(obj=self.portal.noamchomsky, transition="publish")
        self.portal.invokeFactory(
            "News Item",
            id="mynews",
            title="My News Item with Noam Chomsky",
        )
        api.content.transition(obj=self.portal.mynews, transition="publish")
        api.content.create(
            container=self.portal,
            type="Folder",
            id="myfolder",
            title="My Folder to store everything about Noam Chomsky",
        )
        api.content.transition(obj=self.portal.myfolder, transition="publish")
        api.content.create(
            container=self.portal.myfolder,
            type="Document",
            id="mydocument",
            title="Noam Chomsky's private document, in a folder",
        )
        api.content.create(
            container=self.portal.myfolder,
            type="News Item",
            id="mynews",
            title="My News Item with Noam Chomsky, in a folder",
        )
        api.content.transition(obj=self.portal.myfolder.mynews, transition="publish")
        # print('Test user roles:', self.portal.acl_users.getUser('test-user').getRoles()) # noqa
        transaction.commit()

    def test_solr_permissions_baseline(self):
        """baseline test, to check that permissions work as expected"""
        response = self.api_session.get(f"{self.portal_url}/@solr?q=chomsky")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)
        self.assertNotIn("/plone/chomskysdocument", path_strings)

    def test_solr_permissions_group_select_0(self):
        """group=All"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&group_select=0"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)
        self.assertNotIn("/plone/chomskysdocument", path_strings)

    def test_solr_permissions_group_select_5(self):
        """group=Image"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&group_select=5"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertNotIn("/plone/mynews", path_strings)
        self.assertNotIn("/plone/chomskysdocument", path_strings)

    def test_solr_permissions_group_select_3(self):
        """group=Image OR News Item"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&group_select=3"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)
        self.assertNotIn(
            "/plone/chomskysdocument", path_strings
        )  # both group and permission excludes it

    def test_solr_permissions_group_select_4(self):
        """group=Page OR News Item"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&group_select=4"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)  # because of the group
        self.assertIn("/plone/mynews", path_strings)
        self.assertNotIn("/plone/chomskysdocument", path_strings)

    def test_solr_permissions_group_local_including_parent(self):
        """search for all matching objects in a folder, including the parent"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)  # because of the prefix
        self.assertNotIn("/plone/mynews", path_strings)  # because of the prefix
        self.assertNotIn("/plone/chomskysdocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder/chomskysdocument", path_strings)

    def test_solr_permissions_group_local_excluding_parent(self):
        """search for all matching objects in a folder, excluding the parent"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/myfolder/"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/noamchomsky", path_strings)  # because of the prefix
        self.assertNotIn("/plone/mynews", path_strings)  # because of the prefix
        self.assertNotIn("/plone/chomskysdocument", path_strings)
        self.assertNotIn("/plone/myfolder", path_strings)  # because of the prefix
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder/chomskysdocument", path_strings)

    def test_solr_permissions_group_root(self):
        """search for all matching objects in the site, with a root prefix"""
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&path_prefix=/"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/noamchomsky", path_strings)
        self.assertIn("/plone/mynews", path_strings)
        self.assertNotIn("/plone/chomskysdocument", path_strings)
        self.assertIn("/plone/myfolder", path_strings)
        self.assertIn("/plone/myfolder/mynews", path_strings)
        self.assertNotIn("/plone/myfolder/chomskysdocument", path_strings)


class ServicesSolrPortalTypeTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # Person
        api.content.create(
            container=self.portal,
            type="News Item",
            id="news1",
            title="News Item 1",
        )
        api.content.create(
            container=self.portal,
            type="News Item",
            id="news2",
            title="News Item 2 red blue",
            location="",
        )
        api.content.create(
            container=self.portal,
            type="Document",
            id="redandblue",
            title="This is a title",
        )
        api.content.create(
            container=self.portal,
            type="News Item",
            id="newsblue",
            title="This is a blue news item",
        )
        transaction.commit()

    def test_no_portal_types(self):
        response = self.api_session.get(f"{self.portal_url}/@solr?q=red")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/news1", path_strings)
        self.assertIn("/plone/news2", path_strings)
        self.assertIn("/plone/redandblue", path_strings)
        self.assertNotIn("/plone/newsblue", path_strings)

    def test_portal_types_single(self):
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=red&portal_type:list=News Item"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/news1", path_strings)
        self.assertIn("/plone/news2", path_strings)
        self.assertNotIn("/plone/redandblue", path_strings)
        self.assertNotIn("/plone/newsblue", path_strings)

    def test_portal_types_multiple(self):
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=red&portal_type:list=News Item&"
            + "portal_type:list=Page"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/news1", path_strings)
        self.assertIn("/plone/news2", path_strings)
        self.assertIn("/plone/redandblue", path_strings)
        self.assertNotIn("/plone/newsblue", path_strings)

    def test_portal_types_multiple_with_space(self):
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=blue&portal_type:list=News Item&"
            + "portal_type:list=News%20Item"
        )
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/news1", path_strings)
        self.assertIn("/plone/news2", path_strings)
        self.assertNotIn("/plone/redandblue", path_strings)
        self.assertIn("/plone/newsblue", path_strings)


class ServicesSolrLanguageDependantTestCase(unittest.TestCase):

    layer = KITCONCEPT_SOLR_FUNCTIONAL_TESTING

    def makeTranslation(self, first, second):
        ILanguage(first).set_language("en")
        ILanguage(second).set_language("ca")
        ITranslationManager(first).register_translation("ca", second)

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        activateAndReindex(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.maintenance = self.portal.unrestrictedTraverse("solr-maintenance")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # Contents
        api.content.create(
            container=self.portal,
            type="Document",
            id="document1",
            title="Everything about  Prof. Dr. Noam Chomsky",
        )
        api.content.create(
            container=self.portal,
            type="Document",
            id="document1_ca",
            title="Everything about  Prof. Dr. Noam Chomsky, in Canadian",
        )
        self.makeTranslation(self.portal.document1, self.portal.document1_ca)
        api.content.create(
            container=self.portal,
            type="Image",
            id="image1",
            title="Image of Prof. Dr. Noam Chomsky",
        )
        api.content.create(
            container=self.portal,
            type="Image",
            id="image1_ca",
            title="Image of Prof. Dr. Noam Chomsky in Canadian",
        )
        self.makeTranslation(self.portal.image1, self.portal.image1_ca)
        transaction.commit()

    def test_basic(self):
        response = self.api_session.get(f"{self.portal_url}/@solr?q=chomsky&lang=en")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertIn("/plone/document1", path_strings)
        self.assertIn("/plone/image1", path_strings)
        self.assertNotIn("/plone/document1_ca", path_strings)
        self.assertNotIn("/plone/image1_ca", path_strings)
        response = self.api_session.get(f"{self.portal_url}/@solr?q=chomsky&lang=ca")
        self.assertIn("response", response.json())
        path_strings = get_path_strings(response)
        self.assertNotIn("/plone/document1", path_strings)
        self.assertNotIn("/plone/image1", path_strings)
        self.assertIn("/plone/document1_ca", path_strings)
        self.assertIn("/plone/image1_ca", path_strings)

    def test_lang_not_is_multilingual(self):
        response = self.api_session.get(
            f"{self.portal_url}/@solr?q=chomsky&lang=en&is_multilingual=true"
        )
        json = response.json()
        self.assertEqual(json["type"], "BadRequest")
        self.assertEqual(
            json["message"],
            "Property 'lang` and `is_multilingual` are mutually exclusive",
        )
