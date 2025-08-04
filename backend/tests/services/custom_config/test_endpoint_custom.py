import pytest


solr_config = {
    "fieldList": [
        "UID",
        "Title",
        "Description",
        "Type",
        "effective",
        "start",
        "created",
        "end",
        "path_string",
        "phone",
        "email",
        "location",
    ],
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
    ],
}


@pytest.fixture()
def registry_config() -> dict:
    """Override registry configuration."""
    return {
        "collective.solr.active": 1,
        "kitconcept.solr.config": solr_config,
    }


class TestEndpointCustom:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointCustomBaseSearch(TestEndpointCustom):
    url = "/@solr?q=chomsky"

    def test_facet_groups(self):
        # Using default configuration
        assert "response" in self.data
        assert self.data.get("facet_groups") == [
            ["All", 3],
            ["Pages", 1],
            ["News Items", 1],
            ["Pages and News Items", 2],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/mydocument", True),
            ("/plone/noamchomsky", True),
            ("/plone/mynews", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected

    def test_portal_path(self):
        """portal_path is returned for the client"""
        assert "response" in self.data
        assert self.data.get("portal_path") == "/plone"


class TestEndpointCustomGroupSelect1(TestEndpointCustom):
    # "filter": "Type(Page OR News Item)",
    url = "/@solr?q=chomsky&group_select=3"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/mydocument", True),
            ("/plone/noamchomsky", False),
            ("/plone/mynews", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
