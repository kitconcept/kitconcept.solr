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


class TestUtilsFacetQuery(TestUtils):
    def test_facet_query(self):
        assert self.solr_config.facet_query == [
            "{!ex=typefilter}Type(*)",
            "{!ex=typefilter}Type:(Page)",
            '{!ex=typefilter}Type:("News Item")',
            '{!ex=typefilter}Type:(Page OR "News Item")',
        ]


class TestUtilsFieldList(TestUtils):
    def test_field_list(self):
        assert (
            self.solr_config.field_list
            == "UID,Title,Description,Type,effective,start,created,end,path_string,phone,email,location"
        )
