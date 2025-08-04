from base64 import b64decode
from collections import defaultdict
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.namedfile import NamedBlobImage
from plone.restapi.testing import RelativeSession
from zope.component.hooks import setSite

import pytest
import transaction


@pytest.fixture
def users() -> list:
    """Additional users to be created."""
    return []


@pytest.fixture
def contents() -> list:
    """Content to be created."""
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
            "id": "mydocument",
            "title": "My Document about Noam Chomsky",
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


@pytest.fixture
def all_path_string():
    """Helper fixture to extract path information from Solr result."""

    def func(data: dict) -> list[str]:
        return [item["path_string"] for item in data["response"]["docs"]]

    return func


@pytest.fixture
def create_contents(contents):
    """Helper fixture to create initial content."""

    def func(portal) -> dict:
        ids = defaultdict(list)
        for item in contents:
            container_path = item["_container"]
            container = portal.unrestrictedTraverse(container_path)
            payload = {"container": container, "language": "en"}
            if "_image" in item:
                payload["image"] = NamedBlobImage(b64decode(item["_image"]))
            for key, value in item.items():
                if key.startswith("_"):
                    continue
                payload[key] = value
            content = api.content.create(**payload)
            content.language = payload["language"]
            # Set translation
            if "_translation_of" in item:
                source = portal.unrestrictedTraverse(item["_translation_of"])
                ITranslationManager(source).register_translation(
                    content.language, content
                )
            # Transition items
            if "_transitions" in item:
                transitions = item["_transitions"]
                for transition in transitions:
                    api.content.transition(content, transition=transition)
            ids[container_path].append(content.getId())
        return ids

    return func


@pytest.fixture()
def app(functional):
    return functional["app"]


@pytest.fixture()
def http_request(functional):
    return functional["request"]


@pytest.fixture()
def registry_config() -> dict:
    """Fixture with plone.app.registry settings."""
    return {"collective.solr.active": 1}


@pytest.fixture()
def portal(app, solr_service, http_request, users, registry_config):
    """Plone portal with additional users, and registry configuration set."""
    portal = app["plone"]
    setSite(portal)
    current_values = {}
    with api.env.adopt_roles(["Manager", "Member"]):
        for key, value in registry_config.items():
            current_values[key] = api.portal.get_registry_record(key)
            api.portal.set_registry_record(key, value)
        maintenance = api.content.get_view("solr-maintenance", portal, http_request)
        maintenance.clear()
        # Create additional users
        for user in users:
            api.user.create(**user)
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        for key, value in current_values.items():
            api.portal.set_registry_record(key, value)
    transaction.commit()


@pytest.fixture()
def portal_with_content(app, portal, create_contents):
    """Plone portal with initial content."""
    with api.env.adopt_roles(["Manager"]):
        content_ids = create_contents(portal)
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        containers = sorted(content_ids.keys(), reverse=True)
        for container_path in containers:
            container = portal.unrestrictedTraverse(container_path)
            container.manage_delObjects(content_ids[container_path])
    transaction.commit()


@pytest.fixture()
def maintenance(portal, http_request):
    """Return browser view for solr maintenance."""
    with api.env.adopt_roles(["Manager"]):
        view = api.content.get_view("solr-maintenance", portal, http_request)
    return view


@pytest.fixture()
def request_factory(portal):
    """Fixture returning a session to call the API."""

    def factory() -> RelativeSession:
        url = portal.absolute_url()
        api_session = RelativeSession(url)
        api_session.headers.update({"Accept": "application/json"})
        return api_session

    return factory


@pytest.fixture()
def anon_request(request_factory):
    """Anonymous API requests."""
    return request_factory()


@pytest.fixture()
def manager_request(request_factory):
    """Manager API requests."""
    request = request_factory()
    request.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield request
    request.auth = ()
