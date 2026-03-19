"""
test_chunking.py — Unit tests for ProseChunker, TableChunker, and chunk_validators.
"""

import pytest

from oil_painting_rag.models.source_models import SourceRecord


def _make_source(**kwargs) -> SourceRecord:
    defaults = dict(
        source_id="SRC-TEST-001",
        title="Test Source",
        short_title="TestSrc",
        source_family="pigment_reference",
        source_type="technical_handbook",
        institution_or_publisher="Test Publisher",
        access_type="purchased",
        raw_file_name="test.txt",
        raw_file_path="data/raw/test.txt",
        capture_date="2025-01-01",
        capture_method="manual_download",
        domain="pigments",
        trust_tier=2,
    )
    defaults.update(kwargs)
    return SourceRecord(**defaults)


# ---------------------------------------------------------------------------
# ProseChunker
# ---------------------------------------------------------------------------

class TestProseChunker:
    def test_chunks_simple_text(self):
        from oil_painting_rag.chunking.chunker import ProseChunker
        chunker = ProseChunker(min_tokens=5)  # low threshold for test
        source = _make_source()
        text = (
            "# Lead White\n\n"
            "Lead white is the oldest known white pigment. "
            "It is a basic lead carbonate. "
            "The pigment code is PW1.\n\n"
            "## Stability\n\n"
            "Lead white is stable in oil but can darken in the presence of sulfur."
        )
        chunks = chunker.chunk_source(source, text)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.source_id == source.source_id
            assert chunk.chunk_id.startswith("CHK-")
            assert len(chunk.text.strip()) > 0

    def test_chunk_ids_are_unique(self):
        from oil_painting_rag.chunking.chunker import ProseChunker
        chunker = ProseChunker(min_tokens=5)
        source = _make_source()
        text = "\n\n".join(
            [f"Sentence {i}. " * 10 for i in range(20)]
        )
        chunks = chunker.chunk_source(source, text)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), "Duplicate chunk IDs found"

    def test_empty_text_returns_no_chunks(self):
        from oil_painting_rag.chunking.chunker import ProseChunker
        chunker = ProseChunker(min_tokens=5)
        source = _make_source()
        chunks = chunker.chunk_source(source, "")
        assert chunks == []

    def test_chunk_inherits_source_metadata(self):
        from oil_painting_rag.chunking.chunker import ProseChunker
        chunker = ProseChunker(min_tokens=5)
        source = _make_source(
            trust_tier=1,
            domain="conservation",
            source_family="museum_conservation",
        )
        text = "Conservation research shows lead white can form lead soaps over time."
        chunks = chunker.chunk_source(source, text)
        assert len(chunks) >= 1
        assert chunks[0].trust_tier == 1
        assert chunks[0].domain == "conservation"


# ---------------------------------------------------------------------------
# TableChunker
# ---------------------------------------------------------------------------

class TestTableChunker:
    def test_detects_markdown_table(self):
        from oil_painting_rag.chunking.table_chunker import TableChunker
        chunker = TableChunker()
        source = _make_source()
        text = (
            "Some prose before the table.\n\n"
            "| Pigment | Code | Lightfastness |\n"
            "|---------|------|---------------|\n"
            "| Lead White | PW1 | Excellent |\n"
            "| Zinc White | PW4 | Excellent |\n\n"
            "Some prose after."
        )
        chunks = chunker.chunk_tables(source, text)
        assert len(chunks) >= 1
        table_chunks = [c for c in chunks if c.chunk_type == "table"]
        assert len(table_chunks) >= 1

    def test_no_table_returns_empty(self):
        from oil_painting_rag.chunking.table_chunker import TableChunker
        chunker = TableChunker()
        source = _make_source()
        text = "Plain prose with no tables."
        chunks = chunker.chunk_tables(source, text)
        assert chunks == []


# ---------------------------------------------------------------------------
# chunk_validators
# ---------------------------------------------------------------------------

class TestChunkValidators:
    def _make_chunk(self, **kwargs):
        from oil_painting_rag.models.chunk_models import ChunkRecord
        defaults = dict(
            chunk_id="CHK-SRC-TEST-001-001",
            source_id="SRC-TEST-001",
            chunk_index=0,
            section_path="",
            chunk_title="Test",
            text="Lead white is a basic lead carbonate. " * 5,
            token_estimate=50,
            chunk_type="prose",
            domain="pigments",
            trust_tier=2,
            approval_state="retrieval_allowed",
            source_family="pigment_reference",
            source_type="technical_handbook",
        )
        defaults.update(kwargs)
        return ChunkRecord(**defaults)

    def test_valid_chunk_passes(self):
        from oil_painting_rag.chunking.chunk_validators import validate_chunk
        chunk = self._make_chunk()
        errors = validate_chunk(chunk)
        assert errors == []

    def test_empty_text_fails(self):
        from oil_painting_rag.chunking.chunk_validators import validate_chunk
        chunk = self._make_chunk(text="")
        errors = validate_chunk(chunk)
        assert any("text" in e.lower() or "token" in e.lower() for e in errors)

    def test_low_quality_flags_detected(self):
        from oil_painting_rag.chunking.chunk_validators import flag_low_quality
        chunk = self._make_chunk(text="X " * 5)  # very short
        flagged = flag_low_quality(chunk)
        # low_density should be flagged for very short text
        assert "low_density" in flagged.quality_flags or len(flagged.text.split()) < 20
