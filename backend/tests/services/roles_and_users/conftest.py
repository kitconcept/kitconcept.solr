from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import pytest


@pytest.fixture
def contents() -> list:
    return [
        {
            "_container": "",
            "type": "Document",
            "id": "document1",
            "title": "My Document about Noam Chomsky",
            "_transitions": ["publish"],
        },
        {
            "_container": "",
            "type": "Document",
            "id": "document2",
            "title": "My Private Document about Noam Chomsky",
        },
    ]


@pytest.fixture
def user_credentials() -> tuple:
    return "user2", "averylongpasswordbutnotthatlong"


@pytest.fixture
def member_as_user1_credentials() -> tuple:
    return "member_as_user1", "averylongpasswordbutnotthatlong"


@pytest.fixture
def users(user_credentials, member_as_user1_credentials) -> list:
    return [
        {
            "username": user_credentials[0],
            "email": "user2@foo.bar",
            "password": user_credentials[1],
            "roles": ["Member"],
        },
        {
            "username": member_as_user1_credentials[0],
            "email": "user2@foo.bar",
            "password": member_as_user1_credentials[1],
            "roles": ["Member"],
        },
    ]


@pytest.fixture
def users_credentials_role(user_credentials, member_as_user1_credentials) -> dict:
    return {
        "manager": (SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        "member": user_credentials,
        "anonymous": None,
        "member_as_user1": member_as_user1_credentials,
    }
