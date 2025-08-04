from collections import defaultdict
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from zope.component.hooks import setSite

import pytest
import transaction


@pytest.fixture()
def app(functional):
    return functional["app"]


@pytest.fixture
def create_contents():
    """Helper fixture to create initial content."""

    def func(portal) -> dict:
        ids = defaultdict(list)
        return ids

    return func


@pytest.fixture()
def portal(app, registry_config):
    """Plone portal with additional users, and registry configuration set."""
    portal = app["plone"]
    setSite(portal)
    current_values = {}
    with api.env.adopt_roles(["Manager", "Member"]):
        for key, value in registry_config.items():
            current_values[key] = api.portal.get_registry_record(key)
            api.portal.set_registry_record(key, value)
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
