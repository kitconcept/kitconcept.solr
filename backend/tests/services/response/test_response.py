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
        "collective.solr.active": 1,
        "kitconcept.solr.config": solr_config,
    }


class TestResponseCustom:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestResponseKeepFullSolrResponseDefault(TestResponseCustom):
    url = "/@solr?q=chomsky"

    def test_facet_counts(self):
        assert "response" in self.data
        assert "facet_counts" not in self.data


class TestResponseKeepFullSolrResponseIsFalse(TestResponseCustom):
    url = "/@solr?q=chomsky&keep_full_solr_response=false"

    def test_facet_counts(self):
        assert "response" in self.data
        assert "facet_counts" not in self.data


class TestResponseKeepFullSolrResponseDefaultIsTrue(TestResponseCustom):
    url = "/@solr?q=chomsky&keep_full_solr_response=true"

    def test_facet_counts(self):
        assert "response" in self.data
        assert "facet_counts" in self.data
