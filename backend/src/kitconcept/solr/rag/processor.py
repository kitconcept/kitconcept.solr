"""Indexing queue processor that maintains RAG chunk documents.

Registered as an ``IIndexQueueProcessor`` utility next to
collective.solr's own processor, so it receives the same
index/reindex/unindex calls from the Plone indexing queue and writes
chunk sibling documents (see the schema comment on ``is_rag_chunk``)
over the same Solr connection.

Design decisions (see IMPLEMENTATION-79.md):

- Embedding is synchronous with a short timeout; an embedding failure
  logs a warning and leaves the previously indexed chunks in place —
  a content save must never fail or lose search because the LLM stack
  is down.
- A reindex limited to attributes that don't affect the extracted text
  only updates the denormalized chunk metadata (security, language,
  path) in place via Solr atomic updates — no re-embedding e.g. on a
  workflow transition.
- Chunk cleanup on unindex is gated only on the registry toggle (not
  on the endpoint configuration), so chunks written earlier are still
  cleaned up while the endpoint is unconfigured.
"""

from collective.solr.indexer import SolrIndexProcessor
from collective.solr.interfaces import ICheckIndexable
from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.parser import SolrResponse
from collective.solr.utils import prepareData
from kitconcept.solr.rag.chunker import chunk_segments
from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import get_rag_config
from kitconcept.solr.rag.config import rag_enabled
from kitconcept.solr.rag.extraction import extract_segments
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import IIndexQueueProcessor
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer

import logging


logger = logging.getLogger("kitconcept.solr.rag")

# Attribute reindexes intersecting this set require re-chunking and
# re-embedding.
TEXT_ATTRIBUTES = frozenset({"SearchableText", "Title", "Description"})
# Attribute reindexes intersecting this set update the denormalized
# chunk metadata in place (no re-embedding).
METADATA_ATTRIBUTES = frozenset({
    "allowedRolesAndUsers",
    "Language",
    "path",
    "path_string",
    "path_parents",
    "path_depth",
})
# Parent fields denormalized onto every chunk document.
PARENT_DATA_ATTRIBUTES = [
    "Title",
    "allowedRolesAndUsers",
    "Language",
    "path_string",
    "path_parents",
    "path_depth",
]
# Safety cap against pathological documents: at ~400 tokens per chunk
# this covers roughly 40k tokens of text per document.
MAX_CHUNKS_PER_DOCUMENT = 100

# Content types excluded from chunking. An Image's only chunkable text
# is its title/description - metadata about an illustration, not
# knowledge - and it pollutes answer sources (a photo cited as a
# source). File stays included: its title/description locates real
# documents (and the post-MVP Tika body text will build on it).
EXCLUDED_PORTAL_TYPES = frozenset({"Image"})


def chunk_uid(uid: str, index: int) -> str:
    return f"{uid}#rag-{index}"


def chunk_query(uid: str) -> str:
    return f'+parent_uid:"{uid}" +is_rag_chunk:true'


@implementer(IIndexQueueProcessor)
class RagIndexProcessor:
    """Maintain RAG chunk documents alongside regular Solr indexing."""

    def __init__(self, manager=None):
        self.manager = manager

    def _get_manager(self):
        return self.manager or queryUtility(ISolrConnectionManager)

    def _connection(self):
        manager = self._get_manager()
        if manager is None:
            return None, None
        # Returns None while collective.solr is inactive.
        return manager, manager.getConnection()

    def _commit_within(self):
        registry = getUtility(IRegistry)
        return registry["collective.solr.commit_within"]

    def _parent_data(self, obj, manager) -> dict:
        """Parent field values, mangled the way Solr expects them."""
        proc = SolrIndexProcessor(manager)
        data, _missing = proc.getData(obj, attributes=PARENT_DATA_ATTRIBUTES)
        prepareData(data)
        return data

    def _chunk_uids(self, conn, uid: str) -> list[str]:
        """UIDs of the currently indexed chunks of a parent document."""
        response = conn.search(
            q=chunk_query(uid),
            fl="UID",
            rows=MAX_CHUNKS_PER_DOCUMENT * 2,
        )
        try:
            results = SolrResponse(response).results()
        finally:
            response.close()
        return [flare["UID"] for flare in results]

    # IIndexQueueProcessor

    def index(self, obj, attributes=None):
        config = get_rag_config()
        if config is None:
            return
        if not ICheckIndexable(obj)():
            return
        uid = IUUID(obj, None)
        if uid is None:
            return
        manager, conn = self._connection()
        if conn is None:
            return
        if getattr(obj, "portal_type", None) in EXCLUDED_PORTAL_TYPES:
            # also drop chunks indexed before the type was excluded
            conn.deleteByQuery(chunk_query(uid))
            return
        if attributes is not None:
            attributes = set(attributes)
            if attributes & TEXT_ATTRIBUTES:
                pass  # text changed: full rebuild below
            elif attributes & METADATA_ATTRIBUTES:
                self._update_chunk_metadata(obj, uid, manager, conn)
                return
            else:
                return  # nothing relevant for the chunks changed
        self._rebuild_chunks(obj, uid, config, manager, conn)

    def reindex(self, obj, attributes=None, update_metadata=False):
        if not attributes:
            attributes = None
        self.index(obj, attributes)

    def unindex(self, obj):
        # Gate on the toggle only: cleanup must work without the
        # endpoint being configured.
        if not rag_enabled():
            return
        # remove the PathWrapper (see SolrIndexProcessor.unindex)
        if hasattr(obj, "context"):
            obj = obj.context
        uid = IUUID(obj, None)
        if uid is None:
            return
        _manager, conn = self._connection()
        if conn is None:
            return
        conn.deleteByQuery(chunk_query(uid))

    def begin(self):
        pass

    def commit(self, wait=None):
        # The shared connection is committed by collective.solr's own
        # queue processor (or by commitWithin on our updates).
        pass

    def abort(self):
        pass

    # internal

    def _rebuild_chunks(self, obj, uid, config, manager, conn):
        segments = extract_segments(obj)
        chunks = chunk_segments(segments)
        if len(chunks) > MAX_CHUNKS_PER_DOCUMENT:
            logger.warning(
                "%s: truncating %d chunks to %d",
                uid,
                len(chunks),
                MAX_CHUNKS_PER_DOCUMENT,
            )
            chunks = chunks[:MAX_CHUNKS_PER_DOCUMENT]
        try:
            vectors = LLMClient(config).embed_documents(chunks) if chunks else []
        except LLMClientError as e:
            # Never fail (or lose chunks) on an unavailable LLM stack:
            # keep whatever chunks are currently indexed.
            logger.warning("%s: embedding failed, keeping existing chunks: %s", uid, e)
            return
        parent = self._parent_data(obj, manager)
        commit_within = self._commit_within()
        # Delete first: the number of chunks may have shrunk.
        conn.deleteByQuery(chunk_query(uid))
        for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            data = {
                "UID": chunk_uid(uid, index),
                "is_rag_chunk": "true",
                "parent_uid": uid,
                "chunk_index": index,
                "chunk_text": chunk,
                "parent_title": parent.get("Title", ""),
                "rag_embedding_model": config.embed_model,
                "content_vector": vector,
            }
            for name in PARENT_DATA_ATTRIBUTES:
                if name != "Title" and name in parent:
                    data[name] = parent[name]
            if commit_within:
                data["commitWithin"] = commit_within
            conn.add(**data)
        logger.debug("%s: indexed %d chunks", uid, len(chunks))

    def _update_chunk_metadata(self, obj, uid, manager, conn):
        """Update denormalized fields on existing chunks in place."""
        parent = self._parent_data(obj, manager)
        commit_within = self._commit_within()
        for existing_uid in self._chunk_uids(conn, uid):
            data = {"UID": existing_uid}
            for name in PARENT_DATA_ATTRIBUTES:
                if name != "Title" and name in parent:
                    data[name] = parent[name]
            if commit_within:
                data["commitWithin"] = commit_within
            # conn.add issues per-field update="set" operations, so
            # this is an atomic update of the metadata fields only.
            conn.add(**data)
