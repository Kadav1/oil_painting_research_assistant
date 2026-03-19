"""
classifier.py — Query classification for the Oil Painting Research Assistant.

Classifies incoming queries to infer:
- answer_mode(s): Studio, Conservation, Art History, Color Analysis, Product Comparison
- domains: pigment, binder, conservation, historical_practice, color_theory, product, technique
- question_types: from controlled_vocabulary.question_type

Classification method: keyword_rules (deterministic, no LLM dependency).
The classification result drives metadata filter construction and reranking.
"""

from __future__ import annotations

import re
from typing import Any

from oil_painting_rag.models.retrieval_models import QueryClassification
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Keyword rule tables
# All values must match controlled_vocabulary.json exactly
# ---------------------------------------------------------------------------

_MODE_KEYWORDS: dict[str, list[str]] = {
    "Studio": [
        "mix", "mixing", "muddy", "opacity", "transparency", "drying",
        "ground", "gesso", "medium", "varnish", "fat over lean", "lean",
        "underpainting", "glaze", "scumble", "how to paint", "studio",
        "handling", "oil content", "retouch",
    ],
    "Conservation": [
        "conserv", "restoration", "degradation", "failure", "yellowing",
        "cracking", "delamination", "brittleness", "zinc white problem",
        "museum", "institution", "examination", "treatment", "binding media",
        "fading", "darkening", "structural",
    ],
    "Art History": [
        "historical", "history", "renaissance", "baroque", "flemish",
        "venetian", "dutch", "17th century", "18th century", "medieval",
        "period", "historical plausibility", "would have used", "era",
        "period recipe", "treatise", "cennini", "de mayerne",
    ],
    "Color Analysis": [
        "color", "colour", "hue", "saturation", "value", "chroma",
        "optical", "temperature", "warm", "cool", "complementary",
        "color wheel", "munsell", "tint", "shade", "tone", "neutral",
        "simultaneous contrast",
    ],
    "Product Comparison": [
        "brand", "manufacturer", "winsor", "gamblin", "schmincke",
        "old holland", "williamsburg", "michael harding", "rembrandt",
        "product", "tds", "formulation", "compare", "difference between",
        "which brand", "series",
    ],
}

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "pigment": [
        "pigment", "pigments", "pb29", "pw1", "pw4", "pw6", "pr",
        "ultramarine", "cadmium", "lead white", "zinc white", "titanium",
        "lapis lazuli", "vermilion", "ochre", "earth", "oxide", "lake",
        "prussian blue", "viridian",
    ],
    "binder": [
        "binder", "oil", "linseed", "walnut", "poppy", "alkyd",
        "medium", "damar", "stand oil", "resin", "wax", "turpentine",
        "solvent", "mineral spirits",
    ],
    "conservation": [
        "conserv", "degradation", "failure", "yellowing", "crack",
        "delamination", "museum", "treatment", "examination", "restoration",
    ],
    "historical_practice": [
        "historical", "history", "period", "treatise", "baroque",
        "renaissance", "flemish", "dutch", "venetian",
    ],
    "color_theory": [
        "color theory", "colour theory", "optical", "simultaneous contrast",
        "munsell", "itten", "albers", "color wheel",
    ],
    "product": [
        "brand", "manufacturer", "tds", "product", "formulation",
        "series", "winsor", "gamblin", "schmincke",
    ],
    "technique": [
        "technique", "method", "approach", "process", "procedure",
        "how to", "application", "layering",
    ],
}

_QUESTION_TYPE_KEYWORDS: dict[str, list[str]] = {
    "pigment_chemistry": ["pigment", "chemical", "compound", "structure", "molecule"],
    "pigment_handling": ["handling", "mixing", "opacity", "grinding", "oil content"],
    "pigment_history": ["history", "historical", "medieval", "ancient", "period"],
    "binder_chemistry": ["binder", "drying oil", "polymerize", "saponification", "alkyd"],
    "binder_handling": ["medium", "fat over lean", "turpentine", "solvent"],
    "conservation_risk": ["risk", "safety", "archival", "longevity", "lightfast"],
    "conservation_failure": ["failure", "degradation", "crack", "delaminate", "yellow"],
    "degradation_mechanism": ["mechanism", "degradation", "photo", "oxidize", "react"],
    "historical_plausibility": ["would have", "could have", "plausible", "period", "available"],
    "period_practice": ["practice", "historical technique", "period recipe", "treatise"],
    "color_mixing": ["mix", "mixing", "muddy", "shadow", "complement"],
    "color_analysis": ["analyze", "analysis", "color temperature", "hue", "value"],
    "optical_behavior": ["optical", "transparency", "opacity", "glaze", "scumble"],
    "product_comparison": ["compare", "difference", "brand", "which", "better"],
    "product_specification": ["tds", "specification", "formulation", "series"],
    "terminology_definition": ["what is", "define", "definition", "mean", "means"],
    "technique_advice": ["how to", "technique", "advice", "should i", "recommend"],
}


def classify_query(query: str) -> QueryClassification:
    """
    Classify a query using keyword rules.

    Returns a QueryClassification with inferred modes, domains, and question types.
    Multiple modes/domains/question_types may apply.
    """
    q_lower = query.lower()

    inferred_modes = _match_keywords(q_lower, _MODE_KEYWORDS)
    inferred_domains = _match_keywords(q_lower, _DOMAIN_KEYWORDS)
    inferred_question_types = _match_keywords(q_lower, _QUESTION_TYPE_KEYWORDS)

    # Defaults if nothing matched
    if not inferred_modes:
        inferred_modes = ["Studio"]
    if not inferred_domains:
        inferred_domains = ["mixed"]
    if not inferred_question_types:
        inferred_question_types = ["technique_advice"]

    logger.debug(
        "Query classification: modes=%s domains=%s qtypes=%s",
        inferred_modes, inferred_domains, inferred_question_types,
    )

    return QueryClassification(
        inferred_modes=inferred_modes,
        inferred_domains=inferred_domains,
        inferred_question_types=inferred_question_types,
        classification_method="keyword_rules",
    )


def _match_keywords(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    """Return all categories whose keywords appear in text."""
    matched: list[str] = []
    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text:
                matched.append(category)
                break
    return matched
