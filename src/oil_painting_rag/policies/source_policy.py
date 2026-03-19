"""
source_policy.py — Source acquisition and trust policy enforcement.

Implements rules from docs/policies/source_acquisition_policy.md and
docs/foundation/source_hierarchy.md.
"""

from __future__ import annotations

from typing import Optional

from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

# Trust tier mapping per source_hierarchy.md and controlled_vocabulary.json
FAMILY_DEFAULT_TIER: dict[str, int] = {
    "museum_conservation": 1,
    "pigment_reference": 2,
    "manufacturer": 3,
    "historical_practice": 4,
    "color_theory": 5,
    "scientific_paper": 2,  # scientific papers rank alongside pigment reference
}

# Minimum priority score to recommend for ingestion
MIN_PRIORITY_SCORE_FOR_INGESTION: int = 8


def infer_trust_tier(source_family: str) -> Optional[int]:
    """
    Infer the default trust tier from source_family.

    Returns None if family is unrecognized (reviewer must assign explicitly).
    """
    return FAMILY_DEFAULT_TIER.get(source_family)


def compute_priority_score(
    authority_score: Optional[int],
    extractability_score: Optional[int],
    coverage_value_score: Optional[int],
    density_score: Optional[int],
) -> Optional[int]:
    """
    Compute composite priority score as sum of component scores.

    Returns None if any component score is missing.
    Range: 0–20 (sum of four 0–5 scores).
    """
    scores = [authority_score, extractability_score, coverage_value_score, density_score]
    if any(s is None for s in scores):
        return None
    return sum(scores)  # type: ignore[arg-type]


def is_ready_for_ingestion(
    source_family: str,
    trust_tier: Optional[int],
    priority_score: Optional[int],
) -> tuple[bool, str]:
    """
    Check whether a source meets the minimum criteria for ingestion.

    Returns (ready, reason_if_not_ready).
    """
    if source_family not in FAMILY_DEFAULT_TIER:
        return False, f"Unknown source_family: {source_family!r}"
    if trust_tier is None:
        return False, "trust_tier not assigned"
    if priority_score is None:
        return False, "priority_score not computed (missing component scores)"
    if priority_score < MIN_PRIORITY_SCORE_FOR_INGESTION:
        return False, f"priority_score {priority_score} below minimum {MIN_PRIORITY_SCORE_FOR_INGESTION}"
    return True, ""


def validate_source_id_format(source_id: str) -> bool:
    """Validate source_id matches SRC-{FAMILY_CODE}-{NNN} format."""
    import re
    return bool(re.match(r"^SRC-[A-Z]{2,4}-\d{3,}$", source_id))


def source_tier_label(tier: int) -> str:
    """Return a human-readable label for a trust tier."""
    labels = {
        1: "Tier 1 — Museum/Conservation",
        2: "Tier 2 — Pigment Reference / Scientific",
        3: "Tier 3 — Manufacturer",
        4: "Tier 4 — Historical Practice",
        5: "Tier 5 — Color Theory / Teaching",
    }
    return labels.get(tier, f"Tier {tier}")
