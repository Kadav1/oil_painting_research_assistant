"""
metadata_store.py — Storage for provenance records, review records,
retrieval traces, and conflict records.

These records are stored as JSON files in the metadata store,
NOT in ChromaDB (per schema storage_notes).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

# Metadata store root — within data/chunks/metadata for provenance,
# and data/logs for traces and failures.
_PROVENANCE_DIR = cfg.CHUNKS_METADATA_DIR / "provenance"
_REVIEW_DIR = cfg.CHUNKS_METADATA_DIR / "reviews"
_TRACE_DIR = cfg.LOGS_DIR / "traces"
_CONFLICT_DIR = cfg.LOGS_DIR / "conflicts"
_DUP_DIR = cfg.LOGS_DIR / "duplicates"


def _ensure_dirs() -> None:
    for d in [_PROVENANCE_DIR, _REVIEW_DIR, _TRACE_DIR, _CONFLICT_DIR, _DUP_DIR]:
        d.mkdir(parents=True, exist_ok=True)


class MetadataStore:
    """
    Provides read/write access to provenance, review, trace, and conflict records.

    All records stored as individual JSON files keyed by record ID.
    """

    def __init__(self) -> None:
        _ensure_dirs()

    # ------------------------------------------------------------------
    # Field provenance
    # ------------------------------------------------------------------

    def _provenance_path(self, provenance_id: str) -> Path:
        return _PROVENANCE_DIR / f"{provenance_id}.json"

    def save_provenance(self, record: dict[str, Any]) -> None:
        pid = record["provenance_id"]
        path = self._provenance_path(pid)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)

    def load_provenance(self, provenance_id: str) -> Optional[dict[str, Any]]:
        path = self._provenance_path(provenance_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def provenance_for_entity(self, entity_id: str) -> list[dict[str, Any]]:
        """Load all provenance records for a given entity_id."""
        results: list[dict[str, Any]] = []
        prefix = f"PRV-{entity_id}-"
        for f in _PROVENANCE_DIR.glob("PRV-*.json"):
            if f.stem.startswith(prefix):
                with f.open("r", encoding="utf-8") as fh:
                    results.append(json.load(fh))
        return results

    # ------------------------------------------------------------------
    # Review records
    # ------------------------------------------------------------------

    def _review_path(self, review_id: str) -> Path:
        return _REVIEW_DIR / f"{review_id}.json"

    def save_review_record(self, record: dict[str, Any]) -> None:
        rid = record["review_id"]
        path = self._review_path(rid)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)

    def load_review_record(self, review_id: str) -> Optional[dict[str, Any]]:
        path = self._review_path(review_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def reviews_for_entity(self, entity_id: str) -> list[dict[str, Any]]:
        """Load all review records for a given entity_id, sorted by review_date."""
        results: list[dict[str, Any]] = []
        prefix = f"REV-{entity_id}-"
        for f in _REVIEW_DIR.glob("REV-*.json"):
            if f.stem.startswith(prefix):
                with f.open("r", encoding="utf-8") as fh:
                    results.append(json.load(fh))
        return sorted(results, key=lambda r: r.get("review_date", ""))

    # ------------------------------------------------------------------
    # Retrieval traces
    # ------------------------------------------------------------------

    def _trace_path(self, trace_id: str) -> Path:
        return _TRACE_DIR / f"{trace_id}.json"

    def save_trace(self, record: dict[str, Any]) -> None:
        tid = record["trace_id"]
        path = self._trace_path(tid)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)
        logger.debug("Saved retrieval trace: %s", tid)

    def load_trace(self, trace_id: str) -> Optional[dict[str, Any]]:
        path = self._trace_path(trace_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_traces(self, limit: int = 50) -> list[str]:
        """Return most recent trace IDs (by filename, descending)."""
        files = sorted(_TRACE_DIR.glob("TRC-*.json"), reverse=True)
        return [f.stem for f in files[:limit]]

    # ------------------------------------------------------------------
    # Conflict records
    # ------------------------------------------------------------------

    def _conflict_path(self, conflict_id: str) -> Path:
        return _CONFLICT_DIR / f"{conflict_id}.json"

    def save_conflict(self, record: dict[str, Any]) -> None:
        cid = record["conflict_id"]
        path = self._conflict_path(cid)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)

    def load_conflict(self, conflict_id: str) -> Optional[dict[str, Any]]:
        path = self._conflict_path(conflict_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def conflicts_for_entities(self, entity_ids: list[str]) -> list[dict[str, Any]]:
        """Load all conflict records that involve any of the given entity IDs."""
        results: list[dict[str, Any]] = []
        id_set = set(entity_ids)
        for f in _CONFLICT_DIR.glob("CON-*.json"):
            with f.open("r", encoding="utf-8") as fh:
                rec = json.load(fh)
            if id_set.intersection(rec.get("entity_ids", [])):
                results.append(rec)
        return results

    def load_all_conflicts(self) -> list[dict[str, Any]]:
        results = []
        for f in sorted(_CONFLICT_DIR.glob("CON-*.json")):
            with f.open("r", encoding="utf-8") as fh:
                results.append(json.load(fh))
        return results

    # ------------------------------------------------------------------
    # Duplicate clusters
    # ------------------------------------------------------------------

    def _dup_path(self, cluster_id: str) -> Path:
        return _DUP_DIR / f"{cluster_id}.json"

    def save_duplicate_cluster(self, record: dict[str, Any]) -> None:
        cid = record["cluster_id"]
        path = self._dup_path(cid)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)

    def load_duplicate_cluster(self, cluster_id: str) -> Optional[dict[str, Any]]:
        path = self._dup_path(cluster_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
