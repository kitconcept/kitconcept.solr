from kitconcept.solr.testing import FUNCTIONAL_TESTING
from kitconcept.solr.testing import INTEGRATION_TESTING
from pathlib import Path
from pytest_plone import fixtures_factory
from requests import exceptions as exc

import os
import pytest
import requests


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture(scope="class")
def functional_class_bracket(functional_class):
    """A class-scoped test bracket on the functional layer.

    Runs the layer's testSetUp/testTearDown once per test *class*
    instead of once per test function, so expensive per-class fixtures
    (content creation, a shared query) can be set up a single time and
    shared by all tests of the class - the pattern the old
    zope.testrunner layers provided. plone.testing layer resources are
    stacked (LIFO), so per-function brackets can still nest inside if
    a test also uses the function-scoped ``functional`` fixture.

    Tests of a class using this bracket share one ZODB/Solr state:
    suitable for the common read-only pattern (create content, run a
    query, assert many times); not for tests that mutate content.
    """
    layer = functional_class
    layer.testSetUp()
    yield layer
    layer.testTearDown()


@pytest.fixture(scope="session", autouse=True)
def keep_zope_layers(functional_session, integration_session):
    """Keep the expensive Plone test layers alive for the whole session.

    zope.pytestlayer only preserves layers across test classes for
    zope.testrunner style tests (with a ``layer`` class attribute);
    for pytest style tests its class-scoped layer fixture tears the
    whole layer stack down after every test class, so the Plone site
    got rebuilt many times per run - the main reason the suite became
    much slower after the unittest to pytest migration. Depending on
    the session-scoped layer fixtures marks the layers as
    keep-for-whole-session: they are set up once and torn down at the
    end of the session. Per-test isolation (testSetUp/testTearDown)
    is unaffected.
    """


def is_responsive(url):
    """Helper fixture to check if Solr is up and running."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return b"""<str name="status">OK</str>""" in response.content
    except (exc.ConnectionError, exc.Timeout):
        return False


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    """Return the name of the Docker Compose project."""
    return "kitconcept-solr-tests"


@pytest.fixture(scope="session")
def docker_setup():
    """Return the Docker Compose commands to set up the stack."""
    # Ephemeral host ports for the test containers: the tests must
    # never coincide with a locally running site Solr on 8983 - with
    # fixed ports they would either clobber its index or fail to bind.
    # The actual port is read back via docker_services.port_for.
    os.environ.setdefault("SOLR_ACCEPTANCE_PORT", "0")
    os.environ.setdefault("TIKA_ACCEPTANCE_PORT", "0")
    # Stop the stack before starting a new one, only start the Solr service
    profile = "solr"
    return [f"--profile {profile} down -v", f"--profile {profile} up --build -d"]


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Fixture pointing to the docker-compose file to be used."""
    backend_root = Path(str(pytestconfig.rootdir)).resolve()
    repo_root = backend_root.parent
    return repo_root / "docker-compose-dev.yml"


@pytest.fixture(scope="session")
def solr_port(docker_services) -> int:
    """The (ephemeral) host port of the test Solr container."""
    return docker_services.port_for("solr-acceptance", 8983)


@pytest.fixture(scope="session")
def solr_service(docker_ip, docker_services, solr_port):
    """Ensure that Solr service is up and responsive."""
    url = f"http://{docker_ip}:{solr_port}/solr/plone/admin/ping?wt=xml"
    docker_services.wait_until_responsive(
        timeout=90.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url
