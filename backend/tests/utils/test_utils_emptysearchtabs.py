from kitconcept.solr.services.solr_utils import SolrConfig
from kitconcept.solr.services.solr_utils import SolrConfigError

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
    "searchTabs": [],
}


@pytest.fixture()
def registry_config() -> dict:
    """Override registry configuration."""
    return {
        "kitconcept.solr.config": solr_config,
    }


class TestUtilsEmptySearchTabs:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content
        self.solr_config = SolrConfig()

    def test_empty_search_tabs(self):
        with pytest.raises(SolrConfigError) as exc_info:
            _ = self.solr_config.labels
        assert exc_info.type is SolrConfigError
