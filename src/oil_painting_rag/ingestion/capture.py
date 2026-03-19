"""
capture.py — Source capture utilities.

Handles: recording capture metadata, writing raw files, updating
the source register with capture status flags.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.source_models import SourceRecord
from oil_painting_rag.policies.source_policy import (
    infer_trust_tier,
    validate_source_id_format,
)
from oil_painting_rag.storage.filesystem_store import FilesystemStore
from oil_painting_rag.storage.register_store import RegisterStore
from oil_painting_rag.utils.hash_utils import short_hash

logger = get_logger(__name__)


class SourceCapture:
    """
    Registers a new source and saves its raw file.

    Does NOT chunk or index — that is downstream pipeline work.
    """

    def __init__(self) -> None:
        self._fs = FilesystemStore()
        self._register = RegisterStore()

    def register_source(
        self,
        source_id: str,
        title: str,
        short_title: str,
        source_family: str,
        source_type: str,
        institution_or_publisher: str,
        domain: str,
        capture_method: str,
        access_type: str,
        raw_file_name: str,
        capture_date: Optional[str] = None,
        author: Optional[str] = None,
        publication_year: Optional[int] = None,
        source_url: Optional[str] = None,
        **kwargs,
    ) -> SourceRecord:
        """
        Create and register a new SourceRecord.

        Validates source_id format. Infers default trust_tier from source_family.
        Does NOT overwrite an existing source — call update_source for that.
        """
        if not validate_source_id_format(source_id):
            raise ValueError(
                f"source_id {source_id!r} does not match SRC-{{FAMILY_CODE}}-{{NNN}} format"
            )
        if self._register.source_exists(source_id):
            raise ValueError(f"Source {source_id} already registered. Use update_source().")

        capture_date = capture_date or datetime.now(tz=timezone.utc).date().isoformat()

        # Infer default trust tier from family if not provided
        trust_tier = kwargs.pop("trust_tier", None) or infer_trust_tier(source_family)

        record = SourceRecord(
            source_id=source_id,
            title=title,
            short_title=short_title,
            source_family=source_family,
            source_type=source_type,
            institution_or_publisher=institution_or_publisher,
            domain=domain,
            capture_method=capture_method,
            access_type=access_type,
            raw_file_name=raw_file_name,
            raw_file_path=str(cfg.RAW_DIR / source_id / raw_file_name),
            capture_date=capture_date,
            author=author,
            publication_year=publication_year,
            source_url=source_url,
            trust_tier=trust_tier,
            historical_period=kwargs.pop("historical_period", "not_applicable"),
            subdomain=kwargs.pop("subdomain", None),
            **kwargs,
        )

        self._register.save_source(record.model_dump())
        self._register.append_acquisition_log({
            "source_id": source_id,
            "title": title,
            "source_family": source_family,
            "source_type": source_type,
            "capture_date": capture_date,
            "capture_method": capture_method,
            "access_type": access_type,
        })

        logger.info("Registered source: %s — %s", source_id, short_title)
        return record

    def save_raw_file(
        self,
        source_id: str,
        filename: str,
        content: bytes,
    ) -> Path:
        """
        Save a raw file and update the source's raw_captured flag.
        """
        path = self._fs.save_raw_file(source_id, filename, content)

        rec = self._register.load_source(source_id)
        if rec:
            rec["raw_captured"] = True
            self._register.save_source(rec)

        return path

    def save_normalized_text(
        self,
        source_id: str,
        text: str,
    ) -> Path:
        """
        Save normalized markdown text and update normalized_text_created flag.
        """
        path = self._fs.save_clean_text(source_id, text)

        rec = self._register.load_source(source_id)
        if rec:
            rec["normalized_text_created"] = True
            self._register.save_source(rec)

        return path

    def mark_metadata_attached(self, source_id: str) -> None:
        rec = self._register.load_source(source_id)
        if rec:
            rec["metadata_attached"] = True
            self._register.save_source(rec)

    def mark_chunked(self, source_id: str) -> None:
        rec = self._register.load_source(source_id)
        if rec:
            rec["chunked"] = True
            self._register.save_source(rec)

    def mark_indexed(self, source_id: str) -> None:
        rec = self._register.load_source(source_id)
        if rec:
            rec["indexed"] = True
            self._register.save_source(rec)
