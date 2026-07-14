"""Minimal @rag-search endpoint for local testing (RAG: TESTING).

Rough draft of the RAG query pipeline (retrieval endpoint + answer
generation, internal ticket 458), added ahead of time so the feature
can be exercised from the site. To be replaced by the proper
implementation; kept deliberately simple.
"""

from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.parser import SolrResponse
from kitconcept.solr.rag.client import LLMClient
from kitconcept.solr.rag.client import LLMClientError
from kitconcept.solr.rag.config import get_rag_config
from kitconcept.solr.services.solr import security_filter
from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryUtility

import logging
import re


logger = logging.getLogger("kitconcept.solr.rag")

TOP_K = 5

SYSTEM_PROMPT = (
    "You are the search assistant of an intranet site. Answer the"
    " user's question based only on the provided context documents."
    " If the answer is not contained in them, say that you could not"
    " find the answer in the documentation. Answer in the language of"
    " the question. Be concise: one or two short paragraphs."
)

PROMPT_TEMPLATE = (
    "Context documents:\n\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer the question based only on the context documents above."
)

# qwen3 may emit a thinking block; never show it to the user.
THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


class RagSearch(Service):
    """Single-turn RAG search: question -> answer + sources."""

    def reply(self):
        question = self.request.form.get("q", "").strip()
        if not question:
            raise BadRequest("Missing parameter: q")
        config = get_rag_config()
        if config is None:
            return self._error("RAG is not enabled or not configured")
        client = LLMClient(config)
        try:
            vector = client.embed_query(question)
        except LLMClientError as e:
            logger.warning("rag-search: embedding failed: %s", e)
            return self._error(f"embedding failed: {e}")
        chunks = self._search_chunks(vector)
        if not chunks:
            return {"answer": None, "sources": [], "error": None}
        prompt = self._build_prompt(question, chunks)
        sources = self._sources(chunks)
        try:
            answer = client.chat(prompt, system=SYSTEM_PROMPT)
        except LLMClientError as e:
            logger.warning("rag-search: generation failed: %s", e)
            return {
                "answer": None,
                "sources": sources,
                "error": f"answer generation failed: {e}",
            }
        answer = THINK_RE.sub("", answer).strip()
        return {"answer": answer, "sources": sources, "error": None}

    def _error(self, message):
        return {"answer": None, "sources": [], "error": message}

    def _search_chunks(self, vector) -> list[dict]:
        manager = queryUtility(ISolrConnectionManager)
        conn = manager.getConnection() if manager is not None else None
        if conn is None:
            return []
        vector_str = "[" + ",".join(f"{x:.8f}" for x in vector) + "]"
        response = conn.search(
            q=f"{{!knn f=content_vector topK={TOP_K}}}{vector_str}",
            fq=[security_filter(), "is_rag_chunk:true"],
            fl="UID,parent_uid,parent_title,chunk_text,path_string,score",
            rows=TOP_K,
        )
        try:
            return list(SolrResponse(response).results())
        finally:
            response.close()

    def _build_prompt(self, question, chunks) -> str:
        parts = []
        for index, chunk in enumerate(chunks, start=1):
            title = chunk.get("parent_title", "")
            text = chunk.get("chunk_text", "")
            parts.append(f"[{index}] {title}\n{text}")
        return PROMPT_TEMPLATE.format(context="\n\n".join(parts), question=question)

    def _sources(self, chunks) -> list[dict]:
        """Parent documents of the matched chunks, in rank order."""
        portal = api.portal.get()
        portal_path = "/".join(portal.getPhysicalPath())
        portal_url = portal.absolute_url()
        seen = set()
        sources = []
        for chunk in chunks:
            parent_uid = chunk.get("parent_uid")
            if not parent_uid or parent_uid in seen:
                continue
            seen.add(parent_uid)
            path_string = chunk.get("path_string", "")
            url = (
                portal_url + path_string[len(portal_path) :]
                if path_string.startswith(portal_path)
                else path_string
            )
            sources.append({
                "@id": url,
                "UID": parent_uid,
                "title": chunk.get("parent_title", ""),
                "snippet": chunk.get("chunk_text", "")[:300],
            })
        return sources
