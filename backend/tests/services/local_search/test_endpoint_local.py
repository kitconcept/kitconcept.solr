import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "noamchomsky",
            "title": "Prof. Dr. Noam Chomsky",
            "subjects": ["mymembersubject", "mymembersubjecttwo"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",
        },
        {
            "_container": "",
            "type": "Folder",
            "id": "myfolder",
            "title": "My Folder to store everything about Noam Chomsky",
        },
        {
            "_container": "",
            "type": "Folder",
            "id": "myotherfolder",
            "title": "My other Folder",
        },
        {
            "_container": "myfolder",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
        },
        {
            "_container": "myfolder",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
        },
    ]


class TestEndpointLocalSearch:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointLocalSearchGlobal(TestEndpointLocalSearch):
    """Search without a prefix."""

    url = "/@solr?q=chomsky"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", True),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointLocalSearchPrefix(TestEndpointLocalSearch):
    """Search all matching objects in a folder, including the parent."""

    url = "/@solr?q=chomsky&path_prefix=/myfolder"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointLocalSearchContext(TestEndpointLocalSearch):
    """Search all matching objects in a folder, including the parent."""

    url = "/myfolder/@solr?q=chomsky"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointLocalSearchContextWithPrefix(TestEndpointLocalSearch):
    """Search all matching objects in a folder, including the parent.
    Called on object context with path_prefix which overrides the context.
    """

    url = "/myotherfolder/@solr?q=chomsky&path_prefix=/myfolder"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected

    def test_portal_path(self):
        """portal_path depends on the portal path, independent from context"""
        assert "response" in self.data
        assert self.data.get("portal_path") == "/plone"


class TestEndpointLocalSearchPrefixExcludeParent(TestEndpointLocalSearch):
    """Search all matching objects in a folder, excluding the parent."""

    url = "/@solr?q=chomsky&path_prefix=/myfolder/"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointLocalSearchSiteRoot(TestEndpointLocalSearch):
    """Search all matching objects in the site."""

    url = "/@solr?q=chomsky&path_prefix=/"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", True),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
