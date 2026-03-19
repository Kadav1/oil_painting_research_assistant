"""
citation_utils.py — Citation string assembly from chunk and source metadata.

Citations are grounded in retrieved chunk metadata only.
Never fabricate citation information not present in metadata.
"""

from __future__ import annotations

from typing import Optional


def build_citation(
    source_title: str,
    citation_format: str,
    page_range: Optional[str] = None,
    section_path: Optional[str] = None,
    source_url: Optional[str] = None,
    source_type: Optional[str] = None,
    case_specificity: Optional[str] = None,
) -> str:
    """
    Build a citation string from available metadata.

    Degrades gracefully if fields are missing.
    Never appends placeholder text like '[citation needed]'.
    """
    parts: list[str] = []

    # Primary citation text (from source record citation_format field)
    if citation_format:
        parts.append(citation_format)
    elif source_title:
        parts.append(source_title)

    # Location within source
    if page_range:
        parts.append(f"pp. {page_range}")
    elif section_path:
        readable = section_path.replace("_", " ").replace(".", " › ")
        parts.append(f"§ {readable}")

    # URL if available
    if source_url:
        parts.append(f"<{source_url}>")

    # Scope qualifiers
    qualifiers: list[str] = []
    if source_type in ("tds", "product_catalog", "sds"):
        qualifiers.append("manufacturer data")
    if case_specificity == "case_specific":
        qualifiers.append("case-specific")

    base = " — ".join(parts) if parts else (source_title or "unknown source")
    if qualifiers:
        base = f"{base} [{', '.join(qualifiers)}]"

    return base


def format_citation_list(citations: list[str]) -> str:
    """Format a list of citation strings for display in an answer."""
    if not citations:
        return ""
    unique = list(dict.fromkeys(citations))  # preserve order, deduplicate
    return "\n".join(f"[{i + 1}] {c}" for i, c in enumerate(unique))


def citation_is_complete(
    citation_format: Optional[str],
    source_title: Optional[str],
) -> bool:
    """Return True if minimum citation data is present."""
    return bool(citation_format or source_title)
