# fmt: off
from kitconcept.solr.services.solr_highlighting_utils import SolrHighlightingUtils

import pytest


class MockSolrConfig:
    def __init__(self, config):
        self.config = config


class TestSolrHighlightingUtils:
    @pytest.fixture
    def solr_config(self):
        return {
            "highlightingFields": [
                {"field": "title", "prop": "highlight_title"},
                {"field": "description", "prop": "highlight_description"},
            ]
        }

    @pytest.fixture
    def items(self):
        return [
            {
                "UID": "UID1",
                "field_a": "value_a1",
                "field_b": "value_b1",
            },
            {
                "UID": "UID2",
                "field_a": "value_a2",
                "field_b": "value_b2",
            },
        ]

    def test_init(self, solr_config):
        utils = SolrHighlightingUtils(MockSolrConfig(solr_config))
        assert utils.fields == ["title", "description"]
        assert utils.enabled
        assert utils.propByField == {
            "title": "highlight_title",
            "description": "highlight_description",
        }

    def test_enhance_items(self, solr_config, items):
        utils = SolrHighlightingUtils(MockSolrConfig(solr_config))
        highlighting = {
            "UID1": {
                "title": ["highlighted_title1"],
                "description": ["highlighted_description1"],
            },
            "UID2": {
                "title": ["highlighted_title2"],
                "description": ["highlighted_description2"],
            },
        }
        utils.enhance_items(items, highlighting)
        assert items == [
            {
                "UID": "UID1",
                "field_a": "value_a1",
                "field_b": "value_b1",
                "highlight_title": ["highlighted_title1"],
                "highlight_description": ["highlighted_description1"],
            },
            {
                "UID": "UID2",
                "field_a": "value_a2",
                "field_b": "value_b2",
                "highlight_title": ["highlighted_title2"],
                "highlight_description": ["highlighted_description2"],
            },
        ]


class TestSolrHighlightingUtilsEmpty:
    @pytest.fixture
    def solr_config(self):
        return {}

    def test_empty(self, solr_config):
        utils = SolrHighlightingUtils(MockSolrConfig(solr_config))
        assert utils.fields == []
        assert not utils.enabled
        assert utils.propByField == {}

    def test_enhance_items_empty(self, solr_config):
        utils = SolrHighlightingUtils(MockSolrConfig(solr_config))
        items = [
            {
                "UID": "UID1",
                "field_a": "value_a1",
                "field_b": "value_b1",
            },
            {
                "UID": "UID2",
                "field_a": "value_a2",
                "field_b": "value_b2",
            },
        ]
        highlighting = {}
        utils.enhance_items(items, highlighting)
        assert items == [
            {
                "UID": "UID1",
                "field_a": "value_a1",
                "field_b": "value_b1",
            },
            {
                "UID": "UID2",
                "field_a": "value_a2",
                "field_b": "value_b2",
            },
        ]
