from kitconcept.solr.rag import config
from kitconcept.solr.services.site import CollectiveSolrExpander
from plone import api


class TestRagAvailableInSiteExpander:
    def expand(self, portal):
        data = {}
        CollectiveSolrExpander(portal, portal.REQUEST)(data)
        return data

    def test_unconfigured_site_reports_unavailable(self, portal):
        # toggle off (default) and/or no credentials
        data = self.expand(portal)
        assert data["kitconcept.solr.rag_available"] is False

    def test_toggle_without_credentials_degrades_gracefully(self, portal, monkeypatch):
        # Decision (graceful degradation): toggle on but no credentials
        # is NOT an error - the feature reports unavailable and the
        # classic search is used.
        monkeypatch.delenv(config.ENV_URL, raising=False)
        api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, True)
        try:
            data = self.expand(portal)
            assert data["kitconcept.solr.rag_available"] is False
        finally:
            api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, False)

    def test_toggle_with_credentials_reports_available(self, portal, monkeypatch):
        monkeypatch.setenv(config.ENV_URL, "http://llm.example.com")
        api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, True)
        try:
            data = self.expand(portal)
            assert data["kitconcept.solr.rag_available"] is True
        finally:
            api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, False)

    def test_solr_active_still_exposed(self, portal):
        data = self.expand(portal)
        assert "collective.solr.active" in data
