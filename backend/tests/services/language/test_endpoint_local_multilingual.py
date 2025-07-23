import pytest


class TestEndpointMultilingual:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointMultilingualGlobal(TestEndpointMultilingual):
    """Search without a prefix."""

    url = "/@solr?q=chomsky"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", True),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
            ("/plone/myfolder_de", True),
            ("/plone/myfolder_de/mydocument", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointMultilingualDisabled(TestEndpointMultilingual):
    """Search with multilingual results disabled."""

    url = "/@solr?q=chomsky&path_prefix=/myfolder&is_multilingual=false"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/myfolder", True),
            ("/plone/myfolder_de", False),
            ("/plone/myfolder_de/mydocument", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointMultilingualDisabledLocal(TestEndpointMultilingual):
    """Search with multilingual results disabled."""

    url = "/@solr?q=chomsky&path_prefix=/myfolder_de&is_multilingual=false"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/myfolder", False),
            ("/plone/myfolder_de", True),
            ("/plone/myfolder_de/mydocument", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
