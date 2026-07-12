from kitconcept.solr.rag import pipeline as pipeline_module
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.config import RETRIEVAL_KNN
from kitconcept.solr.rag.pipeline import assemble_context
from kitconcept.solr.rag.pipeline import build_sources
from kitconcept.solr.rag.pipeline import ERROR_EMBEDDING_FAILED
from kitconcept.solr.rag.pipeline import ERROR_GENERATION_FAILED
from kitconcept.solr.rag.pipeline import ERROR_SOLR_UNAVAILABLE
from kitconcept.solr.rag.pipeline import format_vector
from kitconcept.solr.rag.pipeline import parent_ranking
from kitconcept.solr.rag.pipeline import rrf_fuse
from kitconcept.solr.rag.pipeline import run_rag_search
from kitconcept.solr.rag.pipeline import search_chunks
from kitconcept.solr.rag.pipeline import search_keyword
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
        mock.patch.object(
            pipeline_module, "search_keyword", return_value=[]
        ) as keyword,
        mock.patch.object(pipeline_module, "fetch_leading_chunks", return_value=[]),
        mock.patch.object(pipeline_module, "fetch_parents", return_value=dict(PARENTS)),
    ):
        llm_class.return_value.embed_query.return_value = [0.1, 0.2]
        llm_class.return_value.chat.return_value = "The answer is 30 days."
        yield {"llm": llm_class, "searcher": searcher, "keyword": keyword}


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


class TestBuildSources:
    def test_parents_in_given_order(self, conn):
        with mock.patch.object(
            pipeline_module, "fetch_parents", return_value=dict(PARENTS)
        ):
            sources = build_sources(conn, ["uid-a", "uid-b"], CHUNKS)
        assert [s["UID"] for s in sources] == ["uid-a", "uid-b"]

    def test_source_shape(self, conn):
        with mock.patch.object(
            pipeline_module, "fetch_parents", return_value=dict(PARENTS)
        ):
            sources = build_sources(conn, ["uid-a", "uid-b"], CHUNKS)
        source = sources[0]
        assert source["@id"] == "http://nohost/plone/vacation-policy"
        assert source["title"] == "Vacation policy"
        assert source["description"] == "Annual leave rules."
        assert source["@type"] == "Page"
        # snippet comes from the best ranked chunk of the parent
        assert source["snippet"] == "30 days of paid vacation per year."

    def test_missing_parent_metadata_falls_back_to_chunk(self, conn):
        with mock.patch.object(pipeline_module, "fetch_parents", return_value={}):
            sources = build_sources(conn, ["uid-a", "uid-b"], CHUNKS)
        assert sources[0]["title"] == "Vacation policy"
        assert sources[0]["@id"] == "http://nohost/plone/vacation-policy"

    def test_parent_without_context_chunk_has_empty_snippet(self, conn):
        with mock.patch.object(
            pipeline_module, "fetch_parents", return_value=dict(PARENTS)
        ):
            sources = build_sources(conn, ["uid-a", "uid-b"], CHUNKS[:1])
        assert sources[1]["snippet"] == ""
        assert sources[1]["title"] == "Cafeteria"


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


class TestHybridRetrieval:
    def test_hybrid_fuses_keyword_ranking(self, environment):
        # keyword search promotes uid-b ahead of knn's uid-a ordering
        environment["keyword"].return_value = ["uid-b", "uid-a"]
        result = run_rag_search("q", CONFIG, SECURITY_FQ)
        # both rank lists: knn [uid-a, uid-b], keyword [uid-b, uid-a]
        # -> RRF ties resolved by first (knn) ranking order
        assert [s["UID"] for s in result.sources] == ["uid-a", "uid-b"]
        environment["keyword"].assert_called_once()

    def test_keyword_only_parent_joins_sources(self, environment):
        environment["keyword"].return_value = ["uid-a", "uid-c"]
        parents = dict(PARENTS)
        parents["uid-c"] = {
            "UID": "uid-c",
            "Title": "Third doc",
            "Description": "",
            "Type": "Page",
            "path_string": "/plone/third",
        }
        with mock.patch.object(pipeline_module, "fetch_parents", return_value=parents):
            result = run_rag_search("q", CONFIG, SECURITY_FQ)
        assert "uid-c" in [s["UID"] for s in result.sources]

    def test_knn_mode_skips_keyword_search(self, environment):
        config = RagConfig(
            base_url=CONFIG.base_url,
            token=None,
            embed_model=CONFIG.embed_model,
            chat_model=CONFIG.chat_model,
            retrieval=RETRIEVAL_KNN,
        )
        result = run_rag_search("q", config, SECURITY_FQ)
        environment["keyword"].assert_not_called()
        assert result.error is None


class TestRrfFuse:
    def test_agreement_wins(self):
        fused = rrf_fuse([["a", "b", "c"], ["b", "a", "c"]])
        # a: 1/61 + 1/62; b: 1/62 + 1/61 -> tie broken by first list
        assert fused[0] == "a"
        assert set(fused) == {"a", "b", "c"}

    def test_item_in_both_lists_beats_single_list_items(self):
        fused = rrf_fuse([["a", "b"], ["c", "b"]])
        assert fused[0] == "b"

    def test_single_ranking_passthrough(self):
        assert rrf_fuse([["x", "y", "z"]]) == ["x", "y", "z"]

    def test_empty(self):
        assert rrf_fuse([[], []]) == []


class TestParentRanking:
    def test_dedupes_preserving_order(self):
        assert parent_ranking(CHUNKS) == ["uid-a", "uid-b"]

    def test_skips_chunks_without_parent(self):
        assert parent_ranking([{"chunk_text": "x"}]) == []


class TestAssembleContext:
    def test_knn_chunks_used_in_fused_order(self, conn):
        context = assemble_context(conn, CHUNKS, ["uid-b", "uid-a"])
        assert [c["UID"] for c in context] == [
            "uid-b#rag-0",
            "uid-a#rag-1",
            "uid-a#rag-0",
        ]

    def test_keyword_only_parent_chunks_are_fetched(self, conn):
        fetched = [
            {
                "UID": "uid-c#rag-0",
                "parent_uid": "uid-c",
                "parent_title": "Third doc",
                "chunk_text": "Third doc text.",
            }
        ]
        with mock.patch.object(
            pipeline_module, "fetch_leading_chunks", return_value=fetched
        ) as fetcher:
            context = assemble_context(conn, CHUNKS, ["uid-c", "uid-a"])
        fetcher.assert_called_once_with(conn, "uid-c")
        assert context[0]["UID"] == "uid-c#rag-0"
        assert context[1]["UID"] == "uid-a#rag-1"


class TestSearchKeyword:
    def fake_search(self, conn, **kwargs):
        conn.search.return_value = mock.Mock()
        with mock.patch.object(pipeline_module, "SolrResponse") as solr_response:
            solr_response.return_value.results.return_value = []
            search_keyword(conn, "usb stick?", SECURITY_FQ, **kwargs)
        return conn.search.call_args.kwargs

    def test_query_is_exact_copy_of_solr_main_query(self, conn):
        """Pin the scoring expression to the @solr main query.

        This test intentionally spells out every clause and boost of
        SolrSearch._base_query: if either side changes, it must fail,
        so the copies cannot drift apart silently. A shared query
        builder replacing the copy is a planned refactoring.
        """
        params = self.fake_search(conn)
        term = "(usb stick\\?)"
        assert params["q"] == (
            f"+(Title:{term}^5 OR Description:{term}^2 OR id:{term}^0.75 "
            f"OR text_prefix:{term}^0.75 OR text_suffix:{term}^0.75 "
            f"OR default:{term} OR body_text:{term} OR SearchableText:{term} "
            f"OR Subject:{term} OR searchwords:({term})^1000) "
            "-showinsearch:False"
        )

    def test_filters(self, conn):
        params = self.fake_search(conn)
        assert SECURITY_FQ in params["fq"]
        assert "-is_rag_chunk:true" in params["fq"]

    def test_question_is_escaped(self, conn):
        conn.search.return_value = mock.Mock()
        with mock.patch.object(pipeline_module, "SolrResponse") as solr_response:
            solr_response.return_value.results.return_value = []
            search_keyword(conn, 'evil" OR *:*', SECURITY_FQ)
        query = conn.search.call_args.kwargs["q"]
        assert '"' not in query.split("Title:")[1].split("^")[0].replace('\\"', "")
