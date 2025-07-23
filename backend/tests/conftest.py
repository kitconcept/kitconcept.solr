from kitconcept.solr.testing import FUNCTIONAL_TESTING
from kitconcept.solr.testing import INTEGRATION_TESTING
from pathlib import Path
from pytest_plone import fixtures_factory
from requests import exceptions as exc

import pytest
import requests


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


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
    # Stop the stack before starting a new one, only start the Solr service
    profile = "solr"
    return [f"--profile {profile} down -v", f"--profile {profile} up --build -d"]


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Fixture pointing to the docker-compose file to be used."""
    backend_root = Path(str(pytestconfig.rootdir)).resolve()
    repo_root = backend_root.parent
    return repo_root / "docker-compose-dev.yml"


@pytest.fixture
def solr_service(docker_ip, docker_services):
    """Ensure that Solr service is up and responsive."""
    port = docker_services.port_for("solr-acceptance", 8983)
    url = f"http://{docker_ip}:{port}/solr/plone/admin/ping?wt=xml"
    docker_services.wait_until_responsive(
        timeout=90.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url
