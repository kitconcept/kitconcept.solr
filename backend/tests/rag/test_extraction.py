"""Unit tests for the text segment extraction - both kinds of chunking.

The Plate structures below follow plone.restapi's Plate support (the
authoritative implementation of the new editor's block storage):
the block @type is __somersault__ (provisional upstream name), the
``value`` is a list of editor nodes - elements with ``children``,
leafs with ``text``, and dicts with an ``@type`` are embedded Volto
sub-blocks. No end-to-end tests yet: Plate pages cannot be produced
manually on a current site, so unit tests carry the coverage until
the new editor settles.
"""

from kitconcept.solr.rag import extraction as extraction_module
from kitconcept.solr.rag.extraction import extract_plate_segments
from kitconcept.solr.rag.extraction import extract_segments
from kitconcept.solr.rag.extraction import is_plate_block
from kitconcept.solr.rag.extraction import PLATE_BLOCK_TYPE
from kitconcept.solr.rag.extraction import plate_embedded_blocks
from kitconcept.solr.rag.extraction import plate_node_text
from unittest import mock

import pytest


def leaf(text, **marks):
    return {"text": text, **marks}


def element(element_type, *children):
    return {"type": element_type, "children": list(children)}


def plate_block(*value):
    return {"@type": PLATE_BLOCK_TYPE, "value": list(value)}


def make_obj(blocks, layout_items, title="", description=""):
    obj = mock.Mock()
    obj.Title.return_value = title
    obj.Description.return_value = description
    obj.blocks = blocks
    obj.blocks_layout = {"items": layout_items}
    return obj


@pytest.fixture(autouse=True)
def blocks_provided():
    """Content objects count as IBlocks; no Zope request needed."""
    with (
        mock.patch.object(extraction_module.IBlocks, "providedBy", return_value=True),
        mock.patch.object(extraction_module, "getRequest", return_value=None),
    ):
        yield


class TestIsPlateBlock:
    def test_plate_block_detected(self):
        assert is_plate_block(plate_block()) is True

    def test_classic_blocks_are_not_plate(self):
        assert is_plate_block({"@type": "slate", "plaintext": "x"}) is False
        assert is_plate_block({}) is False


class TestPlateNodeText:
    def test_leaf(self):
        assert plate_node_text(leaf("Hello")) == "Hello"

    def test_element_with_leaf_children(self):
        node = element("p", leaf("Hello"), leaf("world"))
        assert plate_node_text(node) == "Hello world"

    def test_marked_leafs_are_plain_text(self):
        # marks (bold, italic...) are extra keys on the leaf
        node = element("p", leaf("Plain"), leaf("bold", bold=True))
        assert plate_node_text(node) == "Plain bold"

    def test_nested_elements(self):
        node = element(
            "blockquote",
            element("p", leaf("Deeply")),
            element("p", leaf("nested")),
        )
        assert plate_node_text(node) == "Deeply nested"

    def test_embedded_subblock_contributes_no_text(self):
        node = element(
            "p",
            leaf("Before"),
            {"@type": "image", "searchableText": "not text content"},
            leaf("after"),
        )
        assert plate_node_text(node) == "Before  after"

    def test_plain_string_node(self):
        assert plate_node_text("bare string") == "bare string"

    def test_empty_and_unknown(self):
        assert plate_node_text([]) == ""
        assert plate_node_text({}) == ""
        assert plate_node_text(None) == ""


class TestPlateEmbeddedBlocks:
    def test_in_document_order(self):
        value = [
            element("p", {"@type": "video", "id": "first"}),
            element(
                "div",
                element("p", {"@type": "image", "id": "second"}),
                {"@type": "teaser", "id": "third"},
            ),
        ]
        found = [b["id"] for b in plate_embedded_blocks(value)]
        assert found == ["first", "second", "third"]

    def test_no_embedded_blocks(self):
        assert list(plate_embedded_blocks([element("p", leaf("x"))])) == []


class TestExtractPlateSegments:
    def test_one_segment_per_top_level_element(self):
        block = plate_block(
            element("h2", leaf("Vacation policy")),
            element("p", leaf("Employees get "), leaf("30 days", bold=True)),
            element("p", leaf("Requests go through the HR portal.")),
        )
        segments = extract_plate_segments(block, None, None)
        assert segments == [
            "Vacation policy",
            "Employees get 30 days",
            "Requests go through the HR portal.",
        ]

    def test_empty_elements_skipped(self):
        block = plate_block(
            element("p", leaf("Text")),
            element("p", leaf("   ")),
            element("p"),
        )
        assert extract_plate_segments(block, None, None) == ["Text"]

    def test_embedded_subblock_text_in_place(self):
        block = plate_block(
            element("p", leaf("Before")),
            element(
                "p",
                {"@type": "custom", "searchableText": "Embedded block text"},
            ),
            element("p", leaf("After")),
        )
        segments = extract_plate_segments(block, None, None)
        assert segments == ["Before", "Embedded block text", "After"]

    def test_block_without_value(self):
        assert extract_plate_segments({"@type": PLATE_BLOCK_TYPE}, None, None) == []


class TestExtractSegmentsCoexistence:
    def test_classic_page(self):
        obj = make_obj(
            blocks={
                "b1": {"@type": "slate", "plaintext": "Classic slate text."},
            },
            layout_items=["b1"],
            title="A title",
            description="A description.",
        )
        assert extract_segments(obj) == [
            "A title",
            "A description.",
            "Classic slate text.",
        ]

    def test_plate_page(self):
        obj = make_obj(
            blocks={
                "b1": plate_block(
                    element("h1", leaf("Heading")),
                    element("p", leaf("Paragraph one.")),
                ),
            },
            layout_items=["b1"],
            title="Plate page",
        )
        assert extract_segments(obj) == [
            "Plate page",
            "Heading",
            "Paragraph one.",
        ]

    def test_mixed_page_blocks_coexist(self):
        # both kinds of blocks can even coexist on the same page;
        # detection is per block
        obj = make_obj(
            blocks={
                "old": {"@type": "slate", "plaintext": "Old style."},
                "new": plate_block(element("p", leaf("New style."))),
            },
            layout_items=["old", "new"],
        )
        assert extract_segments(obj) == ["Old style.", "New style."]

    def test_layout_order_respected(self):
        obj = make_obj(
            blocks={
                "new": plate_block(element("p", leaf("New style."))),
                "old": {"@type": "slate", "plaintext": "Old style."},
            },
            layout_items=["new", "old"],
        )
        assert extract_segments(obj) == ["New style.", "Old style."]

    def test_layout_order_wins_over_blocks_dict_order(self):
        # blocks is a plain dict in creation order; reordering a page
        # only rewrites blocks_layout. The layout must win: segments
        # feed the chunker in reading order.
        obj = make_obj(
            blocks={
                "second": {"@type": "slate", "plaintext": "Second on page."},
                "first": {"@type": "slate", "plaintext": "First on page."},
            },
            layout_items=["first", "second"],
        )
        assert extract_segments(obj) == ["First on page.", "Second on page."]

    def test_block_missing_from_layout_still_extracted(self):
        # The Plate editor registers its block in ``blocks`` without
        # adding it to ``blocks_layout`` - the page body must not be
        # lost over that (intranet ticket #580). Layout-listed blocks
        # come first (they carry the document order), unlisted ones
        # after.
        obj = make_obj(
            blocks={
                "classic-title": {"@type": "title"},
                "__somersault__": plate_block(
                    element("title", leaf("Page title")),
                    element("p", leaf("Body paragraph.")),
                ),
                "classic-slate": {"@type": "slate", "plaintext": "Slate text."},
            },
            layout_items=["classic-title", "classic-slate"],
        )
        assert extract_segments(obj) == [
            "Slate text.",
            "Page title",
            "Body paragraph.",
        ]

    def test_layout_id_without_block_ignored(self):
        obj = make_obj(
            blocks={
                "b1": {"@type": "slate", "plaintext": "Kept."},
            },
            layout_items=["missing", "b1"],
        )
        assert extract_segments(obj) == ["Kept."]
