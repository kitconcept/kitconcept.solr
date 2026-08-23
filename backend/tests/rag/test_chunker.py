from itertools import pairwise
from kitconcept.solr.rag.chunker import chunk_segments
from kitconcept.solr.rag.chunker import split_long_text
from kitconcept.solr.rag.config import CHUNK_MIN_CHARS
from kitconcept.solr.rag.config import CHUNK_OVERLAP_CHARS
from kitconcept.solr.rag.config import CHUNK_TARGET_CHARS


def sentences(count: int, length: int = 60, marker: str = "s") -> str:
    """A text of `count` sentences, each ~`length` chars."""
    parts = []
    for i in range(count):
        body = f"Sentence {marker}{i} " + "word " * ((length - 20) // 5)
        parts.append(body.strip() + ".")
    return " ".join(parts)


HARD_CAP = CHUNK_TARGET_CHARS + CHUNK_MIN_CHARS


class TestChunkSegments:
    def test_empty_input(self):
        assert chunk_segments([]) == []
        assert chunk_segments(["", "   ", "\n\t"]) == []

    def test_single_small_segment_is_one_chunk(self):
        assert chunk_segments(["A short paragraph."]) == ["A short paragraph."]

    def test_small_segments_are_packed_together(self):
        segments = ["First paragraph.", "Second paragraph.", "Third paragraph."]
        chunks = chunk_segments(segments)
        assert chunks == ["First paragraph. Second paragraph. Third paragraph."]

    def test_whitespace_is_normalized(self):
        chunks = chunk_segments(["A  text\nwith   messy\t\twhitespace."])
        assert chunks == ["A text with messy whitespace."]

    def test_no_chunk_exceeds_target_plus_merge_slack(self):
        segments = [sentences(6, marker=f"p{p}") for p in range(20)]
        chunks = chunk_segments(segments)
        assert len(chunks) > 1
        assert all(len(chunk) <= HARD_CAP for chunk in chunks)

    def test_consecutive_chunks_overlap(self):
        segments = [sentences(6, marker=f"p{p}") for p in range(20)]
        chunks = chunk_segments(segments)
        for previous, following in pairwise(chunks):
            # The following chunk starts with a tail of the previous.
            overlap_probe = following[: CHUNK_OVERLAP_CHARS // 4]
            assert overlap_probe.split()[0] in previous

    def test_all_content_is_preserved(self):
        segments = [sentences(6, marker=f"p{p}") for p in range(10)]
        chunks = chunk_segments(segments)
        joined = " ".join(chunks)
        for p in range(10):
            for i in range(6):
                assert f"Sentence p{p}{i}" in joined

    def test_tiny_trailing_rest_is_merged(self):
        # One target-filling segment plus a tiny one: the tiny rest must
        # not become a chunk of its own.
        big = "x" * (CHUNK_TARGET_CHARS - 10) + "."
        chunks = chunk_segments([big, "Tiny rest."])
        assert len(chunks) == 1 or all(
            len(chunk) >= CHUNK_MIN_CHARS for chunk in chunks
        )


class TestSplitLongText:
    def test_short_text_untouched(self):
        assert split_long_text("short", 100) == ["short"]

    def test_splits_at_sentence_boundaries(self):
        text = sentences(10)
        pieces = split_long_text(text, 200)
        assert len(pieces) > 1
        assert all(len(piece) <= 200 for piece in pieces)
        # Sentence-boundary splits end with the sentence period.
        assert all(piece.endswith(".") for piece in pieces)

    def test_overlong_sentence_falls_back_to_word_boundary(self):
        text = "word " * 100  # one 500-char "sentence", no sentence end
        pieces = split_long_text(text.strip(), 120)
        assert all(len(piece) <= 120 for piece in pieces)
        assert all(not piece.startswith(" ") for piece in pieces)

    def test_unbroken_run_is_hard_cut(self):
        text = "x" * 500
        pieces = split_long_text(text, 120)
        assert all(len(piece) <= 120 for piece in pieces)
        assert "".join(pieces) == text
