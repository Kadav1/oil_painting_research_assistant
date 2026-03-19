"""
retrieval_policy.py — Retrieval gate and filter policy enforcement.

Implements rules from docs/policies/retrieval_policy_v1.md and
schemas/approval_state_schema.json.
"""

from __future__ import annotations

from typing import Any

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

# Approval state ordinals (higher = more permissive)
APPROVAL_STATE_ORDER: dict[str, int] = {
    "not_approved": 0,
    "internal_draft_only": 1,
    "testing_only": 2,
    "retrieval_allowed": 3,
    "live_allowed": 4,
}


def approval_state_allows_retrieval(approval_state: str, gate: str) -> bool:
    """
    Return True if a chunk's approval_state meets or exceeds the gate requirement.

    gate: "retrieval_allowed" | "live_allowed" | "testing_only"
    """
    chunk_level = APPROVAL_STATE_ORDER.get(approval_state, 0)
    gate_level = APPROVAL_STATE_ORDER.get(gate, 3)
    return chunk_level >= gate_level


def build_approval_filter(gate: str = "retrieval_allowed") -> dict[str, Any]:
    """
    Build the ChromaDB where-clause filter for the given gate.

    Per approval_state_schema.json retrieval_gate_filter.
    """
    gate_map: dict[str, list[str]] = {
        "live_allowed": ["live_allowed"],
        "retrieval_allowed": ["retrieval_allowed", "live_allowed"],
        "testing_only": ["testing_only", "retrieval_allowed", "live_allowed"],
    }
    states = gate_map.get(gate, gate_map["retrieval_allowed"])
    if len(states) == 1:
        return {"approval_state": states[0]}
    return {"approval_state": {"$in": states}}


def merge_filters(
    base_filter: dict[str, Any],
    extra_filter: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge two ChromaDB filter dicts using $and.

    If either is empty, returns the non-empty one.
    """
    if not base_filter:
        return extra_filter
    if not extra_filter:
        return base_filter
    return {"$and": [base_filter, extra_filter]}


def domain_filter(domains: list[str]) -> dict[str, Any]:
    """Build a ChromaDB domain filter from a list of domain values."""
    if not domains:
        return {}
    if len(domains) == 1:
        return {"domain": domains[0]}
    return {"domain": {"$in": domains}}


def source_family_filter(families: list[str]) -> dict[str, Any]:
    """Build a ChromaDB source_family filter."""
    if not families:
        return {}
    if len(families) == 1:
        return {"source_family": families[0]}
    return {"source_family": {"$in": families}}


def trust_tier_filter(max_tier: int) -> dict[str, Any]:
    """Build a ChromaDB filter to restrict to trust_tier <= max_tier (lower = better)."""
    return {"trust_tier": {"$lte": max_tier}}


def chunk_type_filter(types: list[str]) -> dict[str, Any]:
    """Build a ChromaDB chunk_type filter."""
    if not types:
        return {}
    if len(types) == 1:
        return {"chunk_type": types[0]}
    return {"chunk_type": {"$in": types}}


def validate_retrieval_gate(gate: str) -> str:
    """Validate and return the gate; raise ValueError if unknown."""
    valid = {"live_allowed", "retrieval_allowed", "testing_only"}
    if gate not in valid:
        raise ValueError(f"Unknown retrieval gate {gate!r}. Valid: {valid}")
    return gate


def chunk_passes_gate(chunk_approval_state: str, gate: str) -> bool:
    """Convenience wrapper for approval_state_allows_retrieval."""
    return approval_state_allows_retrieval(chunk_approval_state, gate)
