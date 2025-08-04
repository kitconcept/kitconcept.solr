from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

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
        },
        {
            "_container": "",
            "type": "Document",
            "id": "chomskysdocument",
            "title": "Noam Chomsky's private document",
        },
        {
            "_container": "",
            "type": "Document",
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
            "_transitions": ["publish"],
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "mynews",
            "title": "My News Item with Noam Chomsky",
            "_transitions": ["publish"],
        },
        {
            "_container": "",
            "type": "Document",
            "id": "myotherfolder",
            "title": "My other Folder",
            "_transitions": ["publish"],
        },
    ]


@pytest.fixture
def user_credentials() -> tuple:
    return "user2", "averylongpasswordbutnotthatlong"


@pytest.fixture
def users(user_credentials) -> list:
    return [
        {
            "username": user_credentials[0],
            "email": "user2@foo.bar",
            "password": user_credentials[1],
            "roles": ["Member"],
        },
    ]


@pytest.fixture
def users_credentials_role(user_credentials) -> dict:
    return {
        "manager": (SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        "member": user_credentials,
        "anonymous": None,
    }


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
    "searchTabs": [
        {
            "label": "All",
            "filter": "Type(*)",
        },
        {
            "label": "Pages",
            "filter": "Type:(Page)",
        },
        {
            "label": "News Items",
            "filter": 'Type:("News Item")',
        },
        {
            "label": "Images and News Items",
            "filter": 'Type:(Image OR "News Item")',
        },
        {
            "label": "Pages and News Items",
            "filter": 'Type:(Page OR "News Item")',
        },
        {
            "label": "Contacts",
            "filter": "Type:(Image)",
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
