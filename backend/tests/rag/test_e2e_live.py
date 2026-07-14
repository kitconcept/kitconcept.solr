"""Live end-to-end test of the RAG indexing path.

Runs only when the LLM endpoint environment variables are present
(``KITCONCEPT_SOLR_LLM_URL``/``_TOKEN``) — skipped otherwise, so CI is
unaffected. Requires the docker Solr (like the service tests).

This is the verification flagged in IMPLEMENTATION-79.md: indexing a
document must create chunk sibling documents with real vectors in Solr
(via collective.solr's XML update path), and a ``{!knn}`` query with an
embedded question must retrieve them.
"""

from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.config import get_rag_config
from plone import api
from zope.component.hooks import setSite

import os
import pytest
import requests
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
def solr_select(solr_service) -> str:
    """The /select URL of the dockerized Solr core."""
    return solr_service.split("/admin/")[0] + "/select"


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
    transaction.commit()
    yield portal
    with api.env.adopt_roles(["Manager"]):
        if "vacation-policy" in portal:
            api.content.delete(portal["vacation-policy"])
        api.portal.set_registry_record("kitconcept.solr.rag_enabled", False)
        api.portal.set_registry_record("collective.solr.active", False)
    transaction.commit()


def solr_docs(solr_select, **params) -> list[dict]:
    params = {"wt": "json", "rows": 50, **params}
    # POST: knn query vectors are far too long for a GET query string
    response = requests.post(solr_select, data=params, timeout=10)
    response.raise_for_status()
    return response.json()["response"]["docs"]


class TestLiveIndexing:
    def test_chunks_indexed_and_knn_retrievable(self, portal, solr_select):
        with api.env.adopt_roles(["Manager"]):
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
            uid = doc.UID()
        transaction.commit()  # runs the indexing queue processors

        # 1. chunk sibling documents exist, with the expected fields
        chunks = solr_docs(
            solr_select,
            q=f'parent_uid:"{uid}"',
            fq="is_rag_chunk:true",
            fl="UID,parent_uid,chunk_index,chunk_text,parent_title,"
            "allowedRolesAndUsers,Language,rag_embedding_model",
        )
        assert len(chunks) >= 1
        chunk = chunks[0]
        assert chunk["UID"] == f"{uid}#rag-0"
        assert "30 days of paid vacation" in chunk["chunk_text"]
        assert chunk["parent_title"] == "Vacation policy"
        assert chunk["allowedRolesAndUsers"]  # security is denormalized
        assert chunk["rag_embedding_model"]

        # 2. the regular search never returns chunks
        parents = solr_docs(solr_select, q=f'UID:"{uid}"', fl="UID")
        assert len(parents) == 1  # the parent itself is indexed normally

        # 3. a {!knn} query with the embedded question retrieves the chunk
        client = LLMClient(get_rag_config())
        vector = client.embed_query("How many vacation days do employees get?")
        vector_str = "[" + ",".join(f"{x:.8f}" for x in vector) + "]"
        hits = solr_docs(
            solr_select,
            **{
                "q": f"{{!knn f=content_vector topK=5}}{vector_str}",
                "fq": "is_rag_chunk:true",
                "fl": "UID,parent_uid,score",
            },
        )
        assert hits, "knn query returned no chunk hits"
        assert hits[0]["parent_uid"] == uid

        # 4. deleting the content removes its chunks
        with api.env.adopt_roles(["Manager"]):
            api.content.delete(portal["vacation-policy"])
        transaction.commit()
        remaining = solr_docs(
            solr_select, q=f'parent_uid:"{uid}"', fq="is_rag_chunk:true"
        )
        assert remaining == []
