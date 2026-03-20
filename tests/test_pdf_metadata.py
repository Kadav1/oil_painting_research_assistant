"""Tests for PDF metadata extraction."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestExtractPdfMetadata:
    def test_non_pdf_returns_none_values(self, tmp_path):
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("hello")
        result = extract_pdf_metadata(txt_file)
        assert result == {"title": None, "author": None, "creator": None}

    def test_missing_file_returns_none_values(self):
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        result = extract_pdf_metadata(Path("/nonexistent/file.pdf"))
        assert result == {"title": None, "author": None, "creator": None}

    def test_valid_pdf_extracts_metadata(self, tmp_path):
        """Create a minimal PDF with metadata using pypdf."""
        from pypdf import PdfWriter

        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata(
            {
                "/Title": "Test Bulletin",
                "/Author": "Jane Doe",
                "/Creator": "National Gallery",
            }
        )
        pdf_path = tmp_path / "test.pdf"
        with pdf_path.open("wb") as f:
            writer.write(f)

        result = extract_pdf_metadata(pdf_path)
        assert result["title"] == "Test Bulletin"
        assert result["author"] == "Jane Doe"
        assert result["creator"] == "National Gallery"

    def test_pdf_without_metadata_returns_none_values(self, tmp_path):
        """PDF with no /Info dictionary returns all None."""
        from pypdf import PdfWriter

        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        pdf_path = tmp_path / "empty_meta.pdf"
        with pdf_path.open("wb") as f:
            writer.write(f)

        result = extract_pdf_metadata(pdf_path)
        assert result["title"] is None
        assert result["author"] is None
        assert result["creator"] is None

    def test_corrupted_file_returns_none_values(self, tmp_path):
        """Corrupted PDF-like file returns all None, no exception."""
        corrupt_pdf = tmp_path / "corrupt.pdf"
        corrupt_pdf.write_bytes(b"%PDF-1.4 this is not valid")
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        result = extract_pdf_metadata(corrupt_pdf)
        assert result == {"title": None, "author": None, "creator": None}
