from kitconcept.solr.rag import config
from plone import api


class TestRagRegistryToggle:
    def test_record_exists_and_defaults_to_off(self, portal):
        value = api.portal.get_registry_record(
            config.REGISTRY_ENABLED_KEY, default=None
        )
        assert value is False

    def test_rag_enabled_follows_registry(self, portal):
        assert config.rag_enabled() is False
        api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, True)
        try:
            assert config.rag_enabled() is True
        finally:
            api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, False)

    def test_get_rag_config_needs_toggle_and_url(self, portal, monkeypatch):
        monkeypatch.setenv(config.ENV_URL, "http://llm.example.com")
        assert config.get_rag_config() is None  # toggle off
        api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, True)
        try:
            cfg = config.get_rag_config()
            assert cfg is not None
            assert cfg.base_url == "http://llm.example.com"
        finally:
            api.portal.set_registry_record(config.REGISTRY_ENABLED_KEY, False)
