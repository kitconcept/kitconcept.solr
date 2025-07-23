import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "myimage",
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
            "_container": "myfolder",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "foo_alpha",
            "title": "Chomsky foo",
            "description": "Chomsky alpha",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "foo_beta",
            "title": "Chomsky foo",
            "description": "Chomsky beta",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "foo_gamma",
            "title": "Chomsky foo",
            "description": "Chomsky gamma",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "bar_alpha",
            "title": "Chomsky bar",
            "description": "Chomsky alpha",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "bar_beta",
            "title": "Chomsky bar",
            "description": "Chomsky beta",
            "language": "en",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "bar_gamma",
            "title": "Chomsky bar",
            "description": "Chomsky gamma",
            "language": "en",
        },
    ]
