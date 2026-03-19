"""
conflict_policy.py — Conflict detection and disclosure policy.

Implements rules from docs/policies/conflict_resolution_policy.md.
"""

from __future__ import annotations

from typing import Any

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.retrieval_models import ConflictNote

logger = get_logger(__name__)


def requires_disclosure(resolution_status: str) -> bool:
    """
    Return True if a conflict with this resolution_status must be disclosed in answers.

    Unresolved, deferred, and escalated conflicts require disclosure.
    """
    return resolution_status in (
        "unresolved",
        "deferred",
        "escalated",
        "resolved_disclosed_in_answer",
    )


def find_active_conflicts(
    chunk_ids_in_context: list[str],
    all_conflicts: list[dict[str, Any]],
) -> list[ConflictNote]:
    """
    Return ConflictNotes for conflicts where 2+ of the context chunks are involved.

    Only returns conflicts where requires_answer_disclosure is True.
    """
    context_set = set(chunk_ids_in_context)
    notes: list[ConflictNote] = []

    for conflict in all_conflicts:
        if not conflict.get("requires_answer_disclosure", True):
            continue
        entity_ids = set(conflict.get("entity_ids", []))
        overlap = entity_ids.intersection(context_set)
        if len(overlap) >= 2:  # at least 2 conflicting entities appear in context
            notes.append(ConflictNote(
                conflict_id=conflict["conflict_id"],
                topic=conflict.get("topic", ""),
                entity_ids_in_context=list(overlap),
                requires_disclosure=True,
                summary=conflict.get("summary", ""),
            ))

    return notes


def format_conflict_disclosure(conflict_note: ConflictNote) -> str:
    """Format a ConflictNote into a disclosure sentence for answer generation."""
    if conflict_note.summary:
        return f"Note: sources disagree on {conflict_note.topic!r}: {conflict_note.summary}"
    return f"Note: sources disagree on {conflict_note.topic!r} — presenting multiple perspectives."


def preferred_source_for_conflict(conflict: dict[str, Any]) -> str | None:
    """
    Return the preferred source/value for a resolved conflict, or None.

    Used by the answer generator to weight conflicting chunks.
    """
    if conflict.get("resolution_status") == "resolved_with_preferred":
        return conflict.get("preferred_value_or_source")
    return None
