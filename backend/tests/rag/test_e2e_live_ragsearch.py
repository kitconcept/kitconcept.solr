"""Live test of the minimal @rag-search endpoint (RAG: TESTING).

Same gating as test_e2e_live.py: runs only with the LLM env vars set
and the docker Solr running. Goes with the throwaway endpoint and is
removed together with it.
"""

from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from zope.component.hooks import setSite

import os
import pytest
import transaction


LIVE = bool(os.environ.get("KITCONCEPT_SOLR_LLM_URL")) and bool(
    os.environ.get("KITCONCEPT_SOLR_LLM_TOKEN")
)

pytestmark = pytest.mark.skipif(
    not LIVE,
    reason="live LLM test: KITCONCEPT_SOLR_LLM_URL/_TOKEN not set",
)

BODY_TEXT = (
    "Employees are entitled to 30 days of paid vacation per year. "
    "Vacation requests are submitted through the HR portal and must be "
    "approved by the team lead."
)


@pytest.fixture()
def portal(functional, solr_service):
    portal = functional["app"]["plone"]
    setSite(portal)
    with api.env.adopt_roles(["Manager", "Member"]):
        api.portal.set_registry_record("collective.solr.active", True)
        api.portal.set_registry_record("kitconcept.solr.rag_enabled", True)
        maintenance = api.content.get_view(
            "solr-maintenance", portal, functional["request"]
        )
        maintenance.clear()
        doc = api.content.create(
            container=portal,
            type="Document",
            id="vacation-policy",
            title="Vacation policy",
            description="How much annual leave employees get.",
        )
        doc.blocks = {"b1": {"@type": "slate", "plaintext": BODY_TEXT}}
        doc.blocks_layout = {"items": ["b1"]}
        doc.reindexObject()
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        api.content.delete(portal["vacation-policy"])
        api.portal.set_registry_record("kitconcept.solr.rag_enabled", False)
        api.portal.set_registry_record("collective.solr.active", False)
    transaction.commit()


@pytest.fixture()
def manager_session(portal):
    session = RelativeSession(portal.absolute_url())
    session.headers.update({"Accept": "application/json"})
    session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    return session


class TestLiveRagSearch:
    def test_answer_with_sources(self, manager_session):
        response = manager_session.get(
            "/@rag-search",
            params={"q": "How many vacation days do employees get?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is None
        assert data["answer"], "expected a generated answer"
        assert "30" in data["answer"]
        assert data["sources"]
        assert data["sources"][0]["title"] == "Vacation policy"
        assert "<think>" not in data["answer"]

    def test_missing_question_is_bad_request(self, manager_session):
        response = manager_session.get("/@rag-search")
        assert response.status_code == 400
