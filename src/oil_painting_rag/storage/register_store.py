"""
register_store.py — Manages CSV audit registers and the source register JSON.

Audit CSVs: acquisition_log.csv, chunk_review_log.csv, conflict_review_log.csv
Source register: individual JSON files per source_id in data/register/sources/
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

_SOURCES_DIR = cfg.REGISTER_DIR / "sources"


def _ensure_dirs() -> None:
    _SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    cfg.REGISTER_DIR.mkdir(parents=True, exist_ok=True)
    cfg.LOGS_DIR.mkdir(parents=True, exist_ok=True)


class RegisterStore:
    """
    Manages source register records and audit log CSVs.

    Source records stored as individual JSON files under data/register/sources/.
    Audit events appended to CSV logs.
    """

    def __init__(self) -> None:
        _ensure_dirs()

    # ------------------------------------------------------------------
    # Source register (JSON per source)
    # ------------------------------------------------------------------

    def _source_path(self, source_id: str) -> Path:
        return _SOURCES_DIR / f"{source_id}.json"

    def save_source(self, record: dict[str, Any]) -> Path:
        """Save or update a source register record."""
        source_id = record["source_id"]
        path = self._source_path(source_id)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)
        logger.debug("Saved source register: %s", source_id)
        return path

    def load_source(self, source_id: str) -> Optional[dict[str, Any]]:
        path = self._source_path(source_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def source_exists(self, source_id: str) -> bool:
        return self._source_path(source_id).exists()

    def list_source_ids(self) -> list[str]:
        return sorted(f.stem for f in _SOURCES_DIR.glob("SRC-*.json"))

    def load_all_sources(self) -> list[dict[str, Any]]:
        results = []
        for sid in self.list_source_ids():
            rec = self.load_source(sid)
            if rec:
                results.append(rec)
        return results

    def sources_as_dataframe(self) -> pd.DataFrame:
        """Return all source records as a pandas DataFrame."""
        records = self.load_all_sources()
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

    # ------------------------------------------------------------------
    # Acquisition log CSV
    # ------------------------------------------------------------------

    _ACQUISITION_COLUMNS = [
        "source_id", "title", "source_family", "source_type",
        "capture_date", "capture_method", "access_type", "logged_at",
    ]

    def append_acquisition_log(self, row: dict[str, Any]) -> None:
        """Append one row to the acquisition log CSV."""
        row.setdefault("logged_at", datetime.now(tz=timezone.utc).isoformat())
        self._append_csv(cfg.ACQUISITION_LOG_PATH, row, self._ACQUISITION_COLUMNS)

    def load_acquisition_log(self) -> pd.DataFrame:
        return self._load_csv(cfg.ACQUISITION_LOG_PATH, self._ACQUISITION_COLUMNS)

    # ------------------------------------------------------------------
    # Chunk review log CSV
    # ------------------------------------------------------------------

    _CHUNK_REVIEW_COLUMNS = [
        "chunk_id", "source_id", "review_status", "approval_state",
        "reviewer", "review_date", "action", "notes",
    ]

    def append_chunk_review_log(self, row: dict[str, Any]) -> None:
        self._append_csv(cfg.CHUNK_REVIEW_LOG_PATH, row, self._CHUNK_REVIEW_COLUMNS)

    def load_chunk_review_log(self) -> pd.DataFrame:
        return self._load_csv(cfg.CHUNK_REVIEW_LOG_PATH, self._CHUNK_REVIEW_COLUMNS)

    # ------------------------------------------------------------------
    # Conflict review log CSV
    # ------------------------------------------------------------------

    _CONFLICT_REVIEW_COLUMNS = [
        "conflict_id", "conflict_type", "entity_ids", "topic",
        "resolution_status", "reviewer", "reviewed_at", "notes",
    ]

    def append_conflict_review_log(self, row: dict[str, Any]) -> None:
        self._append_csv(cfg.CONFLICT_REVIEW_LOG_PATH, row, self._CONFLICT_REVIEW_COLUMNS)

    def load_conflict_review_log(self) -> pd.DataFrame:
        return self._load_csv(cfg.CONFLICT_REVIEW_LOG_PATH, self._CONFLICT_REVIEW_COLUMNS)

    # ------------------------------------------------------------------
    # Retrieval failure log CSV
    # ------------------------------------------------------------------

    _FAILURE_COLUMNS = [
        "failure_id", "benchmark_id", "question", "failure_tags",
        "logged_at", "reviewer_notes",
    ]

    def append_failure_log(self, row: dict[str, Any]) -> None:
        self._append_csv(cfg.RETRIEVAL_FAILURE_LOG_PATH, row, self._FAILURE_COLUMNS)

    def load_failure_log(self) -> pd.DataFrame:
        return self._load_csv(cfg.RETRIEVAL_FAILURE_LOG_PATH, self._FAILURE_COLUMNS)

    # ------------------------------------------------------------------
    # Internal CSV helpers
    # ------------------------------------------------------------------

    def _append_csv(
        self,
        path: Path,
        row: dict[str, Any],
        columns: list[str],
    ) -> None:
        """Append one row to a CSV file, writing header if file is new."""
        is_new = not path.exists()
        with path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
            if is_new:
                writer.writeheader()
            writer.writerow(row)

    def _load_csv(self, path: Path, columns: list[str]) -> pd.DataFrame:
        """Load a CSV file as DataFrame; returns empty DataFrame if not found."""
        if not path.exists():
            return pd.DataFrame(columns=columns)
        try:
            return pd.read_csv(path, dtype=str)
        except Exception as exc:
            logger.warning("Could not load CSV %s: %s", path, exc)
            return pd.DataFrame(columns=columns)
