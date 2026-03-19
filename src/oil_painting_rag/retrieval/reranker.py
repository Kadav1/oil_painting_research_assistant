"""
reranker.py — Multi-factor reranking for the Oil Painting Research Assistant.

Reranking considers 11 factors per spec:
  1. semantic_relevance    (from vector cosine similarity)
  2. lexical_relevance     (from BM25 score)
  3. trust_tier            (source hierarchy — tier 1 = best)
  4. review_state          (approved > reviewed > draft)
  5. domain_fit            (does chunk domain match query domain?)
  6. question_type_fit     (does chunk support inferred question types?)
  7. case_specificity      (broadly_applicable preferred over case_specific for general queries)
  8. quality_flags         (penalize chunks with quality issues)
  9. citability            (directly_citable > paraphrase_only)
  10. retrieval_weight_hint (optional manual boost from reviewer)
  11. duplicate_status     (penalize confirmed_duplicate / superseded)

All weights come from config.py.
"""

from __future__ import annotations

from typing import Any

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.retrieval_models import MergedCandidate, QueryClassification

logger = get_logger(__name__)

# Approval state scores (higher = better)
_APPROVAL_SCORES: dict[str, float] = {
    "live_allowed": 1.0,
    "retrieval_allowed": 0.8,
    "testing_only": 0.5,
    "internal_draft_only": 0.1,
    "not_approved": 0.0,
}

# Review status scores
_REVIEW_SCORES: dict[str, float] = {
    "approved": 1.0,
    "reviewed": 0.85,
    "under_review": 0.6,
    "pending_review": 0.5,
    "needs_revision": 0.3,
    "draft": 0.2,
    "rejected": 0.0,
}

# Citability scores
_CITABILITY_SCORES: dict[str, float] = {
    "directly_citable": 1.0,
    "paraphrase_only": 0.7,
    "internal_use_only": 0.3,
    "not_citable": 0.1,
}

# Case specificity modifier (when query is general, case-specific is less useful)
_CASE_SPECIFICITY_GENERAL_SCORES: dict[str, float] = {
    "broadly_applicable": 1.0,
    "mixed": 0.8,
    "case_specific": 0.5,
    "unknown": 0.7,
}

# Trust tier scores (tier 1 = best = 1.0)
def _tier_score(tier: int) -> float:
    return max(0.1, 1.0 - (tier - 1) * 0.2)

# Quality flag penalties
_QUALITY_PENALTIES: dict[str, float] = {
    "ocr_suspect": -0.15,
    "table_messy": -0.05,
    "citation_unclear": -0.10,
    "low_density": -0.10,
    "duplicate_suspect": -0.10,
    "needs_manual_review": -0.05,
}

# Duplicate status penalties
_DUPLICATE_PENALTIES: dict[str, float] = {
    "unique": 0.0,
    "canonical": 0.0,
    "format_variant_retained": -0.05,
    "duplicate_suspect": -0.10,
    "confirmed_duplicate": -0.50,
    "superseded": -0.50,
}


class Reranker:
    """
    Multi-factor reranker for hybrid retrieval results.

    Computes a composite score from 11 factors weighted by config.py values.
    Does not replace vector or lexical scores — augments them.
    """

    def rerank(
        self,
        query: str,
        chunks: list[ChunkRecord],
        merged_pool: list[MergedCandidate],
        classification: QueryClassification,
    ) -> list[dict[str, Any]]:
        """
        Rerank chunks by composite score.

        Returns list of dicts: {chunk_id, rerank_score, ...} sorted descending.
        """
        if not chunks:
            return []

        # Build lookup maps
        merged_by_id: dict[str, MergedCandidate] = {m.chunk_id: m for m in merged_pool}
        chunks_by_id: dict[str, ChunkRecord] = {c.chunk_id: c for c in chunks}

        # Normalize merge scores to [0, 1]
        merge_scores = {m.chunk_id: m.merge_score for m in merged_pool}
        max_merge = max(merge_scores.values()) if merge_scores else 1.0
        min_merge = min(merge_scores.values()) if merge_scores else 0.0
        score_range = max_merge - min_merge if max_merge > min_merge else 1.0

        scored: list[dict[str, Any]] = []
        for chunk in chunks:
            cid = chunk.chunk_id
            merged = merged_by_id.get(cid)
            if merged is None:
                continue

            # Normalize merge_score → semantic + lexical proxy
            norm_merge = (merged.merge_score - min_merge) / score_range

            # Decompose into semantic vs lexical contribution
            has_vector = "vector" in (merged.sources or [])
            has_lexical = "lexical" in (merged.sources or [])
            semantic_boost = norm_merge if has_vector else 0.0
            lexical_boost = norm_merge if has_lexical else 0.0

            # Factor 1 + 2: semantic + lexical relevance
            score = (
                cfg.RERANK_WEIGHT_SEMANTIC * semantic_boost +
                cfg.RERANK_WEIGHT_LEXICAL * lexical_boost
            )

            # Factor 3: trust tier
            score += cfg.RERANK_WEIGHT_TRUST_TIER * _tier_score(chunk.trust_tier)

            # Factor 4: review state
            review_s = _REVIEW_SCORES.get(chunk.review_status, 0.2)
            approval_s = _APPROVAL_SCORES.get(chunk.approval_state, 0.5)
            score += cfg.RERANK_WEIGHT_REVIEW_STATE * ((review_s + approval_s) / 2.0)

            # Factor 5: domain fit
            domain_fit = 1.0 if chunk.domain in classification.inferred_domains else 0.5
            score += cfg.RERANK_WEIGHT_DOMAIN_FIT * domain_fit

            # Factor 6: question type fit
            chunk_qtypes = set(chunk.question_types_supported)
            query_qtypes = set(classification.inferred_question_types)
            qtype_overlap = len(chunk_qtypes & query_qtypes)
            qtype_fit = min(1.0, qtype_overlap / max(1, len(query_qtypes)))
            score += cfg.RERANK_WEIGHT_QUESTION_TYPE_FIT * qtype_fit

            # Factor 7: case specificity (prefer broadly_applicable for general queries)
            case_s = _CASE_SPECIFICITY_GENERAL_SCORES.get(chunk.case_specificity, 0.7)
            score += cfg.RERANK_WEIGHT_CASE_SPECIFICITY * case_s

            # Factor 8: quality flags (penalties)
            quality_penalty = sum(
                _QUALITY_PENALTIES.get(f, 0.0) for f in chunk.quality_flags
            )
            score += cfg.RERANK_WEIGHT_QUALITY * max(-1.0, quality_penalty)

            # Factor 9: citability
            cit_s = _CITABILITY_SCORES.get(chunk.citability, 0.5)
            score += cfg.RERANK_WEIGHT_CITABILITY * cit_s

            # Factor 10: retrieval_weight_hint (reviewer manual boost, 0–5)
            if chunk.retrieval_weight_hint is not None:
                hint_norm = chunk.retrieval_weight_hint / 5.0
                score += cfg.RERANK_WEIGHT_RETRIEVAL_HINT * hint_norm

            # Factor 11: duplicate status penalty
            dup_penalty = _DUPLICATE_PENALTIES.get(chunk.duplicate_status, 0.0)
            score += dup_penalty

            scored.append({
                "chunk_id": cid,
                "rerank_score": score,
                "trust_tier": chunk.trust_tier,
                "domain": chunk.domain,
                "case_specificity": chunk.case_specificity,
            })

        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored
