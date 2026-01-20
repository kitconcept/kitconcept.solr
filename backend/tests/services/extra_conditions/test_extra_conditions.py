import base64
import json
import pytest
from typing import ClassVar


def encoded(o):
    return base64.b64encode(json.dumps(o).encode("utf-8")).decode("ascii")


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
            "facetFields": [
                {
                    "name": "Title",
                    "label": "The title",
                },
                {"name": "Description", "label": "The description"},
            ],
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


class TestExtraConditionsInactive(TestEndpointCustom):
    url = "/@solr?q=chomsky"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", True),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", True),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsActive(TestEndpointCustom):
    url = "/@solr?q=chomsky&group_select=1"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 7], ["bar", 3], ["foo", 3]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 6], ["alpha", 2], ["beta", 2], ["gamma", 2]],
            ],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsDateGe(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "start",
            "date-range",
            {"ge": "2021-02-01T00:00:00Z"},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 4], ["bar", 2], ["foo", 2]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 4], ["beta", 2], ["gamma", 2]],
            ],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", False),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsDateLe(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "start",
            "date-range",
            {"le": "2021-02-01T00:00:00Z"},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 4], ["bar", 2], ["foo", 2]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 4], ["alpha", 2], ["beta", 2]],
            ],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsDateGeLe(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "start",
            "date-range",
            {"le": "2021-02-01T00:00:00Z", "ge": "2021-02-01T00:00:00Z"},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 2], ["bar", 1], ["foo", 1]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["beta", 2], ["chomsky", 2]],
            ],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", False),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsDateGrLs(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "start",
            "date-range",
            {"ls": "2021-03-01T00:00:00Z", "gr": "2021-01-01T00:00:00Z"},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 2], ["bar", 1], ["foo", 1]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["beta", 2], ["chomsky", 2]],
            ],
        ]

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", False),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsStringInSingleTerm(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "searchwords",
            "string",
            {"in": ["term1"]},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsStringInSingleTerm2(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "searchwords",
            "string",
            {"in": ["term2"]},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", False),
            ("/plone/foo_beta", False),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsStringInMultipleTerms(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "searchwords",
            "string",
            {"in": ["term1", "term2"]},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestExtraConditionsStringInNoTerms(TestEndpointCustom):
    extra_conditions: ClassVar[list] = [
        [
            "searchwords",
            "string",
            {"in": []},
        ],
    ]
    url = (
        f"/@solr?q=chomsky&group_select=1&extra_conditions={encoded(extra_conditions)}"
    )

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/myimage", False),
            ("/plone/myfolder", True),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", True),
            ("/plone/bar_beta", True),
            ("/plone/bar_gamma", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
