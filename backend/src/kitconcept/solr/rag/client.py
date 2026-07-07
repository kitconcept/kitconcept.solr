"""HTTP client for the LLM server.

Two endpoints are used (SPECIFICATION-79.md §3), with paths matching
the kitconcept LLM server (Open WebUI in front of Ollama) whose API
key allowlist permits exactly these two:

- embeddings: Ollama-compatible ``POST <root>/ollama/api/embed`` —
  batched, returns L2-normalized vectors. The nomic models require
  task prefixes: content is embedded as ``search_document: ...`` and
  queries as ``search_query: ...``; skipping them measurably degrades
  retrieval.
- chat: OpenAI-compatible ``POST <root>/api/chat/completions`` —
  answer generation (used by the query pipeline).

Both paths are configurable (see ``config``), e.g. for a plain Ollama
server during local development.

Embeddings are computed here on the Plone side rather than via Solr's
LLM module, because that module does not support Ollama as a provider
and cannot add the task prefixes.

The client is deliberately a thin ``requests`` wrapper: explicit
timeouts, typed errors, no third-party LLM framework dependency.
"""

from kitconcept.solr.rag.config import EMBED_BATCH_SIZE
from kitconcept.solr.rag.config import EMBED_TOKEN_LIMIT
from kitconcept.solr.rag.config import estimate_tokens
from kitconcept.solr.rag.config import RagConfig

import logging
import requests


logger = logging.getLogger("kitconcept.solr.rag")

SEARCH_DOCUMENT_PREFIX = "search_document: "
SEARCH_QUERY_PREFIX = "search_query: "


class LLMClientError(Exception):
    """Base error talking to the LLM server."""


class LLMTimeout(LLMClientError):
    """The LLM server did not answer within the timeout."""


class LLMResponseError(LLMClientError):
    """The LLM server answered, but not with what we expected."""


class LLMClient:
    """Client for the embedding and generation endpoints."""

    def __init__(self, config: RagConfig):
        self.config = config

    def _post(self, path: str, payload: dict, timeout: float) -> dict:
        url = f"{self.config.base_url}{path}"
        headers = {}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=timeout
            )
        except requests.Timeout as e:
            raise LLMTimeout(f"timeout after {timeout}s calling {path}") from e
        except requests.RequestException as e:
            raise LLMClientError(f"error calling {path}: {e}") from e
        if response.status_code != 200:
            raise LLMResponseError(
                f"{path} returned {response.status_code}: {response.text[:200]}"
            )
        try:
            return response.json()
        except ValueError as e:
            raise LLMResponseError(f"{path} returned invalid JSON") from e

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": self.config.embed_model,
            "input": texts,
        }
        result = self._post(self.config.embed_path, payload, self.config.embed_timeout)
        embeddings = result.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise LLMResponseError(
                "unexpected embed response: "
                f"{len(embeddings) if isinstance(embeddings, list) else 'no'} "
                f"embeddings for {len(texts)} inputs"
            )
        return embeddings

    def _embed(self, texts: list[str], prefix: str) -> list[list[float]]:
        prefixed = [f"{prefix}{text}" for text in texts]
        for text in prefixed:
            tokens = estimate_tokens(text)
            if tokens > EMBED_TOKEN_LIMIT:
                # The model silently truncates beyond its sequence
                # limit; the chunker should prevent this, so it is
                # worth a warning when it happens anyway.
                logger.warning(
                    "embedding input of ~%d tokens exceeds the %d token "
                    "limit of %s and will be truncated: %.80r...",
                    tokens,
                    EMBED_TOKEN_LIMIT,
                    self.config.embed_model,
                    text,
                )
        embeddings: list[list[float]] = []
        for start in range(0, len(prefixed), EMBED_BATCH_SIZE):
            batch = prefixed[start : start + EMBED_BATCH_SIZE]
            embeddings.extend(self._embed_batch(batch))
        return embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed content chunks for indexing."""
        return self._embed(texts, SEARCH_DOCUMENT_PREFIX)

    def embed_query(self, text: str) -> list[float]:
        """Embed a user question for retrieval."""
        return self._embed([text], SEARCH_QUERY_PREFIX)[0]

    def chat(self, prompt: str, system: str | None = None) -> str:
        """Generate an answer with the general-purpose model.

        OpenAI-compatible chat completions request, non-streaming;
        used by the query pipeline (implementation ticket for the
        retrieval endpoint + answer generation).
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.config.chat_model,
            "messages": messages,
            "stream": False,
        }
        result = self._post(self.config.chat_path, payload, self.config.chat_timeout)
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMResponseError("unexpected chat response shape") from e
        if not isinstance(content, str):
            raise LLMResponseError("unexpected chat content type")
        return content
