"""Tests for intake classifier — metadata inference, sanitization, source ID generation."""

from __future__ import annotations

import pytest


class TestSanitizeShortTitle:
    def test_basic_sanitization(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title
        assert sanitize_short_title("NGA Tech Bulletin 35") == "nga_tech_bulletin_35"

    def test_hyphens_become_underscores(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title
        assert sanitize_short_title("Lead-White Study") == "lead_white_study"

    def test_special_chars_stripped(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title
        assert sanitize_short_title("Pigment (Vol. 3): Analysis!") == "pigment_vol_3_analysis"

    def test_consecutive_underscores_collapsed(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title
        assert sanitize_short_title("A   B---C") == "a_b_c"

    def test_truncation_at_60_chars(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title
        long_title = "a" * 80
        result = sanitize_short_title(long_title)
        assert len(result) == 60


class TestInferSourceFamily:
    def test_museum_conservation_from_content(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="bulletin.pdf",
            content="National Gallery Technical Bulletin conservation report on lead white"
        )
        assert result.value == "museum_conservation"
        assert result.confidence == "high"

    def test_manufacturer_from_filename(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="gamblin_tds_titanium_white.pdf",
            content=""
        )
        assert result.value == "manufacturer"

    def test_unknown_when_no_match(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="notes.txt",
            content="some generic text"
        )
        assert result.value == "unknown"
        assert result.confidence == "low"


class TestInferDomain:
    def test_pigment_domain(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        result = clf.infer_domain(
            filename="lead_white.pdf",
            content="Lead white pigment analysis with titanium white comparison"
        )
        assert result.value == "pigment"

    def test_mixed_domain_on_tie(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        result = clf.infer_domain(
            filename="study.pdf",
            content="pigment conservation lead white degradation"
        )
        # pigment: "pigment", "lead white" = 2 hits; conservation: "conservation", "degradation" = 2 hits — tie → mixed
        assert result.value == "mixed"


class TestNextSourceId:
    def test_first_source_in_family(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("MUS", existing_ids=[])
        assert result == "SRC-MUS-001"

    def test_increment_from_existing(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("MUS", existing_ids=["SRC-MUS-001", "SRC-MUS-002", "SRC-PIG-001"])
        assert result == "SRC-MUS-003"

    def test_handles_gaps(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("PIG", existing_ids=["SRC-PIG-001", "SRC-PIG-005"])
        assert result == "SRC-PIG-006"


class TestBuildFilename:
    def test_basic_filename(self):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename
        result = build_intake_filename("SRC-MUS-001", "NGA Tech Bulletin 35", ".pdf")
        assert result == "SRC-MUS-001_nga_tech_bulletin_35.pdf"

    def test_long_title_truncated(self):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename
        long_title = "a" * 80
        result = build_intake_filename("SRC-MUS-001", long_title, ".pdf")
        assert result == f"SRC-MUS-001_{'a' * 60}.pdf"

    def test_collision_suffix(self, tmp_path):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename
        (tmp_path / "SRC-MUS-001_bulletin.pdf").touch()
        result = build_intake_filename("SRC-MUS-001", "Bulletin", ".pdf", dest_dir=tmp_path)
        assert result == "SRC-MUS-001_bulletin_2.pdf"
