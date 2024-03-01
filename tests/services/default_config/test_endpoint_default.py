import pytest


class TestEndpointDefault:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointDefaultBaseSearch(TestEndpointDefault):
    url = "/@solr?q=chomsky"

    def test_facet_groups(self):
        # Using default configuration
        assert "response" in self.data
        assert self.data.get("facet_groups") == [
            ["All", 3],
            ["Pages", 1],
            ["Events", 0],
            ["Images", 1],
            ["Files", 0],
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


class TestEndpointDefaultGroupSelectAll(TestEndpointDefault):
    # "filter": "Type(*)",
    url = "/@solr?q=chomsky&group_select=0"

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


class TestEndpointDefaultGroupSelect1(TestEndpointDefault):
    url = "/@solr?q=chomsky&group_select=1"

    def test_facet_groups(self):
        # Using default configuration
        assert "response" in self.data
        assert self.data.get("facet_groups") == [
            ["All", 3],
            ["Pages", 1],
            ["Events", 0],
            ["Images", 1],
            ["Files", 0],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/mydocument", True),
            ("/plone/noamchomsky", False),
            ("/plone/mynews", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointDefaultGroupSelect3(TestEndpointDefault):
    # "filter": "Type:(Image)",
    url = "/@solr?q=chomsky&group_select=3"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/mydocument", False),
            ("/plone/noamchomsky", True),
            ("/plone/mynews", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointDefaultContext(TestEndpointDefault):
    url = "/myotherfolder/@solr?q=chomsky"

    def test_portal_path(self):
        assert "response" in self.data
        assert self.data.get("portal_path") == "/plone"


class TestEndpointDefaultEmptyQSearch(TestEndpointDefault):
    url = "/@solr?q="

    def test_facet_groups(self):
        # Using default configuration
        assert "response" in self.data
        assert self.data.get("facet_groups") == [
            ["All", 5],
            ["Pages", 2],
            ["Events", 0],
            ["Images", 1],
            ["Files", 0],
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


class TestEndpointDefaultMissingQSearch(TestEndpointDefault):
    url = "/@solr"

    def test_facet_groups(self):
        # Using default configuration
        assert "response" in self.data
        assert self.data.get("facet_groups") == [
            ["All", 5],
            ["Pages", 2],
            ["Events", 0],
            ["Images", 1],
            ["Files", 0],
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
