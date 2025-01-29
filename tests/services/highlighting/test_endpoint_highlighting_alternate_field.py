from test_endpoint_highlighting import TestEndpointDefault

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
    "highlightingFields": [{"field": "content", "prop": "alternate"}],
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


class TestHighlightingAlternateField(TestEndpointDefault):
    @pytest.mark.parametrize(
        "path,highlight_field,highlight",
        [
            (
                "/plone/mydocument",
                "alternate",
                ["This is a description about <em>Chomsky</em>"],
            ),
            (
                "/plone/noamchomsky",
                "alternate",
                None,
            ),
            (
                "/plone/mynews",
                "alternate",
                ["Some more news about <em>Chomsky</em>"],
            ),
            (
                "/plone/myotherfolder",
                "alternate",
                ["Container for material about <em>Chomsky</em>"],
            ),
        ],
    )
    def test_highlight_field(
        self, path: str, highlight_field: str, highlight: str
    ):
        filtered = [
            item.get(highlight_field, None)
            for item in self.data["response"]["docs"]
            if item["path_string"] == path
        ]
        assert (filtered[0] if len(filtered) > 0 else None) == highlight
