from kitconcept.solr.rag import pipeline as pipeline_module
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.pipeline import collapse_sources
from kitconcept.solr.rag.pipeline import ERROR_EMBEDDING_FAILED
from kitconcept.solr.rag.pipeline import ERROR_GENERATION_FAILED
from kitconcept.solr.rag.pipeline import ERROR_SOLR_UNAVAILABLE
from kitconcept.solr.rag.pipeline import format_vector
from kitconcept.solr.rag.pipeline import run_rag_search
from kitconcept.solr.rag.pipeline import search_chunks
from unittest import mock

import pytest


CONFIG = RagConfig(
    base_url="http://llm.example.com",
    token=None,
    embed_model="test-embed",
    chat_model="test-chat",
)

SECURITY_FQ = "allowedRolesAndUsers:(Anonymous)"

CHUNKS = [
    {
        "UID": "uid-a#rag-1",
        "parent_uid": "uid-a",
        "parent_title": "Vacation policy",
        "chunk_text": "30 days of paid vacation per year.",
        "path_string": "/plone/vacation-policy",
        "score": 0.9,
    },
    {
        "UID": "uid-a#rag-0",
        "parent_uid": "uid-a",
        "parent_title": "Vacation policy",
        "chunk_text": "Requests go through the HR portal.",
        "path_string": "/plone/vacation-policy",
        "score": 0.8,
    },
    {
        "UID": "uid-b#rag-0",
        "parent_uid": "uid-b",
        "parent_title": "Cafeteria",
        "chunk_text": "Meal subsidy is 6 euros.",
        "path_string": "/plone/cafeteria",
        "score": 0.5,
    },
]

PARENTS = {
    "uid-a": {
        "UID": "uid-a",
        "Title": "Vacation policy",
        "Description": "Annual leave rules.",
        "Type": "Page",
        "path_string": "/plone/vacation-policy",
    },
    "uid-b": {
        "UID": "uid-b",
        "Title": "Cafeteria",
        "Description": "Meals.",
        "Type": "Page",
        "path_string": "/plone/cafeteria",
    },
}


@pytest.fixture(autouse=True)
def portal():
    fake = mock.Mock()
    fake.getPhysicalPath.return_value = ("", "plone")
    fake.absolute_url.return_value = "http://nohost/plone"
    with mock.patch.object(pipeline_module.api.portal, "get", return_value=fake):
        yield fake


@pytest.fixture
def conn():
    return mock.Mock()


@pytest.fixture(autouse=True)
def environment(conn):
    """Fake LLM client, Solr connection, retrieval and parent lookup."""
    with (
        mock.patch.object(pipeline_module, "LLMClient") as llm_class,
        mock.patch.object(pipeline_module, "get_connection", return_value=conn),
        mock.patch.object(
            pipeline_module, "search_chunks", return_value=list(CHUNKS)
        ) as searcher,
        mock.patch.object(pipeline_module, "fetch_parents", return_value=dict(PARENTS)),
    ):
        llm_class.return_value.embed_query.return_value = [0.1, 0.2]
        llm_class.return_value.chat.return_value = "The answer is 30 days."
        yield {"llm": llm_class, "searcher": searcher}


class TestRunRagSearch:
    def test_success(self):
        result = run_rag_search("How many vacation days?", CONFIG, SECURITY_FQ)
        assert result.error is None
        assert result.answer == "The answer is 30 days."
        assert [s["UID"] for s in result.sources] == ["uid-a", "uid-b"]

    def test_thinking_is_stripped(self, environment):
        environment[
            "llm"
        ].return_value.chat.return_value = "<think>hmm</think>The answer."
        result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.answer == "The answer."

    def test_embedding_failure(self, environment):
        environment["llm"].return_value.embed_query.side_effect = LLMClientError("down")
        result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.error_code == ERROR_EMBEDDING_FAILED
        assert result.answer is None
        assert result.sources == []

    def test_generation_failure_still_exposes_sources(self, environment):
        environment["llm"].return_value.chat.side_effect = LLMClientError("down")
        result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.error_code == ERROR_GENERATION_FAILED
        assert result.answer is None
        assert [s["UID"] for s in result.sources] == ["uid-a", "uid-b"]

    def test_no_solr_connection(self):
        with mock.patch.object(pipeline_module, "get_connection", return_value=None):
            result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.error_code == ERROR_SOLR_UNAVAILABLE

    def test_solr_server_down(self):
        """A dead Solr server raises a raw socket error, not a Solr
        exception - it must map to solr_unavailable, not a 500."""
        with mock.patch.object(
            pipeline_module,
            "search_chunks",
            side_effect=ConnectionRefusedError(61, "Connection refused"),
        ):
            result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.error_code == ERROR_SOLR_UNAVAILABLE
        assert result.answer is None

    def test_no_chunks_found_is_not_an_error(self, environment):
        with mock.patch.object(pipeline_module, "search_chunks", return_value=[]):
            result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert result.error is None
        assert result.answer is None
        assert result.sources == []


class TestCollapseSources:
    def test_parents_in_rank_order_deduplicated(self, conn):
        with mock.patch.object(
            pipeline_module, "fetch_parents", return_value=dict(PARENTS)
        ):
            sources = collapse_sources(conn, CHUNKS)
        assert [s["UID"] for s in sources] == ["uid-a", "uid-b"]

    def test_source_shape(self, conn):
        with mock.patch.object(
            pipeline_module, "fetch_parents", return_value=dict(PARENTS)
        ):
            sources = collapse_sources(conn, CHUNKS)
        source = sources[0]
        assert source["@id"] == "http://nohost/plone/vacation-policy"
        assert source["title"] == "Vacation policy"
        assert source["description"] == "Annual leave rules."
        assert source["@type"] == "Page"
        # snippet comes from the best ranked chunk of the parent
        assert source["snippet"] == "30 days of paid vacation per year."

    def test_missing_parent_metadata_falls_back_to_chunk(self, conn):
        with mock.patch.object(pipeline_module, "fetch_parents", return_value={}):
            sources = collapse_sources(conn, CHUNKS)
        assert sources[0]["title"] == "Vacation policy"
        assert sources[0]["@id"] == "http://nohost/plone/vacation-policy"


class TestSearchChunks:
    def fake_response(self):
        response = mock.Mock()
        response.read.return_value = (
            b'<?xml version="1.0"?><response>'
            b'<result name="response" numFound="0" start="0"/></response>'
        )
        return response

    def search_params(self, conn, **kwargs):
        conn.search.return_value = self.fake_response()
        with mock.patch.object(pipeline_module, "SolrResponse") as solr_response:
            solr_response.return_value.results.return_value = []
            search_chunks(conn, [0.5, 0.5], SECURITY_FQ, **kwargs)
        return conn.search.call_args.kwargs

    def test_knn_query_with_security_prefilter(self, conn):
        params = self.search_params(conn)
        assert params["q"].startswith("{!knn f=content_vector topK=")
        assert format_vector([0.5, 0.5]) in params["q"]
        assert SECURITY_FQ in params["fq"]
        assert "is_rag_chunk:true" in params["fq"]

    def test_path_prefix_filter(self, conn):
        params = self.search_params(conn, path_prefix="/documents/")
        assert 'path_parents:"/plone/documents"' in params["fq"]

    def test_language_filter(self, conn):
        params = self.search_params(conn, lang="en")
        assert "Language:(en OR any)" in params["fq"]
