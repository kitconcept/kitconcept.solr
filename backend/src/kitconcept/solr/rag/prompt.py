"""Prompt building for the RAG answer generation.

The prompt constrains the model to the retrieved context
(SPECIFICATION-79.md §4): answer only from the provided documents,
answer in the language of the question, and decline explicitly when
the answer is not found. Code default for the MVP; a registry override
is a post-MVP configuration item.
"""

from kitconcept.solr.rag.config import TOP_K

import re


SYSTEM_PROMPT = (
    "You are the search assistant of an intranet site. Answer the"
    " user's question based only on the provided context documents."
    " If the answer is not contained in them, say that you could not"
    " find the answer in the documentation - never invent information."
    " Answer in the language of the question. Be concise: one or two"
    " short paragraphs, no headings and no lists unless the question"
    " asks for an enumeration."
)

PROMPT_TEMPLATE = (
    "Context documents:\n\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer the question based only on the context documents above."
)

# Reasoning models may emit a thinking block; never show it to users.
THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def build_prompt(question: str, chunks: list[dict]) -> str:
    """One prompt containing the question and the retrieved context."""
    parts = []
    for index, chunk in enumerate(chunks[:TOP_K], start=1):
        title = chunk.get("parent_title", "")
        text = chunk.get("chunk_text", "")
        parts.append(f"[{index}] {title}\n{text}")
    return PROMPT_TEMPLATE.format(context="\n\n".join(parts), question=question)


def strip_thinking(answer: str) -> str:
    return THINK_RE.sub("", answer).strip()
