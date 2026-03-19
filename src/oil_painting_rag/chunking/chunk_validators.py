"""
chunk_validators.py — Validation for ChunkRecord objects.

Validates: required fields present, enum values valid, token bounds,
chunk_id format. Used after chunking and before indexing.
"""

from __future__ import annotations

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.utils.enum_utils import (
    is_valid_enum,
    approval_states,
    chunk_types,
    citabilities,
    case_specificities,
    duplicate_statuses,
    review_statuses,
)
import oil_painting_rag.config as cfg

logger = get_logger(__name__)


class ChunkValidationError(Exception):
    """Raised when a ChunkRecord fails validation."""


def validate_chunk(chunk: ChunkRecord, strict: bool = False) -> list[str]:
    """
    Validate a ChunkRecord. Return a list of error/warning strings.

    If strict=True, enum mismatches are errors. Otherwise they are warnings.
    Does NOT raise — collect all issues and return them.
    """
    issues: list[str] = []
    cid = chunk.chunk_id

    # chunk_id format check
    import re
    if not re.match(r"^CHK-SRC-[A-Z]+-\d{3,}-\d{3,}$", cid):
        issues.append(f"{cid}: chunk_id format invalid (expected CHK-SRC-XX-NNN-NNN)")

    # Required text content
    if not chunk.text or not chunk.text.strip():
        issues.append(f"{cid}: text is empty")

    if not chunk.source_id:
        issues.append(f"{cid}: source_id is missing")

    if not chunk.chunk_title:
        issues.append(f"{cid}: chunk_title is missing")

    # Token range
    if chunk.token_estimate < cfg.CHUNK_MIN_TOKENS:
        issues.append(
            f"{cid}: token_estimate {chunk.token_estimate} below minimum {cfg.CHUNK_MIN_TOKENS}"
        )
    if chunk.token_estimate > cfg.CHUNK_MAX_TOKENS * 2:
        issues.append(
            f"{cid}: token_estimate {chunk.token_estimate} suspiciously large"
        )

    # Enum validation
    enum_checks = [
        ("chunk_type", chunk.chunk_type, chunk_types()),
        ("approval_state", chunk.approval_state, approval_states()),
        ("citability", chunk.citability, citabilities()),
        ("case_specificity", chunk.case_specificity, case_specificities()),
        ("duplicate_status", chunk.duplicate_status, duplicate_statuses()),
        ("review_status", chunk.review_status, review_statuses()),
    ]
    for field, value, valid_values in enum_checks:
        if value not in valid_values:
            msg = f"{cid}: {field}={value!r} not in controlled vocabulary"
            issues.append(msg)

    # Source propagation fields
    if not chunk.source_family:
        issues.append(f"{cid}: source_family not propagated")
    if chunk.trust_tier not in (1, 2, 3, 4, 5):
        issues.append(f"{cid}: trust_tier {chunk.trust_tier} invalid")

    return issues


def validate_chunk_list(chunks: list[ChunkRecord]) -> tuple[list[ChunkRecord], list[str]]:
    """
    Validate a list of ChunkRecords.

    Returns (valid_chunks, all_issues).
    Chunks with critical errors (empty text, missing source_id) are excluded.
    """
    valid: list[ChunkRecord] = []
    all_issues: list[str] = []

    for chunk in chunks:
        issues = validate_chunk(chunk)
        all_issues.extend(issues)

        # Exclude chunks with critical errors
        critical = [i for i in issues if "text is empty" in i or "source_id is missing" in i]
        if critical:
            logger.warning("Excluding invalid chunk %s: %s", chunk.chunk_id, critical)
        else:
            valid.append(chunk)

    return valid, all_issues


def flag_low_quality(chunk: ChunkRecord) -> ChunkRecord:
    """
    Add quality flags to a chunk that has obvious issues.

    Returns the (potentially modified) chunk.
    """
    flags = list(chunk.quality_flags)

    if chunk.token_estimate < cfg.CHUNK_MIN_TOKENS * 2:
        if "low_density" not in flags:
            flags.append("low_density")

    if not chunk.citation_format and not chunk.source_title:
        if "citation_unclear" not in flags:
            flags.append("citation_unclear")

    if chunk.case_specificity == "case_specific":
        if "case_specific" not in flags:
            flags.append("case_specific")

    # Rebuild with updated flags
    return chunk.model_copy(update={"quality_flags": flags})
