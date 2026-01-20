from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import kitconcept.solr
import plone.exportimport
import plone.volto


class KSolrLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.volto)
        self.loadZCML(package=plone.exportimport)
        self.loadZCML(package=kitconcept.solr)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "kitconcept.solr:default")
        applyProfile(portal, "kitconcept.solr:testing")
        # Applying the plone.volto profile is important for content types
        # we rely on in the tests, for example a folderish Document.
        # st = portal.portal_setup
        # st.runAllImportStepsFromProfile("plone.volto:default")
        applyProfile(portal, "plone.volto:default")


FIXTURE = KSolrLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="KSolrLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, PLONE_RESTAPI_DX_FUNCTIONAL_TESTING),
    name="KSolrLayer:FunctionalTesting",
)
