"""
filters.py — Filter construction for ChromaDB and retrieval gating.

Builds ChromaDB where-clause filters from query classification results
and caller-supplied constraints. Enforces approval_state gating.
"""

from __future__ import annotations

from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.models.retrieval_models import QueryClassification
from oil_painting_rag.policies.retrieval_policy import (
    build_approval_filter,
    domain_filter,
    merge_filters,
)
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


def build_retrieval_filters(
    classification: QueryClassification,
    approval_gate: str = cfg.DEFAULT_RETRIEVAL_GATE,
    extra_filters: Optional[dict[str, Any]] = None,
    restrict_to_domains: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Build the ChromaDB where-clause filter for a retrieval request.

    Always includes approval_state gating.
    Optionally adds domain and other filters from classification.

    Args:
        classification: Query classification result.
        approval_gate: Minimum approval state (retrieval_allowed | live_allowed | testing_only).
        extra_filters: Additional caller-supplied filters.
        restrict_to_domains: If set, override classification domains with these.

    Returns:
        A ChromaDB-compatible where-clause dict, or {} if no filters needed.
    """
    # 1. Approval gate — always applied
    base = build_approval_filter(approval_gate)

    # 2. Domain filter — only applied if domains are narrow and specific
    domains = restrict_to_domains or _narrow_domains(classification.inferred_domains)
    if domains and "mixed" not in domains:
        base = merge_filters(base, domain_filter(domains))

    # 3. Extra caller-supplied filters
    if extra_filters:
        base = merge_filters(base, extra_filters)

    return base


def _narrow_domains(domains: list[str]) -> list[str]:
    """
    Return domains only if they are specific enough to warrant filtering.

    If 4+ domains are inferred, the query is broad — don't filter by domain.
    """
    BROAD_THRESHOLD = 4
    if len(domains) >= BROAD_THRESHOLD:
        return []
    if "mixed" in domains:
        return []
    return domains


def build_source_type_filter(source_types: list[str]) -> dict[str, Any]:
    """Build a filter for specific source types."""
    if not source_types:
        return {}
    if len(source_types) == 1:
        return {"source_type": source_types[0]}
    return {"source_type": {"$in": source_types}}


def exclude_duplicate_clusters(cluster_ids: list[str]) -> dict[str, Any]:
    """
    Build a filter that excludes chunks belonging to known duplicate clusters.

    Uses the canonical member only — non-canonical duplicates are suppressed.
    """
    if not cluster_ids:
        return {}
    # Filter out confirmed_duplicate chunks
    return {"duplicate_status": {"$nin": ["confirmed_duplicate", "superseded"]}}


def historical_period_filter(periods: list[str]) -> dict[str, Any]:
    """Build a filter for historical period scope."""
    if not periods:
        return {}
    if len(periods) == 1:
        return {"historical_period": periods[0]}
    return {"historical_period": {"$in": periods}}


def quality_filter_exclude_flags(flags_to_exclude: list[str]) -> dict[str, Any]:
    """
    Build a filter that would exclude chunks with certain quality flags.

    Note: pipe-encoded list fields cannot be filtered with $nin in ChromaDB.
    This is a post-retrieval filter — use after fetching candidates.
    """
    # ChromaDB cannot filter on pipe-encoded list fields with $nin
    # Return empty; post-retrieval filtering is done in the retrieval layer
    return {}
