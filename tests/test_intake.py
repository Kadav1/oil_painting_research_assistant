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


from unittest.mock import MagicMock, patch


class TestAutoMode:
    """Test auto-mode field resolution in process_file."""

    def _make_classifier(self, family="manufacturer", family_conf="high",
                         domain="product", domain_conf="high"):
        """Create a mock classifier with controlled inference results."""
        from oil_painting_rag.ingestion.intake_classifier import InferenceResult

        clf = MagicMock()
        clf.family_codes = {"manufacturer": "MFR", "museum_conservation": "MUS", "unknown": "UNK"}
        clf.source_type_by_family = {"manufacturer": ["tds", "product_catalog", "sds"]}
        clf.read_content_preview.return_value = ""
        clf.infer_source_family.return_value = InferenceResult(
            value=family, confidence=family_conf, hits=3
        )
        clf.infer_domain.return_value = InferenceResult(
            value=domain, confidence=domain_conf, hits=3
        )
        clf.infer_capture_method.return_value = "pdf_download"
        return clf

    def _make_registry(self, existing_ids=None):
        registry = MagicMock()
        registry.list_ids.return_value = existing_ids or []
        return registry

    def _make_capture(self):
        return MagicMock()

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_flag_skips_prompts(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """With auto=True and high confidence, process_file completes without input()."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {
            "title": "Sennelier Product Catalog",
            "author": "Sennelier",
            "creator": "Sennelier SAS",
        }
        test_file = tmp_path / "sennelier-catalog.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier()
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-MFR-001"
        capture.register_source.assert_called_once()
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["title"] == "Sennelier Product Catalog"
        assert call_kwargs["institution_or_publisher"] == "Sennelier SAS"
        assert call_kwargs["source_type"] == "tds"  # first in source_type_by_family
        assert call_kwargs["access_type"] == "open_access"

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_uses_filename_when_no_pdf_title(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """When PDF has no title metadata, falls back to filename-derived title."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": None, "author": None, "creator": None}
        test_file = tmp_path / "sennelier-NuancierHXF-EN.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier()
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-MFR-001"
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["title"] == "Sennelier Nuancierhxf En"
        assert call_kwargs["institution_or_publisher"] == "unknown"

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_unknown_family_uses_unk(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """With auto=True and unknown family, uses SRC-UNK-xxx."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": None, "author": None, "creator": None}
        test_file = tmp_path / "mystery-doc.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier(family="unknown", family_conf="low")
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-UNK-001"
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["source_family"] == "unknown"
        assert call_kwargs["source_type"] == "web_article"  # fallback

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_no_auto_flag_high_confidence_still_auto(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """Without --auto, but high confidence on both family+domain -> auto-processes."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": "Test Title", "author": None, "creator": None}
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier(family_conf="high", domain_conf="high")
        registry = self._make_registry()
        capture = self._make_capture()

        # auto=False (default), but both confidences high -> auto-process
        result = process_file(test_file, "pdf", clf, registry, capture, auto=False)

        assert result == "SRC-MFR-001"
        capture.register_source.assert_called_once()


class TestTitleFromFilename:
    def test_hyphens_and_underscores_to_spaces(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("sennelier-NuancierHXF-EN.pdf")
        assert result == "Sennelier Nuancierhxf En"

    def test_extension_stripped(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("my_document.txt")
        assert result == "My Document"

    def test_no_extension(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("some-file")
        assert result == "Some File"


class TestUnknownFamilyCode:
    def test_classifier_has_unknown_family_code(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        assert "unknown" in clf.family_codes
        assert clf.family_codes["unknown"] == "UNK"

    def test_next_source_id_with_unk(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("UNK", existing_ids=[])
        assert result == "SRC-UNK-001"

    def test_next_source_id_unk_increments(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("UNK", existing_ids=["SRC-UNK-001", "SRC-UNK-002"])
        assert result == "SRC-UNK-003"
