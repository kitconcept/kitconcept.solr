import pytest


class TestEndpointPortalType:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointPortalTypeNotPassed(TestEndpointPortalType):
    url = "/@solr?q=news"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", False),
            ("/plone/news1", True),
            ("/plone/news2", True),
            ("/plone/news3", True),
            ("/plone/blue", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointPortalTypeSingle(TestEndpointPortalType):
    url = "/@solr?q=blue&portal_type:list=News Item"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", False),
            ("/plone/news1", False),
            ("/plone/news2", False),
            ("/plone/news3", False),
            ("/plone/blue", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointPortalTypeMultiple(TestEndpointPortalType):
    url = "/@solr?q=blue&portal_type:list=News Item&portal_type:list=Page"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", True),
            ("/plone/news1", False),
            ("/plone/news2", False),
            ("/plone/news3", False),
            ("/plone/blue", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointPortalTypeMultipleWithSpace(TestEndpointPortalType):
    url = "/@solr?q=blue&portal_type:list=News Item&portal_type:list=News%20Item"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", False),
            ("/plone/news1", False),
            ("/plone/news2", False),
            ("/plone/news3", False),
            ("/plone/blue", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
