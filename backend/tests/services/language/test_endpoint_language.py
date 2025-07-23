import pytest


class TestEndpointLanguage:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointLanguageEN(TestEndpointLanguage):
    url = "/@solr?q=chomsky&lang=en"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/noamchomsky", True),
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


class TestEndpointLanguageDE(TestEndpointLanguage):
    url = "/@solr?q=chomsky&lang=de"

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


class TestEndpointLanguageError(TestEndpointLanguage):
    url = "/@solr?q=chomsky&lang=en&is_multilingual=true"

    @pytest.mark.parametrize(
        "key,message",
        [
            ("type", "BadRequest"),
            (
                "message",
                "Property 'lang` and `is_multilingual` are mutually exclusive",
            ),
        ],
    )
    def test_error_message(self, key: str, message: str):
        assert self.data[key] == message
