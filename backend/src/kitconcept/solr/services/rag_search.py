"""The @rag-search REST endpoint: single-turn RAG search.

Question in, answer + source documents out (SPECIFICATION-79.md §4).
Thin HTTP layer over ``kitconcept.solr.rag.pipeline``; errors are
reported structurally (``error`` message + ``error_code``) so the
frontend can degrade gracefully to the classic search.
"""

from kitconcept.solr.rag.config import get_rag_config
from kitconcept.solr.rag.pipeline import ERROR_NOT_CONFIGURED
from kitconcept.solr.rag.pipeline import RagResult
from kitconcept.solr.rag.pipeline import run_rag_search
from kitconcept.solr.services.solr import security_filter
from kitconcept.solr.services.solr_utils_extra import SolrExtraConditions
from plone.restapi.services import Service
from zExceptions import BadRequest


class RagSearch(Service):
    """Single-turn RAG search: question -> answer + sources."""

    def reply(self):
        question = self.request.form.get("q", "").strip()
        if not question:
            raise BadRequest("Missing parameter: q")
        path_prefix = self.request.form.get("path_prefix", "").strip() or None
        lang = self.request.form.get("lang", "").strip() or None
        # Same filter mechanism and encoding as the @solr and
        # @solr-suggest endpoints (search dialog filter chips): the
        # conditions restrict what the answer may be grounded on.
        extra_filters = SolrExtraConditions.from_encoded(
            self.request.form.get("extra_conditions")
        ).query_list()

        config = get_rag_config()
        if config is None:
            result = RagResult.failure(
                ERROR_NOT_CONFIGURED, "RAG is not enabled or not configured"
            )
        else:
            result = run_rag_search(
                question,
                config,
                security_filter(),
                path_prefix=path_prefix,
                lang=lang,
                extra_filters=extra_filters or None,
            )
        return {
            "answer": result.answer,
            "sources": result.sources,
            "error": result.error,
            "error_code": result.error_code,
        }
