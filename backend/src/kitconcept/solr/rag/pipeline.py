"""The RAG query pipeline: question -> retrieved chunks -> answer.

Implements the single-turn RAG search (SPECIFICATION-79.md §4) with
hybrid retrieval:

1. embed the user's question (``search_query:`` prefix),
2. retrieve the top chunks via a ``{!knn}`` query — the existing
   security/path/language filter queries compose with the vector query
   as HNSW pre-filters, so permission trimming works unchanged,
3. retrieve the top parent documents via the classic keyword (BM25)
   query and fuse both rankings with client-side Reciprocal Rank
   Fusion — hybrid is the industry default because keyword and vector
   search have complementary failure modes (exact names/codes vs.
   paraphrase). Solr's native RRF lands in 9.11/10.1; the client-side
   fusion is drop-in replaceable by it,
4. assemble the context chunks for the fused parent ranking (chunks
   from the knn hits; fetched from Solr for keyword-only parents),
5. generate the answer with the general-purpose model, prompted with
   the chunk texts (chunk-level context, decision 9) and constrained
   to the provided context.

Fusion happens at the *parent document* level: chunks are invisible to
keyword search by design (their text is stored but not indexed), so
BM25 ranks parents, while the chunk hits of the knn side are collapsed
to their parents (parent-document retrieval).

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
from kitconcept.solr.rag.config import RETRIEVAL_HYBRID
from kitconcept.solr.rag.config import RRF_K
from kitconcept.solr.rag.config import TOP_K
from kitconcept.solr.rag.prompt import build_prompt
from kitconcept.solr.rag.prompt import strip_thinking
from kitconcept.solr.rag.prompt import SYSTEM_PROMPT
from kitconcept.solr.services.solr_utils import escape
from kitconcept.solr.services.solr_utils import replace_reserved
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
    extra_filters: list[str] | None = None,
) -> RagResult:
    """Run the single-turn RAG search pipeline.

    :param question: The user's natural language question.
    :param config: Resolved RAG configuration.
    :param security_filter: The allowedRolesAndUsers filter query for
        the current user (from ``services.solr.security_filter``).
    :param path_prefix: Optional path to restrict the search to.
    :param lang: Optional language to restrict the search to.
    :param extra_filters: Optional pre-built filter queries (from the
        extra_conditions request parameter - the search dialog's
        filter chips). Applied to both retrieval legs: the chunk
        documents carry the denormalized type/creator/date/state of
        their parent, the keyword leg matches parent documents
        directly.
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
        chunks = search_chunks(
            conn, vector, security_filter, path_prefix, lang, extra_filters
        )
        knn_parents = parent_ranking(chunks)
        if config.retrieval == RETRIEVAL_HYBRID:
            keyword_parents = search_keyword(
                conn, question, security_filter, path_prefix, lang, extra_filters
            )
            fused_parents = rrf_fuse([knn_parents, keyword_parents])
        else:
            fused_parents = knn_parents
        fused_parents = fused_parents[:TOP_K]
        if not fused_parents:
            # No matching (visible) content: not an error - the answer is
            # that there is no answer.
            return RagResult()
        context_chunks = assemble_context(conn, chunks, fused_parents)
        sources = build_sources(conn, fused_parents, context_chunks)
    except (SolrConnectionException, OSError) as e:
        # collective.solr raises raw socket errors (e.g.
        # ConnectionRefusedError) when the Solr server is down
        logger.warning("rag-search: Solr unavailable: %s", e)
        return RagResult.failure(ERROR_SOLR_UNAVAILABLE, str(e))

    prompt = build_prompt(question, context_chunks)
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
    extra_filters: list[str] | None = None,
) -> list[dict]:
    """Top-K chunk hits for the query vector, permission trimmed."""
    filter_queries = [security_filter, "is_rag_chunk:true"]
    if extra_filters:
        filter_queries.extend(extra_filters)
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


def search_keyword(
    conn,
    question: str,
    security_filter: str,
    path_prefix: str | None = None,
    lang: str | None = None,
    extra_filters: list[str] | None = None,
) -> list[str]:
    """Top-K parent documents for the classic keyword (BM25) query.

    The scoring expression is an exact copy of the ``@solr`` main
    query (``SolrSearch._base_query``): same fields, same boosts —
    including ``searchwords^1000`` (the editorial "pin a document for
    a keyword" mechanism) and the ``-showinsearch:False`` exclusion,
    both of which must behave identically in the AI search. Notes:

    - ``id^0.75``: kept for parity; whether id matching makes sense
      for natural language questions may be revisited.
    - ``text_prefix``/``text_suffix^0.75``: likely unneeded for full
      NL questions (they serve terse/partial-word queries), but
      included for exact parity since their low boosts don't disturb
      the ranking; may be revisited.

    Not inherited (deliberately): facet/search-tab conditions,
    highlighting, spellcheck, pagination — request-driven UI machinery
    of the classic search page that has no meaning here and does not
    affect the ranking. Extracting a shared query builder so the copy
    cannot drift is a planned refactoring (see the overflow list).

    Chunks are excluded — they carry no indexed text anyway.
    """
    term = f"({escape(replace_reserved(question))})"
    query = (
        f"+(Title:{term}^5 OR Description:{term}^2 OR id:{term}^0.75 "
        f"OR text_prefix:{term}^0.75 OR text_suffix:{term}^0.75 "
        f"OR default:{term} OR body_text:{term} OR SearchableText:{term} "
        f"OR Subject:{term} OR searchwords:({term})^1000) -showinsearch:False"
    )
    filter_queries = [security_filter, "-is_rag_chunk:true"]
    if extra_filters:
        filter_queries.extend(extra_filters)
    if path_prefix:
        portal_path = "/".join(api.portal.get().getPhysicalPath())
        prefix = portal_path + path_prefix.rstrip("/")
        filter_queries.append(f'path_parents:"{prefix}"')
    if lang:
        filter_queries.append(f"Language:({lang} OR any)")
    response = conn.search(
        q=query,
        fq=filter_queries,
        fl="UID",
        rows=TOP_K,
    )
    try:
        results = SolrResponse(response).results()
    finally:
        response.close()
    return [flare["UID"] for flare in results]


def parent_ranking(chunks: list[dict]) -> list[str]:
    """Parent UIDs of the chunk hits, deduplicated, in rank order."""
    order: list[str] = []
    seen = set()
    for chunk in chunks:
        parent_uid = chunk.get("parent_uid")
        if parent_uid and parent_uid not in seen:
            seen.add(parent_uid)
            order.append(parent_uid)
    return order


def rrf_fuse(rankings: list[list[str]], k: int = RRF_K) -> list[str]:
    """Reciprocal Rank Fusion of ranked UID lists.

    ``score(d) = sum over rankings of 1 / (k + rank(d))`` — the
    standard fusion that needs no score normalization (Cormack et al.
    2009). Ties keep the order of the first ranking.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for index, uid in enumerate(ranking):
            scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + index + 1)
    return sorted(scores, key=lambda uid: -scores[uid])


def assemble_context(
    conn, knn_chunks: list[dict], fused_parents: list[str]
) -> list[dict]:
    """Context chunks for the fused parent ranking, capped at TOP_K.

    Chunks retrieved by the knn query are used as-is; for parents that
    only the keyword ranking surfaced, the leading chunks are fetched
    from Solr — their text must reach the model, otherwise a document
    found by keyword search could not contribute to the answer.
    """
    by_parent: dict[str, list[dict]] = {}
    for chunk in knn_chunks:
        by_parent.setdefault(chunk.get("parent_uid"), []).append(chunk)
    context: list[dict] = []
    for parent_uid in fused_parents:
        if parent_uid in by_parent:
            context.extend(by_parent[parent_uid])
        else:
            context.extend(fetch_leading_chunks(conn, parent_uid))
        if len(context) >= TOP_K:
            break
    return context[:TOP_K]


def fetch_leading_chunks(conn, parent_uid: str, limit: int = 2) -> list[dict]:
    """The first chunks of a document (for keyword-only parents)."""
    response = conn.search(
        q=f'+parent_uid:"{parent_uid}" +is_rag_chunk:true',
        sort="chunk_index asc",
        fl=CHUNK_FIELD_LIST,
        rows=limit,
    )
    try:
        return list(SolrResponse(response).results())
    finally:
        response.close()


def build_sources(
    conn, fused_parents: list[str], context_chunks: list[dict]
) -> list[dict]:
    """Source documents in fused rank order.

    Parent-document retrieval: the user sees the parent documents as
    the sources. Parent metadata is fetched from Solr in one query and
    merged with a snippet from the best-ranked context chunk of each
    parent (empty when a parent contributed no context).
    """
    best_chunk: dict[str, dict] = {}
    for chunk in context_chunks:
        best_chunk.setdefault(chunk.get("parent_uid"), chunk)
    parents = fetch_parents(conn, fused_parents)

    portal = api.portal.get()
    portal_path = "/".join(portal.getPhysicalPath())
    portal_url = portal.absolute_url()

    sources = []
    for parent_uid in fused_parents:
        parent = parents.get(parent_uid, {})
        chunk = best_chunk.get(parent_uid, {})
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
