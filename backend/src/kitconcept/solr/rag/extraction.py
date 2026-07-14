"""Extraction of chunkable text segments from content objects.

Reuses the block text extraction of the ``body_text_blocks`` indexer
(``kitconcept.solr.indexers.text``) but keeps the per-block texts as
separate segments, in layout order, so the chunker can respect the
structural boundaries.

MVP scope note: RAG covers block-based content plus title/description.
The body text of binary content (File, Image) is extracted by Tika
inside Solr and never passes through Plone, so it cannot be chunked
and embedded here; supporting it is a post-MVP follow-up.
"""

from kitconcept.solr.indexers.text import extract_text
from plone.restapi.behaviors import IBlocks
from zope.globalrequest import getRequest


def extract_segments(obj) -> list[str]:
    """Text segments of a content object, in document order."""
    segments = []
    title = obj.Title()
    if title and title.strip():
        segments.append(title)
    description = obj.Description()
    if description and description.strip():
        segments.append(description)
    if IBlocks.providedBy(obj):
        request = getRequest()
        blocks = getattr(obj, "blocks", None) or {}
        blocks_layout = getattr(obj, "blocks_layout", None) or {}
        for block_id in blocks_layout.get("items", []):
            block = blocks.get(block_id, {})
            text = extract_text(block, obj, request)
            if text and text.strip():
                segments.append(text)
    return segments
