from typing import ClassVar

import base64
import json
import pytest
import urllib.parse


def encode_conditions(rows: list) -> str:
    """Encode extra_conditions rows the way the frontend does."""
    return urllib.parse.quote(base64.b64encode(json.dumps(rows).encode()).decode())


class TestSuggestDefault:
    @pytest.fixture(autouse=True, scope="class")
    def _init(self, request, portal_with_content, manager_request):
        request.cls.portal = portal_with_content
        response = manager_request.get(request.cls.url)
        request.cls.data = response.json()


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
    expected_result: ClassVar[list] = [
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
        assert (
            get_suggest_result_props(expected_dict).items()
            <= get_suggest_result_props(get_suggest_item(self.data, index)).items()
        )


class TestSuggestPathPrefix(TestSuggestDefault):
    """path_prefix restricts suggestions to a subtree (e.g. a workspace)."""

    url = "/@solr-suggest?query=chomsky&path_prefix=/mydocument"

    def test_only_prefixed_results(self, get_suggest_result_path):
        paths = [get_suggest_result_path(item) for item in self.data["suggestions"]]
        assert paths == ["/plone/mydocument"]


class TestSuggestExtraConditionsType(TestSuggestDefault):
    """A type filter restricts suggestions - including a type with a
    space in its name (which needs the quoted string condition)."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["portal_type", "string", {"in": ["News Item"]}]
    ])

    def test_only_filtered_type(self, get_suggest_result_path):
        paths = [get_suggest_result_path(item) for item in self.data["suggestions"]]
        assert paths == ["/plone/mynews"]


class TestSuggestExtraConditionsTypeOverridesExclusion(TestSuggestDefault):
    """An explicit type filter wins over the built-in type exclusion
    list: Image is normally excluded from suggestions, but a user who
    filters for images must see them."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["portal_type", "string", {"in": ["Image"]}]
    ])

    def test_excluded_type_returned_when_filtered(self, get_suggest_result_path):
        paths = [get_suggest_result_path(item) for item in self.data["suggestions"]]
        assert paths == ["/plone/noamchomsky"]


class TestSuggestExtraConditionsCreator(TestSuggestDefault):
    """A Creator filter with a non-existent user matches nothing."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["Creator", "string", {"in": ["nonexistent-user"]}]
    ])

    def test_no_results(self):
        assert self.data["suggestions"] == []


class TestSuggestExtraConditionsDateRange(TestSuggestDefault):
    """A date-range condition on modified filters by recency: the test
    content was just created, so a lower bound in the recent past keeps
    all default suggestions."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["modified", "date-range", {"ge": "NOW-1DAY"}]
    ])

    def test_recent_content_kept(self, get_suggest_result_path):
        paths = [get_suggest_result_path(item) for item in self.data["suggestions"]]
        assert paths == ["/plone/mydocument", "/plone/mynews"]


class TestSuggestExtraConditionsDateRangePast(TestSuggestDefault):
    """An upper bound in the past matches nothing."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["modified", "date-range", {"le": "2000-01-01T00:00:00Z"}]
    ])

    def test_no_results(self):
        assert self.data["suggestions"] == []


class TestSuggestExtraConditionsReviewState(TestSuggestDefault):
    """A review_state filter: the test content is private, so filtering
    for published matches nothing and private keeps the defaults."""

    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["review_state", "string", {"in": ["published"]}]
    ])

    def test_no_results(self):
        assert self.data["suggestions"] == []


class TestSuggestExtraConditionsReviewStatePrivate(TestSuggestDefault):
    url = "/@solr-suggest?query=chomsky&extra_conditions=" + encode_conditions([
        ["review_state", "string", {"in": ["private"]}]
    ])

    def test_private_content_kept(self, get_suggest_result_path):
        paths = [get_suggest_result_path(item) for item in self.data["suggestions"]]
        assert paths == ["/plone/mydocument", "/plone/mynews"]
