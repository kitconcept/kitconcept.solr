import pytest


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
    ],
}

solr_config_no_vocabs = {
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
    ],
}


class TestVocabulariesEndpoint:
    @pytest.fixture(autouse=True, scope="class")
    def _init(self, request, portal_with_content, manager_request):
        request.cls.portal = portal_with_content
        response = manager_request.get(request.cls.url)
        request.cls.data = response.json()


class TestVocabulariesInResponse(TestVocabulariesEndpoint):
    url = "/@solr?q=chomsky"

    @pytest.fixture(scope="class")
    def registry_config(self) -> dict:
        return {
            "collective.solr.active": 1,
            "kitconcept.solr.config": solr_config_with_vocabs,
        }

    def test_vocabularies(self):
        assert self.data.get("vocabularies") == [
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


class TestVocabulariesEmptyInResponse(TestVocabulariesEndpoint):
    url = "/@solr?q=chomsky"

    @pytest.fixture(scope="class")
    def registry_config(self) -> dict:
        return {
            "collective.solr.active": 1,
            "kitconcept.solr.config": solr_config_no_vocabs,
        }

    def test_vocabularies_empty(self):
        assert self.data.get("vocabularies") == []
