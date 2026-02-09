import pytest


@pytest.fixture
def contents() -> list:
    """Content to be created."""
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "noamchomsky",
            "title": "Prof. Dr. Noam Chomsky",
            "description": "The real Chomsky is here.",
            "subjects": ["mymembersubject", "mymembersubjecttwo"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
            # Highlighting by default is based on `body_text` which is produced
            # from the block content.
            "blocks_layout": {
                "items": [
                    "262c25c6-b5e1-4193-9931-a8a060e2ad93",
                ]
            },
            "blocks": {
                "262c25c6-b5e1-4193-9931-a8a060e2ad93": {
                    "@type": "description",
                    "text": "This is a description about Chomsky",
                }
            },
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
            # Highlighting by default is based on `body_text` which is produced
            # from the block content.
            "blocks_layout": {
                "items": [
                    "262c25c6-b5e1-4193-9931-a8a060e2ad93",
                ]
            },
            "blocks": {
                "262c25c6-b5e1-4193-9931-a8a060e2ad93": {
                    "@type": "description",
                    "text": "Some more news about Chomsky",
                }
            },
        },
        {
            "_container": "",
            "type": "Document",
            "id": "myotherfolder",
            "title": "My other Folder",
            # Highlighting by default is based on `body_text` which is produced
            # from the block content.
            "blocks_layout": {
                "items": [
                    "262c25c6-b5e1-4193-9931-a8a060e2ad93",
                ]
            },
            "blocks": {
                "262c25c6-b5e1-4193-9931-a8a060e2ad93": {
                    "@type": "description",
                    "text": "Container for material about Chomsky",
                }
            },
        },
    ]
