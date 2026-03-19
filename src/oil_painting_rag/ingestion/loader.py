"""
loader.py — Source document loading utilities.

Loads raw files from disk for processing. Handles text extraction from
plain text, markdown, and structured content.
Does NOT call external APIs or download anything.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.storage.filesystem_store import FilesystemStore
from oil_painting_rag.storage.register_store import RegisterStore
from oil_painting_rag.utils.text_utils import clean_text

logger = get_logger(__name__)


class SourceLoader:
    """
    Loads raw and clean source documents from the filesystem.

    Responsible for: reading files, basic text extraction, returning
    content for downstream chunking.
    """

    def __init__(self) -> None:
        self._fs = FilesystemStore()
        self._register = RegisterStore()

    def load_clean_text(self, source_id: str) -> Optional[str]:
        """
        Load normalized text for a source. Returns None if not found.

        Caller should check normalized_text_created flag before calling.
        """
        text = self._fs.load_clean_text(source_id)
        if text is None:
            logger.warning("No clean text found for source %s", source_id)
        return text

    def load_raw_bytes(self, source_id: str, filename: str) -> Optional[bytes]:
        """Load raw file bytes. Returns None if not found."""
        path = self._fs.raw_path(source_id, filename)
        if not path.exists():
            logger.warning("Raw file not found: %s", path)
            return None
        return path.read_bytes()

    def extract_text_from_raw(self, source_id: str, filename: str) -> Optional[str]:
        """
        Extract text from a raw file based on extension.

        Supports: .txt, .md (direct read).
        For .pdf and other formats, callers must pre-convert to text
        before registering (the raw file should already be a text format,
        or a separate normalization step is applied upstream).
        """
        path = self._fs.raw_path(source_id, filename)
        if not path.exists():
            logger.warning("Raw file not found: %s", path)
            return None

        suffix = path.suffix.lower()
        if suffix in (".txt", ".md", ".markdown"):
            text = path.read_text(encoding="utf-8", errors="replace")
            return clean_text(text)

        # For other formats, try reading as UTF-8 text (may be pre-extracted)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            return clean_text(text)
        except Exception as exc:
            logger.error("Cannot extract text from %s: %s", path, exc)
            return None

    def sources_ready_for_chunking(self) -> list[str]:
        """
        Return source_ids that have clean text but are not yet chunked.
        """
        results: list[str] = []
        for source_id in self._register.list_source_ids():
            rec = self._register.load_source(source_id)
            if rec and rec.get("normalized_text_created") and not rec.get("chunked"):
                results.append(source_id)
        return results

    def sources_ready_for_indexing(self) -> list[str]:
        """
        Return source_ids that are chunked but not yet indexed.
        """
        results: list[str] = []
        for source_id in self._register.list_source_ids():
            rec = self._register.load_source(source_id)
            if rec and rec.get("chunked") and not rec.get("indexed"):
                results.append(source_id)
        return results
