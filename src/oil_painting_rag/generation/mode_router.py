"""
mode_router.py — Answer mode selection for the Oil Painting Research Assistant.

Maps query classification to a primary answer mode (Studio, Conservation,
Art History, Color Analysis, Product Comparison). Mode shifts emphasis in
the prompt, not facts.
"""

from __future__ import annotations

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.retrieval_models import QueryClassification

logger = get_logger(__name__)

# Canonical mode names (match controlled_vocabulary.answer_mode)
MODE_STUDIO = "Studio"
MODE_CONSERVATION = "Conservation"
MODE_ART_HISTORY = "Art History"
MODE_COLOR_ANALYSIS = "Color Analysis"
MODE_PRODUCT_COMPARISON = "Product Comparison"

ALL_MODES = [
    MODE_STUDIO,
    MODE_CONSERVATION,
    MODE_ART_HISTORY,
    MODE_COLOR_ANALYSIS,
    MODE_PRODUCT_COMPARISON,
]

# Mapping from inferred_modes (classification output) → canonical mode name
_MODE_ALIAS_MAP: dict[str, str] = {
    "studio": MODE_STUDIO,
    "Studio": MODE_STUDIO,
    "conservation": MODE_CONSERVATION,
    "Conservation": MODE_CONSERVATION,
    "art_history": MODE_ART_HISTORY,
    "Art History": MODE_ART_HISTORY,
    "art history": MODE_ART_HISTORY,
    "color_analysis": MODE_COLOR_ANALYSIS,
    "Color Analysis": MODE_COLOR_ANALYSIS,
    "color analysis": MODE_COLOR_ANALYSIS,
    "product_comparison": MODE_PRODUCT_COMPARISON,
    "Product Comparison": MODE_PRODUCT_COMPARISON,
    "product comparison": MODE_PRODUCT_COMPARISON,
}

# Priority ordering when multiple modes are inferred (first = highest priority)
_MODE_PRIORITY: list[str] = [
    MODE_CONSERVATION,
    MODE_ART_HISTORY,
    MODE_PRODUCT_COMPARISON,
    MODE_COLOR_ANALYSIS,
    MODE_STUDIO,
]


def select_mode(classification: QueryClassification) -> str:
    """
    Select the primary answer mode from a query classification.

    Rules:
    - Normalize inferred_modes aliases to canonical mode names.
    - If exactly one mode, return it.
    - If multiple, return the highest-priority mode per _MODE_PRIORITY.
    - If none, fall back to MODE_STUDIO (most general).
    """
    canonical_modes: list[str] = []
    for raw_mode in classification.inferred_modes:
        canonical = _MODE_ALIAS_MAP.get(raw_mode)
        if canonical:
            canonical_modes.append(canonical)
        else:
            logger.debug("Unknown inferred mode %r — ignoring", raw_mode)

    if not canonical_modes:
        logger.debug("No recognizable modes — defaulting to Studio")
        return MODE_STUDIO

    if len(canonical_modes) == 1:
        return canonical_modes[0]

    # Multiple modes: pick by priority
    for priority_mode in _MODE_PRIORITY:
        if priority_mode in canonical_modes:
            return priority_mode

    return canonical_modes[0]


def mode_emphasis_note(mode: str) -> str:
    """
    Return a brief note about the primary source tier emphasis for a mode.

    Used by the prompt builder to add mode-specific context.
    """
    notes: dict[str, str] = {
        MODE_STUDIO: (
            "Emphasize practical handling and material behavior. "
            "Prioritize Tier 2 (pigment reference) and Tier 3 (manufacturer) sources."
        ),
        MODE_CONSERVATION: (
            "Emphasize long-term stability, degradation risk, and archival concerns. "
            "Prioritize Tier 1 (museum conservation) sources. "
            "State uncertainty clearly when Tier 1 evidence is absent."
        ),
        MODE_ART_HISTORY: (
            "Emphasize historical plausibility and documented period practice. "
            "Prioritize Tier 1 and Tier 4 (historical practice) sources. "
            "Scope claims as case-specific where appropriate."
        ),
        MODE_COLOR_ANALYSIS: (
            "Emphasize hue, value, chroma, and mixture behavior. "
            "Prioritize Tier 2 (pigment reference) and Tier 5 (color theory) sources. "
            "Explain in painterly terms while preserving technical clarity."
        ),
        MODE_PRODUCT_COMPARISON: (
            "Emphasize modern product data. "
            "Prioritize Tier 3 (manufacturer) sources. "
            "Label all product-specific information clearly — "
            "do not generalize to universal chemistry."
        ),
    }
    return notes.get(mode, "")
