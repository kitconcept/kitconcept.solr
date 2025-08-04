import base64
import json
import pytest


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


class TestFacetConditionsInactive(TestEndpointCustom):
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


class TestFacetConditionsActive(TestEndpointCustom):
    url = "/@solr?q=chomsky&group_select=1"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 6], ["bar", 3], ["foo", 3]],
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
            ("/plone/myfolder", False),
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


class TestFacetConditionsFiltering1(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with beginning search."""
        return {"Title": {"c": {"foo": True}}}

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 6], ["bar", 3], ["foo", 3]],
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
            ("/plone/myfolder", False),
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


class TestFacetConditionsFiltering2(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with beginning search."""
        return {"Title": {"c": {"foo": True}}, "Description": {"c": {"alpha": True}}}

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 6], ["bar", 3], ["foo", 3]],
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
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", False),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestFacetConditionsFiltering3(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with beginning search."""
        return {
            "Title": {"c": {"foo": True}},
            "Description": {"c": {"alpha": True, "beta": True}},
        }

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 6], ["bar", 3], ["foo", 3]],
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
            ("/plone/myfolder", False),
            ("/plone/myfolder/mynews", False),
            ("/plone/foo_alpha", True),
            ("/plone/foo_beta", True),
            ("/plone/foo_gamma", False),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestFacetConditionsFilteringFalseIgnored(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with beginning search."""
        return {
            "Title": {"c": {"foo": True, "bar": False}},
            "Description": {"c": {"alpha": False}},
        }

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["chomsky", 6], ["bar", 3], ["foo", 3]],
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
            ("/plone/myfolder", False),
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


class TestFacetConditionsContainsBeginning(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with beginning search."""
        return {"Title": {"c": {"foo": True}, "p": "ba"}, "Description": {"p": "cho"}}

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["bar", 3]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 6]],
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
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestFacetConditionsContainsMiddle(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with middle search."""
        return {"Title": {"c": {"foo": True}, "p": "ar"}, "Description": {"p": "cho"}}

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["bar", 3]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 6]],
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
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestFacetConditionsContainsCaseInsensitive(TestEndpointCustom):
    @property
    def c(self):
        """Conditions with case-insensitive search."""
        return {
            "Title": {"c": {"foo": True}, "p": "BAR"},
            "Description": {"p": "cho"},
        }

    @property
    def url(self):
        """URL to test the facets."""
        return f"/@solr?q=chomsky&group_select=1&facet_conditions={encoded(self.c)}"

    def test_facet_fields(self):
        assert self.data.get("facet_fields") == [
            [
                {"name": "Title", "label": "The title"},
                [["bar", 3]],
            ],
            [
                {"name": "Description", "label": "The description"},
                [["chomsky", 6]],
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
            ("/plone/foo_gamma", True),
            ("/plone/bar_alpha", False),
            ("/plone/bar_beta", False),
            ("/plone/bar_gamma", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
