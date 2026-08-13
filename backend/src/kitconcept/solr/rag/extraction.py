"""Extraction of chunkable text segments from content objects.

Two kinds of block storage are supported, coexisting in the same site
(detected per block):

- Classic Volto blocks (slate & friends): reuses the block text
  extraction of the ``body_text_blocks`` indexer
  (``kitconcept.solr.indexers.text``), one segment per block, in
  layout order.
- Plate blocks (the rich text block of the new Volto/Seven editor):
  the block carries a ``value`` list of editor nodes (leafs with
  ``text``, elements with ``children``; dicts with an ``@type`` are
  embedded Volto sub-blocks). Since the single-page editor typically
  holds the whole page in one Plate block, one segment is emitted per
  TOP-LEVEL element (paragraph, heading, ...), so the chunker keeps
  its structural boundaries; embedded sub-blocks contribute their
  segments in document order. The reading logic mirrors
  plone.restapi's PlateTextIndexer/NestedBlocksVisitor (the
  authoritative implementation of the Plate storage), adapted to
  produce ordered segments instead of one flat string.

MVP scope note: RAG covers block-based content plus title/description.
The body text of binary content (File, Image) is extracted by Tika
inside Solr and never passes through Plone, so it cannot be chunked
and embedded here; supporting it is a post-MVP follow-up.
"""

from kitconcept.solr.indexers.text import extract_text
from plone.restapi.behaviors import IBlocks
from zope.globalrequest import getRequest


# The block @type of the Plate rich text block, as currently used by
# plone.restapi's Plate support. The name is clearly provisional
# upstream and may change when the new editor settles - it is the
# single decisive marker distinguishing the two kinds of chunking, so
# keep it in this one constant. Not importable: our pinned
# plone.restapi predates the Plate support, and even upstream main
# hardcodes the string (no named constant). Once the feature settles
# in a plone.restapi release we depend on, import it from there
# instead (provided upstream exposes a constant by then).
PLATE_BLOCK_TYPE = "__somersault__"


def is_plate_block(block: dict) -> bool:
    return block.get("@type") == PLATE_BLOCK_TYPE


def plate_node_text(node) -> str:
    """The flattened text of a Plate node (without sub-blocks).

    Mirrors plone.restapi's PlateTextIndexer.extract_plate_text:
    leafs carry ``text``, elements carry ``children``; a dict with an
    ``@type`` is an embedded sub-block and contributes no text here
    (it is extracted separately, as its own segment).
    """
    if isinstance(node, list):
        return " ".join(plate_node_text(item) for item in node)
    if isinstance(node, dict):
        if "@type" in node:
            return ""
        texts = []
        for key in ("text", "children"):
            if key in node:
                texts.append(plate_node_text(node[key]))
        return " ".join(texts)
    if isinstance(node, str):
        return node.strip()
    return ""


def plate_embedded_blocks(node):
    """Embedded Volto sub-blocks inside a Plate node, in document order.

    The plone.restapi visitor walks these with a LIFO queue (order is
    irrelevant for search indexing); for chunking segments the
    document order matters, so this is a plain in-order traversal.
    """
    if isinstance(node, list):
        for item in node:
            yield from plate_embedded_blocks(item)
    elif isinstance(node, dict):
        if "@type" in node:
            yield node
        else:
            yield from plate_embedded_blocks(node.get("children") or [])


def extract_plate_segments(block: dict, obj, request) -> list[str]:
    """Segments of a Plate block: one per top-level element.

    The single-page editor typically stores the whole page in one
    Plate block, so the top-level elements (paragraphs, headings, ...)
    are the structural boundaries the chunker should see - the analog
    of "one segment per classic block". Embedded sub-blocks are
    extracted with the classic block extraction, in place.
    """
    segments = []
    for element in block.get("value") or []:
        text = plate_node_text(element)
        if text and text.strip():
            segments.append(text)
        for embedded in plate_embedded_blocks(element):
            embedded_text = extract_text(embedded, obj, request)
            if embedded_text and embedded_text.strip():
                segments.append(embedded_text)
    return segments


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
        # Walk the layout first (it carries the document order), then
        # any blocks not listed in it: the Plate editor registers its
        # block in ``blocks`` without adding it to ``blocks_layout``,
        # so a layout-only walk loses the whole page body (intranet
        # ticket #580). Same coverage as plone.restapi's visit_blocks,
        # which iterates blocks.values() for SearchableText.
        # The layout list is the authoritative document order: blocks
        # is a plain dict in creation order, and reordering a page
        # only rewrites blocks_layout - so walking the layout first
        # keeps segments in the order the reader sees them (the
        # chunker merges *consecutive* segments, order matters).
        # The "in blocks" filter guards against a dangling layout
        # entry (a layout id whose block was deleted), which would
        # otherwise KeyError below.
        layout_ids = [
            block_id
            for block_id in blocks_layout.get("items", [])
            if block_id in blocks
        ]
        unlisted_ids = [
            block_id for block_id in blocks if block_id not in set(layout_ids)
        ]
        for block_id in layout_ids + unlisted_ids:
            block = blocks[block_id]
            if is_plate_block(block):
                segments.extend(extract_plate_segments(block, obj, request))
            else:
                text = extract_text(block, obj, request)
                if text and text.strip():
                    segments.append(text)
    return segments
