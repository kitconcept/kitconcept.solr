import pytest


class TestEndpointEncoding:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointEncodingColon(TestEndpointEncoding):
    url = "/@solr?q=something: colon"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/withcolon", True),
            ("/plone/withspam", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointEncodingColonEncoded(TestEndpointEncoding):
    url = "/@solr?q=something%3a20colon"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/withcolon", True),
            ("/plone/withspam", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointEncodingSpan(TestEndpointEncoding):
    url = "/@solr?q=something:+-&|!()${'{}'}[]^+~*?/ spam"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/withcolon", True),
            ("/plone/withspam", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestEndpointEncodingSpanEncoded(TestEndpointEncoding):
    url = "/@solr?q=something%3A%2B-%26%7C!()%7B%7D%5B%5D%5E%2B~*%3F%2F spam"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", False),
            ("/plone/myfolder/mydocument", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/withcolon", True),
            ("/plone/withspam", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
