"""
pdf_metadata_reader.py — Extract metadata from PDF files.

Uses pypdf to read the PDF document info dictionary (/Title, /Author, /Creator).
Returns all None on any failure — no exceptions leak out.
"""

from __future__ import annotations

from pathlib import Path

from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

_EMPTY_RESULT: dict[str, str | None] = {"title": None, "author": None, "creator": None}


def extract_pdf_metadata(filepath: Path) -> dict[str, str | None]:
    """
    Extract title, author, and creator from a PDF's document info dictionary.

    Returns {"title": ..., "author": ..., "creator": ...} with str values from
    the PDF metadata, or None for any field that is missing or unreadable.

    Returns all-None dict for non-PDF files, missing files, or read errors.
    """
    if filepath.suffix.lower() != ".pdf":
        return dict(_EMPTY_RESULT)

    try:
        from pypdf import PdfReader

        reader = PdfReader(filepath)
        meta = reader.metadata

        if meta is None:
            return dict(_EMPTY_RESULT)

        title = meta.get("/Title")
        author = meta.get("/Author")
        creator = meta.get("/Creator")

        return {
            "title": str(title).strip() if title else None,
            "author": str(author).strip() if author else None,
            "creator": str(creator).strip() if creator else None,
        }
    except Exception as exc:
        logger.debug("Could not read PDF metadata from %s: %s", filepath, exc)
        return dict(_EMPTY_RESULT)
