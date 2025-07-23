import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "News Item",
            "id": "news1",
            "title": "News Item 1",
            "language": "en",
            "location": "",
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "news2",
            "title": "News Item 2",
            "language": "en",
            "location": "",
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "news3",
            "title": "News Item 3",
            "language": "en",
            "location": "My location",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "redandblue",
            "title": "This is a title",
            "language": "en",
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "blue",
            "title": "Blue news item",
            "language": "en",
        },
    ]
