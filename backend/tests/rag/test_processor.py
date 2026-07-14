from kitconcept.solr.rag import processor as processor_module
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.processor import chunk_query
from kitconcept.solr.rag.processor import chunk_uid
from kitconcept.solr.rag.processor import RagIndexProcessor
from unittest import mock

import pytest


UID = "abcd1234"

CONFIG = RagConfig(
    base_url="http://llm.example.com",
    token=None,
    embed_model="test-embed",
    chat_model="test-chat",
)

PARENT_DATA = {
    "Title": "A document",
    "allowedRolesAndUsers": ["Anonymous"],
    "Language": "en",
    "path_string": "/plone/a-document",
    "path_parents": ["/plone", "/plone/a-document"],
    "path_depth": 2,
}


class FakeConnection:
    def __init__(self):
        self.added = []
        self.deleted_queries = []

    def add(self, **fields):
        self.added.append(fields)

    def deleteByQuery(self, query):
        self.deleted_queries.append(query)


class FakeContextProcessor(RagIndexProcessor):
    """Processor with the Zope/Solr context faked out for unit tests."""

    def __init__(self, conn, parent_data=PARENT_DATA, commit_within=None):
        super().__init__(manager=mock.Mock())
        self._conn = conn
        self._parent = parent_data
        self._within = commit_within
        self.existing_chunk_uids = []

    def _connection(self):
        return self.manager, self._conn

    def _parent_data(self, obj, manager):
        return dict(self._parent)

    def _commit_within(self):
        return self._within

    def _chunk_uids(self, conn, uid):
        return self.existing_chunk_uids


@pytest.fixture
def conn():
    return FakeConnection()


@pytest.fixture
def proc(conn):
    return FakeContextProcessor(conn)


@pytest.fixture
def obj():
    """A content object double passing ICheckIndexable and IUUID."""
    fake = mock.Mock()
    fake.Title.return_value = "A document"
    fake.Description.return_value = "About something."
    return fake


@pytest.fixture(autouse=True)
def environment(obj):
    """Enabled config, indexable object, deterministic embeddings."""
    with (
        mock.patch.object(processor_module, "get_rag_config", return_value=CONFIG),
        mock.patch.object(processor_module, "rag_enabled", return_value=True),
        mock.patch.object(
            processor_module, "ICheckIndexable", return_value=lambda: True
        ),
        mock.patch.object(processor_module, "IUUID", return_value=UID),
        mock.patch.object(
            processor_module,
            "extract_segments",
            return_value=["A document", "About something."],
        ),
        mock.patch.object(processor_module, "LLMClient") as llm_class,
    ):
        llm_class.return_value.embed_documents.side_effect = lambda chunks: [
            [0.1, 0.2] for _ in chunks
        ]
        yield llm_class


class TestIndexRebuild:
    def test_deletes_then_adds_chunks(self, proc, conn, obj):
        proc.index(obj)
        assert conn.deleted_queries == [chunk_query(UID)]
        assert len(conn.added) == 1  # short text: one chunk
        doc = conn.added[0]
        assert doc["UID"] == chunk_uid(UID, 0)
        assert doc["is_rag_chunk"] == "true"
        assert doc["parent_uid"] == UID
        assert doc["chunk_index"] == 0
        assert doc["chunk_text"] == "A document About something."
        assert doc["parent_title"] == "A document"
        assert doc["rag_embedding_model"] == "test-embed"
        assert doc["content_vector"] == [0.1, 0.2]

    def test_denormalizes_security_language_path(self, proc, conn, obj):
        proc.index(obj)
        doc = conn.added[0]
        assert doc["allowedRolesAndUsers"] == ["Anonymous"]
        assert doc["Language"] == "en"
        assert doc["path_string"] == "/plone/a-document"
        assert doc["path_parents"] == ["/plone", "/plone/a-document"]
        assert doc["path_depth"] == 2

    def test_commit_within_is_propagated(self, conn, obj):
        proc = FakeContextProcessor(conn, commit_within=10000)
        proc.index(obj)
        assert conn.added[0]["commitWithin"] == 10000

    def test_disabled_config_is_a_noop(self, proc, conn, obj):
        with mock.patch.object(processor_module, "get_rag_config", return_value=None):
            proc.index(obj)
        assert conn.added == []
        assert conn.deleted_queries == []

    def test_no_connection_is_a_noop(self, conn, obj):
        proc = FakeContextProcessor(conn)
        proc._connection = lambda: (None, None)
        proc.index(obj)
        assert conn.added == []

    def test_embedding_failure_keeps_existing_chunks(
        self, proc, conn, obj, environment
    ):
        environment.return_value.embed_documents.side_effect = LLMClientError("down")
        proc.index(obj)
        # neither deleted nor re-added: previously indexed chunks stay
        assert conn.deleted_queries == []
        assert conn.added == []

    def test_empty_text_deletes_stale_chunks(self, proc, conn, obj):
        with mock.patch.object(processor_module, "extract_segments", return_value=[]):
            proc.index(obj)
        assert conn.deleted_queries == [chunk_query(UID)]
        assert conn.added == []

    def test_chunk_cap(self, proc, conn, obj):
        many = [f"Paragraph {i}. " + "word " * 400 for i in range(300)]
        with mock.patch.object(processor_module, "extract_segments", return_value=many):
            proc.index(obj)
        assert len(conn.added) == processor_module.MAX_CHUNKS_PER_DOCUMENT


class TestReindexAttributes:
    def test_irrelevant_attributes_are_a_noop(self, proc, conn, obj):
        proc.reindex(obj, attributes=["getObjPositionInParent"])
        assert conn.added == []
        assert conn.deleted_queries == []

    def test_text_attribute_triggers_rebuild(self, proc, conn, obj):
        proc.reindex(obj, attributes=["SearchableText"])
        assert conn.deleted_queries == [chunk_query(UID)]
        assert len(conn.added) == 1

    def test_security_attribute_updates_metadata_in_place(self, proc, conn, obj):
        proc.existing_chunk_uids = [chunk_uid(UID, 0), chunk_uid(UID, 1)]
        proc.reindex(obj, attributes=["allowedRolesAndUsers"])
        # no delete, no re-embedding: atomic updates on existing chunks
        assert conn.deleted_queries == []
        assert len(conn.added) == 2
        for doc in conn.added:
            assert doc["allowedRolesAndUsers"] == ["Anonymous"]
            assert "content_vector" not in doc
            assert "chunk_text" not in doc

    def test_empty_attributes_means_full_rebuild(self, proc, conn, obj):
        proc.reindex(obj, attributes=[])
        assert conn.deleted_queries == [chunk_query(UID)]


class TestUnindex:
    def test_deletes_chunks(self, proc, conn, obj):
        proc.unindex(obj)
        assert conn.deleted_queries == [chunk_query(UID)]

    def test_gated_on_toggle_not_endpoint(self, proc, conn, obj):
        # endpoint unconfigured, toggle on: cleanup still works
        with mock.patch.object(processor_module, "get_rag_config", return_value=None):
            proc.unindex(obj)
        assert conn.deleted_queries == [chunk_query(UID)]

    def test_toggle_off_is_a_noop(self, proc, conn, obj):
        with mock.patch.object(processor_module, "rag_enabled", return_value=False):
            proc.unindex(obj)
        assert conn.deleted_queries == []
