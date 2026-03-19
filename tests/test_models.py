"""
test_models.py — Unit tests for Pydantic v2 data models.

Tests: ChunkRecord, SourceRecord, BenchmarkRecord, AnswerResult, ContextPackage.
"""

import pytest
from pydantic import ValidationError


def _make_chunk_record(**kwargs):
    from oil_painting_rag.models.chunk_models import ChunkRecord
    defaults = dict(
        chunk_id="CHK-SRC001-001",
        source_id="SRC001",
        chunk_index=0,
        section_path="",
        chunk_title="Test Chunk",
        text="Lead white is a basic lead carbonate.",
        token_estimate=10,
        chunk_type="prose",
        domain="pigments",
        trust_tier=2,
        approval_state="retrieval_allowed",
        source_family="pigment_reference",
        source_type="technical_handbook",
    )
    defaults.update(kwargs)
    return ChunkRecord(**defaults)


# ---------------------------------------------------------------------------
# ChunkRecord
# ---------------------------------------------------------------------------

class TestChunkRecord:
    def test_basic_creation(self):
        chunk = _make_chunk_record()
        assert chunk.chunk_id == "CHK-SRC001-001"
        assert chunk.trust_tier == 2
        assert chunk.domain == "pigments"

    def test_chroma_round_trip(self):
        """Metadata written to ChromaDB and read back should reproduce the record."""
        from oil_painting_rag.models.chunk_models import ChunkRecord
        chunk = _make_chunk_record(
            chunk_id="CHK-SRC001-001",
            chunk_title="Lead White",
            text="Lead white (2PbCO3·Pb(OH)2) is a warm white.",
            materials_mentioned=["lead white", "PbCO3"],
            pigment_codes=["PW1"],
            quality_flags=[],
            question_types_supported=["material_identification"],
        )
        meta = chunk.to_chroma_metadata()

        # ChromaDB only allows str/int/float/bool
        for v in meta.values():
            assert isinstance(v, (str, int, float, bool)), f"Bad type for {v!r}"

        # Reconstruct
        rebuilt = ChunkRecord.from_chroma_metadata(chunk.chunk_id, chunk.text, meta)
        assert rebuilt.chunk_id == chunk.chunk_id
        assert rebuilt.source_id == chunk.source_id
        assert rebuilt.materials_mentioned == chunk.materials_mentioned
        assert rebuilt.pigment_codes == chunk.pigment_codes

    def test_pipe_encoding_empty_list(self):
        from oil_painting_rag.models.chunk_models import ChunkRecord
        chunk = _make_chunk_record(
            chunk_id="CHK-SRC001-002",
            chunk_title="Empty",
            text="No pigments.",
            domain="mixed",
            trust_tier=3,
        )
        meta = chunk.to_chroma_metadata()
        assert meta["materials_mentioned"] == ""
        rebuilt = ChunkRecord.from_chroma_metadata(chunk.chunk_id, chunk.text, meta)
        assert rebuilt.materials_mentioned == []


# ---------------------------------------------------------------------------
# SourceRecord
# ---------------------------------------------------------------------------

def _make_source_record(**kwargs):
    from oil_painting_rag.models.source_models import SourceRecord
    defaults = dict(
        source_id="SRC001",
        title="Pigment Reference Handbook",
        short_title="PigmentRef",
        source_family="pigment_reference",
        source_type="technical_handbook",
        institution_or_publisher="Test Publisher",
        access_type="purchased",
        raw_file_name="pigref.pdf",
        raw_file_path="data/raw/pigref.pdf",
        capture_date="2025-01-01",
        capture_method="manual_download",
        domain="pigments",
        trust_tier=2,
    )
    defaults.update(kwargs)
    return SourceRecord(**defaults)


class TestSourceRecord:
    def test_basic_creation(self):
        src = _make_source_record()
        assert src.source_id == "SRC001"
        assert src.trust_tier == 2

    def test_chroma_propagation(self):
        src = _make_source_record(source_family="museum_conservation", domain="conservation", trust_tier=1)
        prop = src.to_chroma_propagation()
        assert prop["trust_tier"] == 1
        assert prop["source_family"] == "museum_conservation"
        assert "source_title" in prop
        assert "citation_format" in prop


# ---------------------------------------------------------------------------
# BenchmarkRecord
# ---------------------------------------------------------------------------

class TestBenchmarkRecord:
    def test_basic_creation(self):
        from oil_painting_rag.models.benchmark_models import BenchmarkRecord
        rec = BenchmarkRecord(
            benchmark_id="BMK-PIG-001",
            category="pigments",
            question="What is lead white?",
            difficulty="basic",
            status="approved",
        )
        assert rec.benchmark_id == "BMK-PIG-001"
        assert rec.question == "What is lead white?"

    def test_extra_fields_ignored(self):
        """extra='ignore' should allow unknown fields without raising."""
        from oil_painting_rag.models.benchmark_models import BenchmarkRecord
        rec = BenchmarkRecord.model_validate({
            "benchmark_id": "BMK-CON-001",
            "category": "conservation",
            "question": "Why does smalt discolor?",
            "difficulty": "intermediate",
            "status": "approved",
            "unknown_field": "this should be ignored",
        })
        assert rec.benchmark_id == "BMK-CON-001"
        assert not hasattr(rec, "unknown_field")


# ---------------------------------------------------------------------------
# ScoringResult.compute()
# ---------------------------------------------------------------------------

class TestScoringResult:
    def test_pass(self):
        from oil_painting_rag.models.benchmark_models import DimensionScore, ScoringResult
        result = ScoringResult(
            benchmark_id="BMK-PIG-001",
            dimension_scores=[
                DimensionScore(dimension="Accuracy", score=4.5),
                DimensionScore(dimension="Source Fitness", score=4.0),
                DimensionScore(dimension="Usefulness", score=4.5),
                DimensionScore(dimension="Uncertainty Handling", score=4.0),
                DimensionScore(dimension="Distinction Quality", score=4.0),
                DimensionScore(dimension="Citation Readiness", score=4.0),
            ],
        )
        result.compute()
        assert result.passed is True
        assert result.average_score == pytest.approx(4.166, rel=1e-2)

    def test_fail_low_accuracy_floor(self):
        from oil_painting_rag.models.benchmark_models import DimensionScore, ScoringResult
        result = ScoringResult(
            benchmark_id="BMK-PIG-001",
            dimension_scores=[
                DimensionScore(dimension="Accuracy", score=2.0),  # below floor
                DimensionScore(dimension="Source Fitness", score=5.0),
                DimensionScore(dimension="Usefulness", score=5.0),
                DimensionScore(dimension="Uncertainty Handling", score=5.0),
                DimensionScore(dimension="Distinction Quality", score=5.0),
                DimensionScore(dimension="Citation Readiness", score=5.0),
            ],
        )
        result.compute()
        assert result.passed is False

    def test_fail_low_average(self):
        from oil_painting_rag.models.benchmark_models import DimensionScore, ScoringResult
        result = ScoringResult(
            benchmark_id="BMK-PIG-001",
            dimension_scores=[
                DimensionScore(dimension="Accuracy", score=3.5),
                DimensionScore(dimension="Source Fitness", score=3.0),
                DimensionScore(dimension="Usefulness", score=3.0),
                DimensionScore(dimension="Uncertainty Handling", score=3.0),
                DimensionScore(dimension="Distinction Quality", score=3.0),
                DimensionScore(dimension="Citation Readiness", score=3.0),
            ],
        )
        result.compute()
        assert result.passed is False  # average < 4.0


# ---------------------------------------------------------------------------
# AnswerResult
# ---------------------------------------------------------------------------

class TestAnswerResult:
    def test_basic_creation(self):
        from oil_painting_rag.models.retrieval_models import AnswerLabel, AnswerResult
        result = AnswerResult(
            query="What is titanium white?",
            answer_text="Titanium white (PW6) is a bright, highly opaque white.",
            answer_mode="Studio",
            answer_labels=[
                AnswerLabel(
                    label="well_established",
                    scope_level="general",
                    display_phrase="well-documented in conservation literature",
                )
            ],
            citations=["Mayer, R. (1991). The Artist's Handbook."],
        )
        assert result.answer_mode == "Studio"
        assert len(result.answer_labels) == 1
        assert result.answer_labels[0].label == "well_established"
