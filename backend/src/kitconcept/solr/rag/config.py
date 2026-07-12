"""Configuration for the RAG feature.

MVP configuration is deliberately minimal (SPECIFICATION-79.md §5):

- The "AI search" feature toggle lives in the Plone registry
  (``kitconcept.solr.rag_enabled``), so an admin can turn the feature
  on or off.
- The LLM endpoint URL and credentials come from environment variables,
  following the ``COLLECTIVE_SOLR_HOST`` pattern. Credentials must not
  live in the registry, because registry content ends up in exported
  site configuration.
- Everything else (model names, chunking parameters, timeouts) is a
  code default here. Environment overrides exist for the model names to
  ease testing against different servers; promoting them to registry
  records is a post-MVP task.
"""

from dataclasses import dataclass
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

import os


# Fixed models for the MVP (SPECIFICATION-79.md §8, decisions 3 and 5).
# The explicit :latest tag is required: the kitconcept server does not
# resolve the bare model name.
DEFAULT_EMBED_MODEL = "nomic-embed-text-v2-moe:latest"
DEFAULT_CHAT_MODEL = "qwen3:14b"

# nomic-embed-text-v2-moe truncates input at 512 tokens. Chunks target
# ~400 tokens to leave headroom for the task prefix and tokenizer
# variance (SPECIFICATION-79.md §3). We have no access to the model's
# tokenizer, so sizes are estimated with a chars-per-token heuristic.
EMBED_TOKEN_LIMIT = 512
CHUNK_TARGET_TOKENS = 400
CHARS_PER_TOKEN = 4
CHUNK_TARGET_CHARS = CHUNK_TARGET_TOKENS * CHARS_PER_TOKEN
# 10-15% overlap between consecutive chunks.
CHUNK_OVERLAP_CHARS = CHUNK_TARGET_CHARS // 8
# Fragments smaller than this are merged with their neighbor.
CHUNK_MIN_CHARS = 128

# Timeouts (seconds). Indexing must never hang a worker for long; the
# chat timeout is generous because answer generation takes a while.
EMBED_TIMEOUT = 30.0
CHAT_TIMEOUT = 120.0

# Number of texts sent to /api/embed in one request.
EMBED_BATCH_SIZE = 32

# Number of chunks retrieved for a question (and passed to the
# generation prompt).
TOP_K = 5

# Reciprocal Rank Fusion constant for hybrid retrieval (the standard
# value from Cormack et al. 2009; Solr's native RRF uses it as well).
RRF_K = 60

# Retrieval mode: "hybrid" (BM25 + vector, RRF-fused; the default) or
# "knn" (pure vector). The env override exists for the evaluation on
# the real corpus (compare the two modes); not a supported setting.
RETRIEVAL_HYBRID = "hybrid"
RETRIEVAL_KNN = "knn"

REGISTRY_ENABLED_KEY = "kitconcept.solr.rag_enabled"

# Endpoint paths, relative to the server root URL. The defaults match
# the kitconcept LLM server (Open WebUI in front of Ollama), whose API
# key allowlist permits exactly these two endpoints: embeddings via the
# Ollama-compatible proxy, chat via the native OpenAI-compatible
# endpoint. For a plain Ollama server, override with
# EMBED_PATH=/api/embed and CHAT_PATH=/v1/chat/completions.
DEFAULT_EMBED_PATH = "/ollama/api/embed"
DEFAULT_CHAT_PATH = "/api/chat/completions"

ENV_URL = "KITCONCEPT_SOLR_LLM_URL"
ENV_TOKEN = "KITCONCEPT_SOLR_LLM_TOKEN"  # noqa: S105 - env var name, not a secret
ENV_EMBED_MODEL = "KITCONCEPT_SOLR_LLM_EMBED_MODEL"
ENV_CHAT_MODEL = "KITCONCEPT_SOLR_LLM_CHAT_MODEL"
ENV_EMBED_PATH = "KITCONCEPT_SOLR_LLM_EMBED_PATH"
ENV_CHAT_PATH = "KITCONCEPT_SOLR_LLM_CHAT_PATH"
ENV_RETRIEVAL = "KITCONCEPT_SOLR_RAG_RETRIEVAL"


@dataclass(frozen=True)
class RagConfig:
    """Resolved configuration for the RAG feature."""

    base_url: str
    token: str | None
    embed_model: str
    chat_model: str
    embed_path: str = DEFAULT_EMBED_PATH
    chat_path: str = DEFAULT_CHAT_PATH
    embed_timeout: float = EMBED_TIMEOUT
    chat_timeout: float = CHAT_TIMEOUT
    retrieval: str = RETRIEVAL_HYBRID


def rag_enabled() -> bool:
    """Is the "AI search" registry toggle on?

    Defends against a missing record (e.g. site not upgraded yet).
    """
    registry = queryUtility(IRegistry)
    if registry is None:
        return False
    try:
        return bool(registry[REGISTRY_ENABLED_KEY])
    except KeyError:
        return False


def get_rag_config() -> RagConfig | None:
    """Return the resolved configuration, or None when the feature is off.

    The feature counts as enabled when the registry toggle is on *and*
    the endpoint URL environment variable is present.
    """
    if not rag_enabled():
        return None
    base_url = os.environ.get(ENV_URL, "").strip().rstrip("/")
    if not base_url:
        return None
    token = os.environ.get(ENV_TOKEN, "").strip() or None
    return RagConfig(
        base_url=base_url,
        token=token,
        embed_model=os.environ.get(ENV_EMBED_MODEL, "").strip() or DEFAULT_EMBED_MODEL,
        chat_model=os.environ.get(ENV_CHAT_MODEL, "").strip() or DEFAULT_CHAT_MODEL,
        embed_path=os.environ.get(ENV_EMBED_PATH, "").strip() or DEFAULT_EMBED_PATH,
        chat_path=os.environ.get(ENV_CHAT_PATH, "").strip() or DEFAULT_CHAT_PATH,
        retrieval=os.environ.get(ENV_RETRIEVAL, "").strip() or RETRIEVAL_HYBRID,
    )


def estimate_tokens(text: str) -> int:
    """Heuristic token count (no tokenizer dependency)."""
    return -(-len(text) // CHARS_PER_TOKEN)
