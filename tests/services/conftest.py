from base64 import b64decode
from collections import defaultdict
from pathlib import Path
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.namedfile import NamedBlobImage
from plone.restapi.testing import RelativeSession
from typing import List
from zope.component.hooks import setSite

import pytest
import requests
import transaction


@pytest.fixture
def users() -> List:
    return []


@pytest.fixture
def contents() -> List:
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "noamchomsky",
            "title": "Prof. Dr. Noam Chomsky",
            "subjects": ["mymembersubject", "mymembersubjecttwo"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",  # noQA
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
    def func(data: dict) -> List[str]:
        return [item["path_string"] for item in data["response"]["docs"]]

    return func


@pytest.fixture
def create_contents(contents):
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


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return """<str name="status">OK</str>""" in response.content
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return Path(str(pytestconfig.rootdir)).resolve() / "docker-compose.yml"


@pytest.fixture
def solr_service(docker_ip, docker_services):
    """Ensure that Solr service is up and responsive."""
    port = docker_services.port_for("solr", 8983)
    url = f"http://{docker_ip}:{port}/admin/ping?wt=xml"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture()
def app(functional):
    return functional["app"]


@pytest.fixture()
def http_request(functional):
    return functional["request"]


@pytest.fixture()
def registry_config() -> dict:
    return {"collective.solr.active": 1}


@pytest.fixture()
def portal(app, docker_services, http_request, users, registry_config):
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
    with api.env.adopt_roles(["Manager"]):
        content_ids = create_contents(portal)
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        containers = sorted([path for path in content_ids.keys()], reverse=True)
        for container_path in containers:
            container = portal.unrestrictedTraverse(container_path)
            container.manage_delObjects(content_ids[container_path])
    transaction.commit()


@pytest.fixture()
def maintenance(portal, http_request):
    with api.env.adopt_roles(["Manager"]):
        view = api.content.get_view("solr-maintenance", portal, http_request)
    return view


@pytest.fixture()
def request_factory(portal):
    def factory():
        url = portal.absolute_url()
        api_session = RelativeSession(url)
        api_session.headers.update({"Accept": "application/json"})
        return api_session

    return factory


@pytest.fixture()
def anon_request(request_factory):
    return request_factory()


@pytest.fixture()
def manager_request(request_factory):
    request = request_factory()
    request.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield request
    request.auth = ()
