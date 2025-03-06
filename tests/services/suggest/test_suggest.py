import pytest
import urllib.parse


class TestSuggestDefault:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


@pytest.fixture
def get_suggest_result_path():
    def func(a: dict) -> str:
        return urllib.parse.urlparse(a["@id"]).path

    return func


@pytest.fixture
def get_suggest_item():
    def func(data, index: int) -> dict:
        return data.get("suggestions")[index]

    return func


class TestSuggestDefaultBaseSearch(TestSuggestDefault):
    url = "/@solr-suggest?query=chomsky"
    expected = [
        "/plone/mydocument",
        "/plone/mynews",
    ]

    @pytest.mark.parametrize(
        "index,expected_path",
        enumerate(expected),
    )
    def test_suggest_result_path(
        self,
        get_suggest_item,
        get_suggest_result_path,
        index: int,
        expected_path: str,
    ):
        assert (
            get_suggest_result_path(get_suggest_item(self.data, index))
            == expected_path
        )
