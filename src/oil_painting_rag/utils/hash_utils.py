"""
hash_utils.py — Stable ID generation and content hashing.

chunk_id format:  CHK-{source_id}-{index:03d}  e.g. CHK-SRC-MUS-001-001
source_id format: SRC-{FAMILY_CODE}-{NNN:03d}  e.g. SRC-MUS-001
trace_id format:  TRC-{timestamp}-{short_hash}
package_id:       PKG-{timestamp}-{short_hash}
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of the given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(text: str, length: int = 8) -> str:
    """Return the first `length` characters of the SHA-256 hex digest."""
    return sha256_hex(text)[:length]


def make_chunk_id(source_id: str, chunk_index: int) -> str:
    """
    Build a stable chunk_id from source_id and 0-based index.

    Format: CHK-{source_id}-{index:03d}
    Example: CHK-SRC-MUS-001-001  (for index 1)
    """
    return f"CHK-{source_id}-{chunk_index:03d}"


def make_provenance_id(entity_id: str, field_name: str) -> str:
    """
    Build a provenance record ID.

    Format: PRV-{entity_id}-{field_name}
    Example: PRV-SRC-MUS-001-trust_tier
    """
    return f"PRV-{entity_id}-{field_name}"


def make_trace_id() -> str:
    """
    Generate a unique retrieval trace ID.

    Format: TRC-{ISO_timestamp}-{short_hash_of_timestamp}
    """
    now = datetime.now(tz=timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    h = short_hash(now.isoformat())
    return f"TRC-{ts}-{h}"


def make_package_id() -> str:
    """
    Generate a unique context package ID.

    Format: PKG-{ISO_timestamp}-{short_hash_of_timestamp}
    """
    now = datetime.now(tz=timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    h = short_hash(now.isoformat())
    return f"PKG-{ts}-{h}"


def make_review_id(entity_id: str, sequence: int) -> str:
    """
    Build a review record ID.

    Format: REV-{entity_id}-{sequence:03d}
    Example: REV-SRC-MUS-001-001
    """
    return f"REV-{entity_id}-{sequence:03d}"


def make_conflict_id(sequence: int) -> str:
    """
    Build a conflict record ID.

    Format: CON-{sequence:03d}
    """
    return f"CON-{sequence:03d}"


def make_duplicate_cluster_id(entity_type: str, sequence: int) -> str:
    """
    Build a duplicate cluster ID.

    Format: DUP-{entity_type_code}-{sequence:03d}
    entity_type_code: "SRC" for source, "CHK" for chunk
    """
    code = "SRC" if entity_type == "source" else "CHK"
    return f"DUP-{code}-{sequence:03d}"


def content_hash(text: str) -> str:
    """Return a stable hash of chunk text for deduplication detection."""
    return sha256_hex(text.strip().lower())
