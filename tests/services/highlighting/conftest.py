from typing import List

import pytest


@pytest.fixture
def contents() -> List:
    """Content to be created."""
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "noamchomsky",
            "title": "Prof. Dr. Noam Chomsky",
            "description": "The real Chomsky is here.",
            "subjects": ["mymembersubject", "mymembersubjecttwo"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",  # noQA
        },
        {
            "_container": "",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
            "description": "This is a description about Chomsky",
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "myotherfolder",
            "title": "My other Folder",
        },
    ]
