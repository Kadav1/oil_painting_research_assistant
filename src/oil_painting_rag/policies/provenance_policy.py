"""
provenance_policy.py — Rules for metadata provenance tracking and trust assessment.

Implements rules from docs/policies/metadata_provenance_rules.md.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.utils.hash_utils import make_provenance_id

logger = get_logger(__name__)

# Provenance types that require human review before being treated as authoritative
REQUIRES_REVIEW: frozenset[str] = frozenset({
    "model_suggested",
    "rule_inferred",
})

# Provenance types that are considered authoritative without additional review
AUTHORITATIVE_WITHOUT_REVIEW: frozenset[str] = frozenset({
    "manual_reviewed",
    "manual_overridden",
    "manual_entered",
})


def is_authoritative(provenance_type: str, review_status: str) -> bool:
    """
    Return True if a field value can be treated as authoritative.

    model_suggested and rule_inferred require review_status == "reviewed" or "approved".
    manual_entered/reviewed/overridden are authoritative regardless.
    """
    if provenance_type in AUTHORITATIVE_WITHOUT_REVIEW:
        return True
    if provenance_type in REQUIRES_REVIEW:
        return review_status in ("reviewed", "approved")
    # extracted, derived, imported — treated as authoritative if not in review queue
    return review_status not in ("draft", "pending_review")


def make_provenance_record(
    entity_type: str,
    entity_id: str,
    field_name: str,
    value: Any,
    provenance_type: str,
    provenance_method: str,
    confidence: str,
    updated_by: str,
    review_status: str = "draft",
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """
    Build a provenance record dict conforming to field_provenance_schema.json.
    """
    now = datetime.now(tz=timezone.utc).isoformat()
    return {
        "provenance_id": make_provenance_id(entity_id, field_name),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "field_name": field_name,
        "value": value,
        "provenance_type": provenance_type,
        "provenance_method": provenance_method,
        "confidence": confidence,
        "review_status": review_status,
        "override_status": "original",
        "original_value": None,
        "last_updated_at": now,
        "last_updated_by": updated_by,
        "notes": notes,
    }


def make_override_record(
    existing: dict[str, Any],
    new_value: Any,
    updated_by: str,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a provenance record that overrides a previous value.

    Preserves the original value in original_value.
    """
    now = datetime.now(tz=timezone.utc).isoformat()
    return {
        **existing,
        "value": new_value,
        "provenance_type": "manual_overridden",
        "provenance_method": "manual_entry",
        "review_status": "reviewed",
        "override_status": "overridden",
        "original_value": existing.get("value"),
        "last_updated_at": now,
        "last_updated_by": updated_by,
        "notes": notes,
    }


def assess_metadata_trustworthiness(
    field_name: str,
    provenance_type: str,
    review_status: str,
    confidence: str,
) -> str:
    """
    Return a trustworthiness label: 'high' | 'medium' | 'low' | 'unverified'.

    Used internally for retrieval weighting decisions.
    """
    if is_authoritative(provenance_type, review_status):
        if confidence == "high":
            return "high"
        elif confidence == "medium":
            return "medium"
        else:
            return "low"
    return "unverified"
