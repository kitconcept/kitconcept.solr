"""The RAG query pipeline: question -> retrieved chunks -> answer.

Implements the single-turn RAG search (SPECIFICATION-79.md §4):

1. embed the user's question (``search_query:`` prefix),
2. retrieve the top chunks via a ``{!knn}`` query — the existing
   security/path/language filter queries compose with the vector query
   as HNSW pre-filters, so permission trimming works unchanged,
3. collapse the chunk hits to their parent documents (the sources),
4. generate the answer with the general-purpose model, prompted with
   the matched chunk texts (chunk-level context, decision 9) and
   constrained to the provided context.

The pipeline is independent of the REST service so it can be tested
with a faked Solr connection and LLM client, and reused (e.g. by a
future evaluation harness).
"""

from collective.solr.exceptions import SolrConnectionException
from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.parser import SolrResponse
from dataclasses import dataclass
from dataclasses import field
from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import RagConfig
from kitconcept.solr.rag.config import TOP_K
from kitconcept.solr.rag.prompt import build_prompt
from kitconcept.solr.rag.prompt import strip_thinking
from kitconcept.solr.rag.prompt import SYSTEM_PROMPT
from plone import api
from zope.component import queryUtility

import logging


logger = logging.getLogger("kitconcept.solr.rag")

# Error codes for structured error reporting (the frontend degrades
# gracefully based on these; the message is for humans/logs).
ERROR_NOT_CONFIGURED = "not_configured"
ERROR_EMBEDDING_FAILED = "embedding_failed"
ERROR_GENERATION_FAILED = "generation_failed"
ERROR_SOLR_UNAVAILABLE = "solr_unavailable"

CHUNK_FIELD_LIST = "UID,parent_uid,parent_title,chunk_text,path_string,score"
SOURCE_FIELD_LIST = "UID,Title,Description,Type,path_string"
SNIPPET_LENGTH = 300


@dataclass
class RagResult:
    answer: str | None = None
    sources: list = field(default_factory=list)
    error: str | None = None
    error_code: str | None = None

    @classmethod
    def failure(cls, code: str, message: str) -> "RagResult":
        return cls(error=message, error_code=code)


def run_rag_search(
    question: str,
    config: RagConfig,
    security_filter: str,
    path_prefix: str | None = None,
    lang: str | None = None,
) -> RagResult:
    """Run the single-turn RAG search pipeline.

    :param question: The user's natural language question.
    :param config: Resolved RAG configuration.
    :param security_filter: The allowedRolesAndUsers filter query for
        the current user (from ``services.solr.security_filter``).
    :param path_prefix: Optional path to restrict the search to.
    :param lang: Optional language to restrict the search to.
    """
    client = LLMClient(config)
    try:
        vector = client.embed_query(question)
    except LLMClientError as e:
        logger.warning("rag-search: embedding failed: %s", e)
        return RagResult.failure(ERROR_EMBEDDING_FAILED, str(e))

    conn = get_connection()
    if conn is None:
        return RagResult.failure(
            ERROR_SOLR_UNAVAILABLE, "no Solr connection (solr inactive?)"
        )
    try:
        chunks = search_chunks(conn, vector, security_filter, path_prefix, lang)
        sources = collapse_sources(conn, chunks) if chunks else []
    except (SolrConnectionException, OSError) as e:
        # collective.solr raises raw socket errors (e.g.
        # ConnectionRefusedError) when the Solr server is down
        logger.warning("rag-search: Solr unavailable: %s", e)
        return RagResult.failure(ERROR_SOLR_UNAVAILABLE, str(e))
    if not chunks:
        # No matching (visible) content: not an error - the answer is
        # that there is no answer.
        return RagResult()

    prompt = build_prompt(question, chunks)
    try:
        answer = client.chat(prompt, system=SYSTEM_PROMPT)
    except LLMClientError as e:
        logger.warning("rag-search: generation failed: %s", e)
        result = RagResult.failure(ERROR_GENERATION_FAILED, str(e))
        result.sources = sources  # retrieval worked; expose the sources
        return result
    return RagResult(answer=strip_thinking(answer), sources=sources)


def get_connection():
    manager = queryUtility(ISolrConnectionManager)
    return manager.getConnection() if manager is not None else None


def format_vector(vector: list[float]) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in vector) + "]"


def search_chunks(
    conn,
    vector: list[float],
    security_filter: str,
    path_prefix: str | None = None,
    lang: str | None = None,
) -> list[dict]:
    """Top-K chunk hits for the query vector, permission trimmed."""
    filter_queries = [security_filter, "is_rag_chunk:true"]
    if path_prefix:
        portal_path = "/".join(api.portal.get().getPhysicalPath())
        prefix = portal_path + path_prefix.rstrip("/")
        filter_queries.append(f'path_parents:"{prefix}"')
    if lang:
        filter_queries.append(f"Language:({lang} OR any)")
    response = conn.search(
        q=f"{{!knn f=content_vector topK={TOP_K}}}{format_vector(vector)}",
        fq=filter_queries,
        fl=CHUNK_FIELD_LIST,
        rows=TOP_K,
    )
    try:
        return list(SolrResponse(response).results())
    finally:
        response.close()


def collapse_sources(conn, chunks: list[dict]) -> list[dict]:
    """Parent documents of the matched chunks, in rank order.

    Parent-document retrieval: retrieval matches chunks, but the user
    sees the parent documents as the sources. Parent metadata is
    fetched from Solr in one query and merged with a snippet from the
    best-ranked chunk of each parent.
    """
    order: list[str] = []
    best_chunk: dict[str, dict] = {}
    for chunk in chunks:
        parent_uid = chunk.get("parent_uid")
        if not parent_uid:
            continue
        if parent_uid not in best_chunk:
            order.append(parent_uid)
            best_chunk[parent_uid] = chunk
    if not order:
        return []
    parents = fetch_parents(conn, order)

    portal = api.portal.get()
    portal_path = "/".join(portal.getPhysicalPath())
    portal_url = portal.absolute_url()

    sources = []
    for parent_uid in order:
        parent = parents.get(parent_uid, {})
        chunk = best_chunk[parent_uid]
        path_string = parent.get("path_string") or chunk.get("path_string", "")
        url = (
            portal_url + path_string[len(portal_path) :]
            if path_string.startswith(portal_path)
            else path_string
        )
        sources.append({
            "@id": url,
            "UID": parent_uid,
            "@type": parent.get("Type", ""),
            "title": parent.get("Title") or chunk.get("parent_title", ""),
            "description": parent.get("Description", ""),
            "snippet": chunk.get("chunk_text", "")[:SNIPPET_LENGTH],
        })
    return sources


def fetch_parents(conn, uids: list[str]) -> dict[str, dict]:
    """Metadata of the parent documents, keyed by UID."""
    query = " OR ".join(f'"{uid}"' for uid in uids)
    response = conn.search(
        q=f"UID:({query})",
        fl=SOURCE_FIELD_LIST,
        rows=len(uids),
    )
    try:
        results = SolrResponse(response).results()
    finally:
        response.close()
    return {flare["UID"]: flare for flare in results}
