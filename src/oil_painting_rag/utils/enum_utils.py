"""
enum_utils.py — Controlled vocabulary loading and enum validation.

All enum values come from vocab/controlled_vocabulary.json.
This module loads that file once and exposes validation helpers.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from oil_painting_rag.config import CONTROLLED_VOCABULARY_PATH
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def load_controlled_vocabulary() -> dict[str, Any]:
    """Load and cache the controlled vocabulary JSON."""
    path = CONTROLLED_VOCABULARY_PATH
    if not path.exists():
        logger.warning("controlled_vocabulary.json not found at %s", path)
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_enum_values(key: str) -> list[str]:
    """
    Return the list of valid string values for a vocabulary key.

    For keys whose values are integers (trust_tier), returns strings of those ints.
    """
    vocab = load_controlled_vocabulary()
    entry = vocab.get(key, {})
    values = entry.get("values", [])
    return [str(v) for v in values]


def is_valid_enum(key: str, value: str) -> bool:
    """Return True if `value` is a valid member of the enum for `key`."""
    return str(value) in get_enum_values(key)


def validate_enum(key: str, value: str, field_name: str = "") -> str:
    """
    Return `value` if it is a valid enum member; raise ValueError otherwise.
    """
    if not is_valid_enum(key, value):
        label = field_name or key
        valid = get_enum_values(key)
        raise ValueError(
            f"Invalid value {value!r} for {label!r}. Valid values: {valid}"
        )
    return value


def validate_enum_list(key: str, values: list[str], field_name: str = "") -> list[str]:
    """Validate each item in a list against a controlled vocabulary enum."""
    for v in values:
        validate_enum(key, v, field_name=field_name)
    return values


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------

def source_families() -> list[str]:
    return get_enum_values("source_family")


def source_types() -> list[str]:
    return get_enum_values("source_type")


def domains() -> list[str]:
    return get_enum_values("domain")


def question_types() -> list[str]:
    return get_enum_values("question_type")


def claim_types() -> list[str]:
    return get_enum_values("claim_type")


def case_specificities() -> list[str]:
    return get_enum_values("case_specificity")


def approval_states() -> list[str]:
    return get_enum_values("approval_state")


def review_statuses() -> list[str]:
    return get_enum_values("review_status")


def chunk_types() -> list[str]:
    return get_enum_values("chunk_type")


def citabilities() -> list[str]:
    return get_enum_values("citability")


def duplicate_statuses() -> list[str]:
    return get_enum_values("duplicate_status")


def answer_labels() -> list[str]:
    return get_enum_values("answer_label")


def answer_modes() -> list[str]:
    return get_enum_values("answer_mode")


def trust_tiers() -> list[int]:
    vocab = load_controlled_vocabulary()
    return list(vocab.get("trust_tier", {}).get("values", [1, 2, 3, 4, 5]))


def binder_vocab() -> list[str]:
    return get_enum_values("binder_vocabulary")


def historical_periods() -> list[str]:
    return get_enum_values("historical_period")


def quality_flags() -> list[str]:
    return get_enum_values("quality_flag")


def restriction_flags() -> list[str]:
    return get_enum_values("restriction_flag")


def provenance_types() -> list[str]:
    return get_enum_values("provenance_type")


def provenance_methods() -> list[str]:
    return get_enum_values("provenance_method")


def benchmark_categories() -> list[str]:
    return get_enum_values("benchmark_category")


def benchmark_difficulties() -> list[str]:
    return get_enum_values("benchmark_difficulty")
