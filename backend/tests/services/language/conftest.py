import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "noamchomsky",
            "title": "Prof. Dr. Noam Chomsky",
            "subjects": ["mymembersubject", "mymembersubjecttwo"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Folder",
            "id": "myfolder",
            "title": "My Folder to store everything about Noam Chomsky",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Folder",
            "id": "myotherfolder",
            "title": "My other Folder",
            "language": "en",
        },
        {
            "_container": "myfolder",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
            "language": "en",
        },
        {
            "_container": "myfolder",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Folder",
            "id": "myfolder_de",
            "title": "My Folder to store everything about Noam Chomsky in Deutsch",
            "language": "de",
            "_translation_of": "myfolder",
        },
        {
            "_container": "myfolder_de",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
            "language": "de",
            "_translation_of": "myfolder/mydocument",
        },
    ]
