from kitconcept.solr.services.solr_utils import SolrConfig
from kitconcept.solr.services.solr_utils import SolrConfigError

import pytest


solr_config = {
    "fieldList": [
        "UID",
        "Title",
        "Description",
        "Type",
        # This field has a comma
        "effective,withcomma",
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


class TestUtilsFieldListWithComma:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content
        self.solr_config = SolrConfig()

    def test_field_list_with_comma(self):
        with pytest.raises(SolrConfigError) as exc_info:
            _ = self.solr_config.field_list
        assert exc_info.type is SolrConfigError
