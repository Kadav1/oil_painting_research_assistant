"""
source_registry.py — High-level source registry management interface.

Provides a unified facade over RegisterStore and SourceCapture for
querying, updating, and managing source records.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.source_models import SourceRecord
from oil_painting_rag.storage.register_store import RegisterStore

logger = get_logger(__name__)


class SourceRegistry:
    """
    Facade for source register operations.

    Provides: lookup, listing, status updates, and validation.
    """

    def __init__(self) -> None:
        self._store = RegisterStore()

    def get(self, source_id: str) -> Optional[SourceRecord]:
        """Return a SourceRecord by ID, or None if not found."""
        data = self._store.load_source(source_id)
        if data is None:
            return None
        return SourceRecord.model_validate(data)

    def exists(self, source_id: str) -> bool:
        return self._store.source_exists(source_id)

    def list_ids(self) -> list[str]:
        return self._store.list_source_ids()

    def all_sources(self) -> list[SourceRecord]:
        return [
            SourceRecord.model_validate(rec)
            for rec in self._store.load_all_sources()
        ]

    def as_dataframe(self) -> pd.DataFrame:
        return self._store.sources_as_dataframe()

    def update_field(self, source_id: str, field: str, value: Any) -> None:
        """Update a single field on a source record."""
        rec = self._store.load_source(source_id)
        if rec is None:
            raise KeyError(f"Source not found: {source_id}")
        rec[field] = value
        self._store.save_source(rec)
        logger.debug("Updated %s.%s = %r", source_id, field, value)

    def mark_ready_for_use(self, source_id: str) -> None:
        self.update_field(source_id, "ready_for_use", True)

    def sources_by_family(self, family: str) -> list[SourceRecord]:
        return [s for s in self.all_sources() if s.source_family == family]

    def sources_by_trust_tier(self, tier: int) -> list[SourceRecord]:
        return [s for s in self.all_sources() if s.trust_tier == tier]

    def sources_ready_for_use(self) -> list[SourceRecord]:
        return [s for s in self.all_sources() if s.ready_for_use]

    def sources_not_yet_chunked(self) -> list[SourceRecord]:
        return [
            s for s in self.all_sources()
            if s.normalized_text_created and not s.chunked
        ]

    def validate_all(self) -> list[str]:
        """
        Validate all source records. Return list of error messages.

        Checks: required fields present, enum values valid.
        """
        errors: list[str] = []
        for source in self.all_sources():
            if not source.source_id:
                errors.append("Source with missing source_id found")
                continue
            if not source.citation_format:
                errors.append(f"{source.source_id}: missing citation_format")
            if not source.summary:
                errors.append(f"{source.source_id}: missing summary")
            if source.trust_tier is None:
                errors.append(f"{source.source_id}: trust_tier not assigned")
        return errors
