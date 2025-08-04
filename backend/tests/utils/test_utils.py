from kitconcept.solr.services.solr_utils import SolrConfig

import pytest


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
        },
        {
            "label": "News Items",
            "filter": 'Type:("News Item")',
            "layouts": ["list", "grid"],
            "facetFields": ["contact_phone", "contact_email"],
        },
        {
            "label": "Pages and News Items",
            "filter": 'Type:(Page OR "News Item")',
            "layouts": ["grid"],
            "facetFields": ["contact_email"],
        },
    ],
}


@pytest.fixture()
def registry_config() -> dict:
    """Override registry configuration."""
    return {
        "kitconcept.solr.config": solr_config,
    }


class TestUtils:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content
        self.solr_config = SolrConfig()


class TestUtilsLabels(TestUtils):
    def test_labels(self):
        assert self.solr_config.labels == [
            "All",
            "Pages",
            "News Items",
            "Pages and News Items",
        ]


class TestUtilsSelectCondition(TestUtils):
    def test_select_condition(self):
        assert self.solr_config.select_condition(0) == "{!tag=typefilter}Type(*)"
        assert self.solr_config.select_condition(1) == "{!tag=typefilter}Type:(Page)"
        assert (
            self.solr_config.select_condition(2)
            == '{!tag=typefilter}Type:("News Item")'
        )
        assert (
            self.solr_config.select_condition(3)
            == '{!tag=typefilter}Type:(Page OR "News Item")'
        )


class TestUtilsFieldList(TestUtils):
    def test_field_list(self):
        assert (
            self.solr_config.field_list
            == "UID,Title,Description,Type,effective,start,created,end,path_string,phone,email,location"
        )


class TestUtilsSelectLayouts(TestUtils):
    def test_select_layouts(self):
        assert self.solr_config.select_layouts(0) is None
        assert self.solr_config.select_layouts(1) is None
        assert self.solr_config.select_layouts(2) == ["list", "grid"]
        assert self.solr_config.select_layouts(3) == ["grid"]


class TestUtilsSelectFacetFields(TestUtils):
    def test_select_facet_fields(self):
        assert self.solr_config.select_facet_fields(0) == []
        assert self.solr_config.select_facet_fields(1) == []
        assert self.solr_config.select_facet_fields(2) == [
            "contact_phone",
            "contact_email",
        ]
        assert self.solr_config.select_facet_fields(3) == ["contact_email"]
