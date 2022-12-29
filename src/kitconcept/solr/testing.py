from plone import api
from collective.solr.testing import CollectiveSolrLayer
from collective.solr.testing import SolrLayer
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import PLONE_ROBOT_TESTING
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

import kitconcept.solr
import http.client
import os.path
import six
import subprocess
import sys
from time import sleep


# Use `solr_start`, `solr_stop` scripts directly from `solr/bin`
BIN_DIR = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "solr", "bin"
    )
)


class KitconceptSolrLayer(PloneSandboxLayer):
    """Kitconcept Solr Testing Layer that sets up a Plone site with the
    kitconcept.solr:testing profile."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.MockMailHost

        self.loadZCML(package=collective.MockMailHost)
        self.loadZCML(package=kitconcept.solr)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        api.content.create(
            type="Document", id="front-page", title="Welcome", container=portal
        )
        logout()
        applyProfile(portal, "kitconcept.solr:default")


KITCONCEPT_SOLR_FIXTURE = KitconceptSolrLayer()


COLLECTIVE_SOLR_FIXTURE = CollectiveSolrLayer(solr_active=True)

KITCONCEPT_SOLR_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(KITCONCEPT_SOLR_FIXTURE,), name="KitconceptSolrLayer:IntegrationTesting"
)


KITCONCEPT_SOLR_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(KITCONCEPT_SOLR_FIXTURE, WSGI_SERVER_FIXTURE),
    name="KitconceptSolrLayer:FunctionalTesting",
)


class DockerizedSolrLayer(SolrLayer):
    """Solr test layer that fires up and shuts down a Solr instance. This
    layer can be used to unit test a Solr configuration without having to
    fire up Plone.

    This modifies the original SolrLayer by controlling solr from scripts
    in a different location. Thus is able to run in a setup without buildout.
    """

    def setUp(self):
        """Start Solr and poll until it is up and running."""
        self.proc = subprocess.call(
            "./solr-start", shell=True, close_fds=True, cwd=BIN_DIR
        )
        # Poll Solr until it is up and running
        solr_ping_url = "{0}/admin/ping?wt=xml".format(self.solr_url)
        for i in range(1, 10):
            try:
                result = six.moves.urllib.request.urlopen(solr_ping_url)
                if result.code == 200:
                    if b'<str name="status">OK</str>' in result.read():
                        break
            except (
                six.moves.urllib.error.URLError,
                http.client.RemoteDisconnected,
                ConnectionResetError,
            ):
                # Catch errors,
                # in addition also catch not connected error (happens on docker startup)
                sleep(3)
                sys.stdout.write(".")
            if i == 9:
                subprocess.call("./solr-stop", shell=True, close_fds=True, cwd=BIN_DIR)
                sys.stdout.write("Solr Instance could not be started !!!")

    def tearDown(self):
        """Stop Solr."""
        subprocess.check_call("./solr-stop", shell=True, close_fds=True, cwd=BIN_DIR)


class KitconceptSolrSolrLayer(CollectiveSolrLayer):
    """Kitconcept Solr with Solr Testing Layer."""

    def __init__(
        self,
        bases=None,
        name="Collective Solr Layer",
        module=None,
        solr_host="localhost",
        solr_port=8983,
        solr_base="/solr/plone",
        solr_active=False,
    ):
        super(PloneSandboxLayer, self).__init__(bases, name, module)
        self.solr_active = solr_active
        self.solr_host = solr_host
        self.solr_port = solr_port
        self.solr_base = solr_base
        # SolrLayer should use the same settings as CollectiveSolrLayer
        self.solr_layer = DockerizedSolrLayer(
            bases,
            name,
            module,
            solr_host=solr_host,
            solr_port=solr_port,
            solr_base=solr_base,
        )

    def setUpZope(self, app, configurationContext):
        KitconceptSolrLayer.setUpZope(self, app, configurationContext)
        super(KitconceptSolrSolrLayer, self).setUpZope(app, configurationContext)

    def setUpPloneSite(self, portal):
        KitconceptSolrLayer.setUpPloneSite(self, portal)
        super(KitconceptSolrSolrLayer, self).setUpPloneSite(portal)
        applyProfile(portal, "kitconcept.solr:testing")


KITCONCEPT_SOLR_SOLR_FIXTURE = KitconceptSolrSolrLayer(solr_active=True)

KITCONCEPT_SOLR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(
        KITCONCEPT_SOLR_SOLR_FIXTURE,
        WSGI_SERVER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
    ),
    name="KitconceptSolrLayer:SolrFunctionalTesting",
)

KITCONCEPT_SOLR_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_SOLR_FIXTURE, PLONE_ROBOT_TESTING),
    # bases=(COLLECTIVE_SOLR_FIXTURE, WSGI_SERVER_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE), # noqa
    name="KitconceptSolrLayer:AcceptanceTesting",
)
