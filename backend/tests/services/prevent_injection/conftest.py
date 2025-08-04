import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "Document",
            "id": "document1",
            "title": "This is a blue document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "document2",
            "title": "This is a red document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "AnD_oR_nOt_WHATnot",
            "title": "This is a whatnot document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "oR",
            "title": "This is another document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "ANDoR",
            "title": "This is another document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "ANdOR",
            "title": "This is another document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "OReo",
            "title": "This is another document",
        },
    ]
