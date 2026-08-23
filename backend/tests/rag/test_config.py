from kitconcept.solr.rag import config
from unittest import mock

import pytest


@pytest.fixture
def enabled_toggle():
    """Pretend the registry toggle is on."""
    with mock.patch.object(config, "rag_enabled", return_value=True):
        yield


class TestGetRagConfig:
    def test_disabled_toggle_returns_none(self, monkeypatch):
        monkeypatch.setenv(config.ENV_URL, "http://llm.example.com")
        with mock.patch.object(config, "rag_enabled", return_value=False):
            assert config.get_rag_config() is None

    def test_no_url_returns_none(self, enabled_toggle, monkeypatch):
        monkeypatch.delenv(config.ENV_URL, raising=False)
        assert config.get_rag_config() is None

    def test_defaults(self, enabled_toggle, monkeypatch):
        monkeypatch.setenv(config.ENV_URL, "http://llm.example.com/")
        for name in (
            config.ENV_TOKEN,
            config.ENV_EMBED_MODEL,
            config.ENV_CHAT_MODEL,
            config.ENV_EMBED_PATH,
            config.ENV_CHAT_PATH,
        ):
            monkeypatch.delenv(name, raising=False)
        cfg = config.get_rag_config()
        assert cfg.base_url == "http://llm.example.com"  # trailing / stripped
        assert cfg.token is None
        assert cfg.embed_model == config.DEFAULT_EMBED_MODEL
        assert cfg.chat_model == config.DEFAULT_CHAT_MODEL
        assert cfg.embed_path == config.DEFAULT_EMBED_PATH
        assert cfg.chat_path == config.DEFAULT_CHAT_PATH

    def test_env_overrides(self, enabled_toggle, monkeypatch):
        monkeypatch.setenv(config.ENV_URL, "http://llm.example.com")
        monkeypatch.setenv(config.ENV_TOKEN, "secret")
        monkeypatch.setenv(config.ENV_EMBED_MODEL, "custom-embed")
        monkeypatch.setenv(config.ENV_CHAT_MODEL, "custom-chat")
        monkeypatch.setenv(config.ENV_EMBED_PATH, "/api/embed")
        monkeypatch.setenv(config.ENV_CHAT_PATH, "/v1/chat/completions")
        cfg = config.get_rag_config()
        assert cfg.token == "secret"
        assert cfg.embed_model == "custom-embed"
        assert cfg.chat_model == "custom-chat"
        assert cfg.embed_path == "/api/embed"
        assert cfg.chat_path == "/v1/chat/completions"

    def test_rag_enabled_without_registry_is_false(self):
        # Outside a configured Zope site there is no registry utility;
        # the toggle must default to off instead of breaking.
        assert config.rag_enabled() is False


class TestEstimateTokens:
    def test_rounds_up(self):
        assert config.estimate_tokens("abcde") == 2

    def test_empty(self):
        assert config.estimate_tokens("") == 0
