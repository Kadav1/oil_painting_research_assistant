"""
filesystem_store.py — Filesystem-based storage for raw, clean, and chunk files.

Handles: path resolution, file reading/writing, sidecar metadata JSON files.
All paths rooted at config data dirs. No hardcoded paths.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


class FilesystemStore:
    """
    Provides read/write access to the project's data directory structure.

    Responsibilities:
    - Save raw captured files to data/raw/
    - Save normalized text/markdown to data/clean/
    - Save and load chunk text and metadata JSON files
    - Manage metadata sidecar files
    """

    def __init__(self) -> None:
        cfg.ensure_data_dirs()

    # ------------------------------------------------------------------
    # Raw files
    # ------------------------------------------------------------------

    def raw_path(self, source_id: str, filename: str) -> Path:
        """Construct the path for a raw file under data/raw/{source_id}/."""
        return cfg.RAW_DIR / source_id / filename

    def save_raw_file(self, source_id: str, filename: str, content: bytes) -> Path:
        """Save raw file bytes to data/raw/{source_id}/{filename}."""
        dest = self.raw_path(source_id, filename)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        logger.info("Saved raw file: %s", dest)
        return dest

    def raw_file_exists(self, source_id: str, filename: str) -> bool:
        return self.raw_path(source_id, filename).exists()

    # ------------------------------------------------------------------
    # Clean / normalized text
    # ------------------------------------------------------------------

    def clean_path(self, source_id: str) -> Path:
        """Construct the path for the normalized markdown file."""
        return cfg.CLEAN_DIR / source_id / f"{source_id}.md"

    def save_clean_text(self, source_id: str, text: str) -> Path:
        """Save normalized markdown text to data/clean/{source_id}/{source_id}.md."""
        dest = self.clean_path(source_id)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        logger.info("Saved clean text: %s", dest)
        return dest

    def load_clean_text(self, source_id: str) -> Optional[str]:
        """Load normalized text; returns None if not found."""
        path = self.clean_path(source_id)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def clean_text_exists(self, source_id: str) -> bool:
        return self.clean_path(source_id).exists()

    # ------------------------------------------------------------------
    # Chunk files
    # ------------------------------------------------------------------

    def chunk_text_path(self, chunk_id: str) -> Path:
        """Path for a chunk's text file: data/chunks/text/{chunk_id}.txt"""
        return cfg.CHUNKS_TEXT_DIR / f"{chunk_id}.txt"

    def chunk_metadata_path(self, chunk_id: str) -> Path:
        """Path for a chunk's metadata sidecar: data/chunks/metadata/{chunk_id}.json"""
        return cfg.CHUNKS_METADATA_DIR / f"{chunk_id}.json"

    def save_chunk(self, chunk_id: str, text: str, metadata: dict[str, Any]) -> None:
        """Save chunk text and metadata sidecar JSON."""
        text_path = self.chunk_text_path(chunk_id)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(text, encoding="utf-8")

        meta_path = self.chunk_metadata_path(chunk_id)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with meta_path.open("w", encoding="utf-8") as fh:
            json.dump(metadata, fh, ensure_ascii=False, indent=2)

    def load_chunk_text(self, chunk_id: str) -> Optional[str]:
        """Load chunk text; returns None if not found."""
        path = self.chunk_text_path(chunk_id)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def load_chunk_metadata(self, chunk_id: str) -> Optional[dict[str, Any]]:
        """Load chunk metadata JSON; returns None if not found."""
        path = self.chunk_metadata_path(chunk_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def chunk_ids_for_source(self, source_id: str) -> list[str]:
        """List all chunk_ids whose metadata file belongs to a given source_id."""
        results: list[str] = []
        for meta_file in cfg.CHUNKS_METADATA_DIR.glob("CHK-*.json"):
            if meta_file.stem.startswith(f"CHK-{source_id}-"):
                results.append(meta_file.stem)
        return sorted(results)

    def delete_chunks_for_source(self, source_id: str) -> int:
        """Delete all text and metadata chunk files for a source. Returns count deleted."""
        chunk_ids = self.chunk_ids_for_source(source_id)
        for cid in chunk_ids:
            for path in [self.chunk_text_path(cid), self.chunk_metadata_path(cid)]:
                if path.exists():
                    path.unlink()
        logger.info("Deleted %d chunk files for source %s", len(chunk_ids), source_id)
        return len(chunk_ids)

    # ------------------------------------------------------------------
    # Source metadata sidecars
    # ------------------------------------------------------------------

    def source_metadata_path(self, source_id: str) -> Path:
        """Path for source-level metadata JSON: data/clean/{source_id}/{source_id}.meta.json"""
        return cfg.CLEAN_DIR / source_id / f"{source_id}.meta.json"

    def save_source_metadata(self, source_id: str, metadata: dict[str, Any]) -> Path:
        dest = self.source_metadata_path(source_id)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(metadata, fh, ensure_ascii=False, indent=2)
        return dest

    def load_source_metadata(self, source_id: str) -> Optional[dict[str, Any]]:
        path = self.source_metadata_path(source_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    # ------------------------------------------------------------------
    # Table files
    # ------------------------------------------------------------------

    def table_path(self, source_id: str, table_index: int) -> Path:
        """Path for an extracted table: data/chunks/tables/{source_id}_table_{NNN}.json"""
        return cfg.CHUNKS_TABLES_DIR / f"{source_id}_table_{table_index:03d}.json"

    def save_table(self, source_id: str, table_index: int, table_data: dict[str, Any]) -> Path:
        dest = self.table_path(source_id, table_index)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(table_data, fh, ensure_ascii=False, indent=2)
        return dest

    # ------------------------------------------------------------------
    # Generic JSON helpers
    # ------------------------------------------------------------------

    def load_json(self, path: Path) -> Optional[dict[str, Any]]:
        """Load a JSON file; returns None if not found."""
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def save_json(self, path: Path, data: Any) -> None:
        """Save data to a JSON file, creating parent directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
