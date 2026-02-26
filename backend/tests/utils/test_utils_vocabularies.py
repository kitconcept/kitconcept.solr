from kitconcept.solr.services.solr_utils import SolrConfig

import pytest


solr_config_no_vocabs = {
    "fieldList": [
        "UID",
        "Title",
        "Description",
    ],
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
    ],
}

solr_config_with_vocabs = {
    "fieldList": [
        "UID",
        {
            "name": "Title",
            "vocabulary": {
                "name": "kitconcept.solr.vocabularies.test",
                "isMultilingual": False,
            },
        },
        "Description",
        {
            "name": "Type",
            "vocabulary": {
                "name": "kitconcept.solr.vocabularies.types",
            },
        },
    ],
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
    ],
}

solr_config_dict_without_vocab = {
    "fieldList": [
        "UID",
        {
            "name": "Title",
        },
        "Description",
    ],
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
    ],
}


class TestUtils:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content
        self.solr_config = SolrConfig()


class TestVocabulariesEmpty(TestUtils):
    @pytest.fixture()
    def registry_config(self) -> dict:
        return {
            "kitconcept.solr.config": solr_config_no_vocabs,
        }

    def test_vocabularies_empty(self):
        assert self.solr_config.vocabularies == []


class TestVocabulariesWithVocabs(TestUtils):
    @pytest.fixture()
    def registry_config(self) -> dict:
        return {
            "kitconcept.solr.config": solr_config_with_vocabs,
        }

    def test_vocabularies(self):
        assert self.solr_config.vocabularies == [
            {
                "field": "Title",
                "name": "kitconcept.solr.vocabularies.test",
                "isMultilingual": False,
            },
            {
                "field": "Type",
                "name": "kitconcept.solr.vocabularies.types",
            },
        ]


class TestVocabulariesDictWithoutVocab(TestUtils):
    @pytest.fixture()
    def registry_config(self) -> dict:
        return {
            "kitconcept.solr.config": solr_config_dict_without_vocab,
        }

    def test_vocabularies_empty_when_dict_has_no_vocab(self):
        assert self.solr_config.vocabularies == []
