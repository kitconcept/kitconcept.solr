from kitconcept.solr.testing import FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import INavigationSchema
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest


LANG = "en"


def create(container, portal_type, **kw):
    content = createContentInContainer(container, portal_type, **kw)
    content.language = LANG
    return content


class TestServicesNavigation(unittest.TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Re-enable Folder type (disabled by plone.volto profile)
        fti = self.portal.portal_types["Folder"]
        fti.global_allow = True

        # Ensure Folder is in displayed_types for navigation
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        displayed_types = settings.displayed_types
        if "Folder" not in displayed_types:
            settings.displayed_types = tuple(list(displayed_types) + ["Folder"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = create(self.portal, "Folder", id="folder", title="Some Folder")
        self.folder2 = create(
            self.portal, "Folder", id="folder2", title="Some Folder 2"
        )
        self.subfolder1 = create(
            self.folder, "Folder", id="subfolder1", title="SubFolder 1"
        )
        self.subfolder2 = create(
            self.folder, "Folder", id="subfolder2", title="SubFolder 2"
        )
        self.thirdlevelfolder = create(
            self.subfolder1,
            "Folder",
            id="thirdlevelfolder",
            title="Third Level Folder",
        )
        self.fourthlevelfolder = create(
            self.thirdlevelfolder,
            "Folder",
            id="fourthlevelfolder",
            title="Fourth Level Folder",
        )
        create(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_navigation_service(self):
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )

        assert response.status_code == 200
        assert len(response.json()["items"]) == 3
        assert response.json()["items"][1]["title"] == "Some Folder"
        assert len(response.json()["items"][1]["items"]) == 3
        assert len(response.json()["items"][2]["items"]) == 0

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 3}
        )

        assert len(response.json()["items"][1]["items"][0]["items"]) == 1
        assert (
            response.json()["items"][1]["items"][0]["items"][0]["title"]
            == "Third Level Folder"
        )
        assert len(response.json()["items"][1]["items"][0]["items"][0]["items"]) == 0

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 4}
        )

        assert len(response.json()["items"][1]["items"][0]["items"][0]["items"]) == 1
        assert (
            response.json()["items"][1]["items"][0]["items"][0]["items"][0]["title"]
            == "Fourth Level Folder"
        )

    def test_dont_broke_with_contents_without_review_state(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        displayed_types = settings.displayed_types
        settings.displayed_types = tuple(list(displayed_types) + ["File"])
        create(
            self.portal,
            "File",
            id="example-file",
            title="Example file",
        )
        create(
            self.folder,
            "File",
            id="example-file-1",
            title="Example file 1",
        )
        transaction.commit()

        response = self.api_session.get("/folder/@navigation")
        assert response.json()["items"][3]["review_state"] is None

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )
        assert response.json()["items"][1]["items"][3]["review_state"] is None

    def test_show_excluded_items(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")

        # Plone 5.2 and Plone 6.0 have different default values:
        # False for Plone 6.0 and True for Plone 5.2
        # explicitly set the value to False to avoid test failures
        settings.show_excluded_items = False
        create(
            self.folder,
            "Folder",
            id="excluded-subfolder",
            title="Excluded SubFolder",
            exclude_from_nav=True,
        )
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )
        assert "Excluded SubFolder" not in [
            item["title"] for item in response.json()["items"][1]["items"]
        ]

        # change setting to show excluded items
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        settings.show_excluded_items = True
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )
        assert "Excluded SubFolder" in [
            item["title"] for item in response.json()["items"][1]["items"]
        ]

    def test_navigation_sorting(self):
        registry = getUtility(IRegistry)
        registry["plone.displayed_types"] = (
            "Link",
            "News Item",
            "Folder",
            "Document",
            "Event",
            "Collection",
            "File",
        )
        create(
            self.portal,
            "File",
            id="example-file",
            title="Example file",
        )
        create(
            self.folder,
            "File",
            id="example-file-1",
            title="Example file 1",
        )
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        ).json()

        contents = response["items"][1]["items"]
        assert [p["@id"].replace(self.portal.absolute_url(), "") for p in contents] == [
            "/folder/subfolder1",
            "/folder/subfolder2",
            "/folder/doc1",
            "/folder/example-file-1",
        ]

        self.portal["folder"].moveObjectsUp(["example-file-1"])
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        ).json()
        contents = response["items"][1]["items"]
        assert [p["@id"].replace(self.portal.absolute_url(), "") for p in contents] == [
            "/folder/subfolder1",
            "/folder/subfolder2",
            "/folder/example-file-1",
            "/folder/doc1",
        ]

    def test_use_nav_title_when_available_and_set(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        displayed_types = settings.displayed_types
        settings.displayed_types = tuple(list(displayed_types) + ["DXTestDocument"])

        title = "Example Document"
        nav_title = "Fancy title"

        create(
            self.folder,
            "DXTestDocument",
            id="example-dx-document",
            title=title,
            nav_title=nav_title,
        )
        transaction.commit()

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )

        assert response.json()["items"][1]["items"][-1]["title"] == nav_title

    def test_navigation_badrequests(self):
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": "php"}
        )

        assert response.status_code == 400
        assert "Invalid expand.navigation.depth" in response.json()["message"]
