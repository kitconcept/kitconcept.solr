"""Integration test of the full RAG path with a deterministic mock LLM.

Runs in CI: needs the docker Solr (like the service tests) but no LLM
server — the client methods are patched with deterministic fakes, so
this covers everything except the LLM itself: chunk indexing through
the real Solr XML update path, the schema fields, the {!knn} and
keyword queries, hybrid fusion, and the @rag-search service over HTTP.

The fake embeddings map topics to orthogonal unit vectors, so vector
retrieval ranks deterministically.
"""

from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.config import ENV_URL
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from unittest import mock
from zope.component.hooks import setSite

import pytest
import transaction


DIMENSION = 768

TOPIC_AXES = {
    "vacation": 0,
    "security": 1,
}
OTHER_AXIS = 2

CANNED_ANSWER = "According to the vacation policy you get 30 days."


def topic_vector(text: str) -> list[float]:
    """A unit vector on the axis of the text's topic."""
    lowered = text.lower()
    axis = OTHER_AXIS
    for topic, topic_axis in TOPIC_AXES.items():
        if topic in lowered:
            axis = topic_axis
            break
    vector = [0.0] * DIMENSION
    vector[axis] = 1.0
    return vector


def fake_embed_documents(self, texts):
    return [topic_vector(text) for text in texts]


def fake_embed_query(self, text):
    return topic_vector(text)


def fake_chat(self, prompt, system=None):
    return f"<think>reasoning</think>{CANNED_ANSWER}"


@pytest.fixture()
def mock_llm(monkeypatch):
    """Deterministic LLM client + enabled feature, no network."""
    monkeypatch.setenv(ENV_URL, "http://mock-llm.invalid")
    with (
        mock.patch.object(LLMClient, "embed_documents", fake_embed_documents),
        mock.patch.object(LLMClient, "embed_query", fake_embed_query),
        mock.patch.object(LLMClient, "chat", fake_chat),
    ):
        yield


@pytest.fixture()
def portal(functional, solr_service, solr_port, mock_llm):
    portal = functional["app"]["plone"]
    setSite(portal)
    with api.env.adopt_roles(["Manager", "Member"]):
        # The test Solr runs on an ephemeral host port (never the fixed
        # 8983 of a locally running site Solr) - point collective.solr
        # at it before activating.
        api.portal.set_registry_record("collective.solr.port", solr_port)
        api.portal.set_registry_record("collective.solr.active", True)
        api.portal.set_registry_record("kitconcept.solr.rag_enabled", True)
        maintenance = api.content.get_view(
            "solr-maintenance", portal, functional["request"]
        )
        maintenance.clear()
        for doc_id, title, body in [
            (
                "vacation-policy",
                "Vacation policy",
                "Employees get 30 days of vacation per year.",
            ),
            (
                "it-rules",
                "IT rules",
                "Security guidelines: two-factor authentication required.",
            ),
        ]:
            doc = api.content.create(
                container=portal, type="Document", id=doc_id, title=title
            )
            doc.blocks = {"b1": {"@type": "slate", "plaintext": body}}
            doc.blocks_layout = {"items": ["b1"]}
            doc.reindexObject()
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        for doc_id in ["vacation-policy", "it-rules"]:
            if doc_id in portal:
                api.content.delete(portal[doc_id])
        api.portal.set_registry_record("kitconcept.solr.rag_enabled", False)
        api.portal.set_registry_record("collective.solr.active", False)
    transaction.commit()


@pytest.fixture()
def manager_session(portal):
    session = RelativeSession(portal.absolute_url())
    session.headers.update({"Accept": "application/json"})
    session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    return session


class TestRagIntegrationWithMockLLM:
    def test_full_path_vacation_question(self, manager_session):
        response = manager_session.get(
            "/@rag-search",
            params={"q": "How much vacation do I get?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is None
        # canned answer passed through, thinking block stripped
        assert data["answer"] == CANNED_ANSWER
        # vector retrieval ranks the on-topic document first
        assert data["sources"]
        assert data["sources"][0]["title"] == "Vacation policy"
        # hybrid: the keyword hit ("vacation" in title/text) is fused in
        titles = [source["title"] for source in data["sources"]]
        assert "Vacation policy" in titles

    def test_full_path_security_question(self, manager_session):
        response = manager_session.get(
            "/@rag-search",
            params={"q": "What are the security rules?"},
        )
        data = response.json()
        assert data["answer"] == CANNED_ANSWER
        assert data["sources"][0]["title"] == "IT rules"
        assert data["sources"][0]["snippet"]

    def test_chunks_indexed_with_fake_vectors(self, portal, solr_service):
        import requests

        select = solr_service.split("/admin/")[0] + "/select"
        response = requests.post(
            select,
            data={"q": "is_rag_chunk:true", "rows": 0, "wt": "json"},
            timeout=10,
        )
        assert response.json()["response"]["numFound"] >= 2
