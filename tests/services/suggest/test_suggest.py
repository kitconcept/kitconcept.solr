import pytest
import urllib.parse


class TestSuggestDefault:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


@pytest.fixture
def get_suggest_result_props():
    def func(
        a: dict,
    ) -> bool:
        ac = dict(a)
        del ac["@id"]
        return ac

    return func


@pytest.fixture
def get_suggest_result_path():
    def func(a: dict) -> bool:
        return urllib.parse.urlparse(a["@id"]).path

    return func


@pytest.fixture
def get_suggest_item():
    def func(data, index: int) -> dict:
        return data.get("suggestions")[index]

    return func


class TestSuggestDefaultBaseSearch(TestSuggestDefault):
    url = "/@solr-suggest?query=chomsky"
    expected_result = [
        {
            "@id": "http://localhost:59793/plone/mydocument",
            "@type": "Document",
            "description": "",
            "review_state": "private",
            "title": "My Document about Noam Chomsky",
            "type_title": "Page",
        },
        {
            "@id": "http://localhost:59793/plone/mynews",
            "@type": "News Item",
            "description": "",
            "review_state": "private",
            "title": "My News Item with Noam Chomsky",
            "type_title": "News Item",
        },
    ]

    @pytest.mark.parametrize(
        "index,expected_dict",
        enumerate(expected_result),
    )
    def test_suggest_result_path(
        self,
        get_suggest_item,
        get_suggest_result_path,
        index: int,
        expected_dict: dict,
    ):
        assert get_suggest_result_path(
            get_suggest_item(self.data, index)
        ) == get_suggest_result_path(expected_dict)

    @pytest.mark.parametrize(
        "index,expected_dict",
        enumerate(expected_result),
    )
    def test_suggest_result_props(
        self,
        get_suggest_item,
        get_suggest_result_props,
        index: int,
        expected_dict: dict,
    ):
        assert get_suggest_result_props(
            get_suggest_item(self.data, index)
        ) == get_suggest_result_props(expected_dict)
