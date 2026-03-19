"""
provenance_models.py — Pydantic v2 models for provenance, deduplication,
conflict records, and review records.

All models map to their respective JSON schemas.
Provenance records are stored in the metadata store, not ChromaDB.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Field-level provenance
# ---------------------------------------------------------------------------

class FieldProvenance(BaseModel):
    """
    Per-field provenance record tracking how a metadata value was determined.

    Maps to field_provenance_schema.json.
    Keyed by entity_id + field_name.
    """

    provenance_id: str = Field(
        ...,
        description="Format: PRV-{entity_id}-{field_name}",
    )
    entity_type: str           # "source" | "chunk"
    entity_id: str
    field_name: str
    value: Any

    provenance_type: str       # controlled_vocabulary.provenance_type
    provenance_method: str     # controlled_vocabulary.provenance_method
    confidence: str            # controlled_vocabulary.confidence_level
    review_status: str         # controlled_vocabulary.review_status
    override_status: str       # controlled_vocabulary.override_status

    original_value: Optional[Any] = None  # populated only when overridden
    last_updated_at: str = ""  # ISO 8601 datetime
    last_updated_by: str = ""
    notes: Optional[str] = None

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Duplicate cluster
# ---------------------------------------------------------------------------

class DuplicateCluster(BaseModel):
    """
    Groups two or more sources or chunks identified as duplicates.

    Maps to duplicate_cluster_schema.json.
    """

    cluster_id: str = Field(
        ...,
        description="Format: DUP-{entity_type_code}-{NNN}",
    )
    entity_type: str           # "source" | "chunk"
    member_ids: list[str] = Field(default_factory=list)
    canonical_id: str
    duplicate_type: str        # controlled_vocabulary.duplicate_type
    reason: str
    reviewer: str
    decision_date: str         # ISO 8601 date
    status: str = "open"       # "open" | "resolved" | "needs_revision"
    notes: Optional[str] = None

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Conflict record
# ---------------------------------------------------------------------------

class ConflictRecord(BaseModel):
    """
    Logs a known disagreement between sources or chunks.

    Maps to conflict_record_schema.json.
    Drives disclosure behavior in answer generation.
    """

    conflict_id: str = Field(
        ...,
        description="Format: CON-{NNN}",
    )
    conflict_type: str         # controlled_vocabulary.conflict_type
    entity_type: str           # "source" | "chunk" | "mixed"
    entity_ids: list[str] = Field(default_factory=list)
    topic: str
    summary: str
    requires_answer_disclosure: bool = True
    resolution_status: str     # controlled_vocabulary.resolution_status
    preferred_value_or_source: Optional[str] = None
    resolution_reason: Optional[str] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[str] = None  # ISO 8601
    created_at: str = ""       # ISO 8601
    notes: Optional[str] = None

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Review record
# ---------------------------------------------------------------------------

class ReviewRecord(BaseModel):
    """
    One review event record per review action on a source or chunk.

    Maps to review_record_schema.json.
    Forms the audit trail for metadata changes and approval state transitions.
    """

    review_id: str = Field(
        ...,
        description="Format: REV-{entity_id}-{NNN}",
    )
    entity_type: str     # "source" | "chunk"
    entity_id: str
    review_stage: str    # "intake_review" | "metadata_review" | "chunk_review" | ...
    reviewer: str
    review_date: str     # ISO 8601 datetime
    action: str          # "approved" | "rejected" | "returned_for_revision" | ...
    status_before: str
    status_after: str
    summary_of_findings: str

    field_changes: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    next_action: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"extra": "forbid"}
