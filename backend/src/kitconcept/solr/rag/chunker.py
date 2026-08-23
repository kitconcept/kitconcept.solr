"""Structure-aware chunking of content text for embedding.

Long documents embedded as a single vector become "blurry", and the
embedding model additionally truncates its input at 512 tokens, so the
extracted text is split into chunks of ~400 tokens (SPECIFICATION-79.md
§3). Sizes are estimated with a chars-per-token heuristic — we have no
access to the model's tokenizer, which is also why the chunk target
leaves headroom below the model limit.

The chunker is structure-aware in the sense that it packs whole
segments (Volto blocks, paragraphs) and only splits inside a segment
when the segment alone exceeds the chunk size — then preferably at
sentence boundaries. Consecutive chunks overlap by a tail of the
previous chunk so that statements on a chunk border stay retrievable.
"""

from kitconcept.solr.rag.config import CHUNK_MIN_CHARS
from kitconcept.solr.rag.config import CHUNK_OVERLAP_CHARS
from kitconcept.solr.rag.config import CHUNK_TARGET_CHARS

import re


SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
WHITESPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return WHITESPACE.sub(" ", text).strip()


def split_long_text(text: str, limit: int) -> list[str]:
    """Split a text into pieces of at most ``limit`` characters.

    Prefers sentence boundaries; falls back to word boundaries, and to
    a hard cut only for pathological unbroken runs.
    """
    if len(text) <= limit:
        return [text]
    pieces: list[str] = []
    current = ""
    for sentence in SENTENCE_END.split(text):
        while len(sentence) > limit:
            # Overlong sentence: cut at the last word boundary before
            # the limit, or hard-cut when there is none.
            cut = sentence.rfind(" ", 0, limit + 1)
            if cut <= 0:
                cut = limit
            head, sentence = sentence[:cut].strip(), sentence[cut:].strip()
            if current:
                pieces.append(current)
                current = ""
            if head:
                pieces.append(head)
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) > limit and current:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _overlap_tail(chunk: str) -> str:
    """The tail of a chunk carried over into the next one."""
    if len(chunk) <= CHUNK_OVERLAP_CHARS:
        return chunk
    tail = chunk[-CHUNK_OVERLAP_CHARS:]
    # Start the overlap at a word boundary.
    cut = tail.find(" ")
    if cut >= 0:
        tail = tail[cut + 1 :]
    return tail


def chunk_segments(segments: list[str]) -> list[str]:
    """Pack text segments into overlapping chunks of the target size.

    :param segments: Texts in document order (e.g. one per Volto
        block). Segment boundaries are respected: a segment is only
        split when it alone exceeds the chunk size.
    :returns: Chunk texts in document order.
    """
    pieces: list[str] = []
    for segment in segments:
        segment = _normalize(segment)
        if not segment:
            continue
        pieces.extend(split_long_text(segment, CHUNK_TARGET_CHARS))

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) > CHUNK_TARGET_CHARS and current:
            chunks.append(current)
            current = f"{_overlap_tail(current)} {piece}".strip()
        else:
            current = candidate
    if current:
        # Merge a tiny trailing rest into the previous chunk instead of
        # emitting a low-content chunk of its own.
        if chunks and len(current) < CHUNK_MIN_CHARS:
            merged = f"{chunks[-1]} {current}".strip()
            chunks[-1] = merged
        else:
            chunks.append(current)
    return chunks
