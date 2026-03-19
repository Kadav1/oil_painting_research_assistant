"""
scorer.py — Automated pre-scoring for the Oil Painting Research Assistant benchmark.

The scorer performs a lightweight automated check against BenchmarkRecord criteria
before human evaluation. It is not a replacement for human scoring — it provides:
  - must_not_say violation detection (automatic fail)
  - must_include keyword presence (partial scoring signal)
  - required_distinctions checks
  - failure tag derivation

Human evaluators assign final 1–5 dimension scores. The scorer populates
ScoringResult with automated failure_tags and a preliminary passed flag.

The 6 scoring dimensions (human-scored 1–5):
  1. Accuracy            (floor: 3)
  2. Source Fitness      (floor: 3)
  3. Usefulness
  4. Uncertainty Handling
  5. Distinction Quality
  6. Citation Readiness

Pass threshold: average >= 4.0, Accuracy >= 3, Source Fitness >= 3.
"""

from __future__ import annotations

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.benchmark_models import (
    BenchmarkRecord,
    DimensionScore,
    ScoringResult,
)
from oil_painting_rag.models.retrieval_models import AnswerResult

logger = get_logger(__name__)

# Failure taxonomy codes (from benchmark_template.md §9)
FAILURE_FABRICATED_CITATION = "FABRICATED_CITATION"
FAILURE_UNCERTAINTY_COLLAPSED = "UNCERTAINTY_COLLAPSED"
FAILURE_SCOPE_MISMATCH = "SCOPE_MISMATCH"
FAILURE_PRODUCT_UNIVERSALIZED = "PRODUCT_UNIVERSALIZED"
FAILURE_CASE_GENERALIZED = "CASE_GENERALIZED"
FAILURE_CONFLICT_UNDISCLOSED = "CONFLICT_UNDISCLOSED"
FAILURE_HISTORICAL_ANACHRONISM = "HISTORICAL_ANACHRONISM"
FAILURE_MUST_NOT_SAY_VIOLATION = "MUST_NOT_SAY_VIOLATION"

# Dimension names
DIM_ACCURACY = "Accuracy"
DIM_SOURCE_FITNESS = "Source Fitness"
DIM_USEFULNESS = "Usefulness"
DIM_UNCERTAINTY = "Uncertainty Handling"
DIM_DISTINCTION = "Distinction Quality"
DIM_CITATION = "Citation Readiness"

ALL_DIMENSIONS = [
    DIM_ACCURACY,
    DIM_SOURCE_FITNESS,
    DIM_USEFULNESS,
    DIM_UNCERTAINTY,
    DIM_DISTINCTION,
    DIM_CITATION,
]

# Dimensions with a hard floor
CRITICAL_DIMENSIONS: dict[str, float] = {
    DIM_ACCURACY: 3.0,
    DIM_SOURCE_FITNESS: 3.0,
}


class Scorer:
    """
    Lightweight automated scorer for benchmark answers.

    Detects must_not_say violations and must_include misses.
    Human evaluators still provide final dimension scores.
    """

    def score_answer(
        self,
        record: BenchmarkRecord,
        answer: AnswerResult,
    ) -> ScoringResult:
        """
        Run automated pre-scoring checks against a BenchmarkRecord.

        Returns a ScoringResult with automated failure_tags.
        Dimension scores are set to 0.0 (require human scoring to complete).
        """
        failure_tags: list[str] = list(record.failure_tags_if_wrong)
        evaluator_notes: list[str] = []

        answer_text_lower = answer.answer_text.lower()

        # --- must_not_say violations ---
        for prohibited in record.must_not_say:
            if prohibited.lower() in answer_text_lower:
                failure_tags.append(FAILURE_MUST_NOT_SAY_VIOLATION)
                evaluator_notes.append(
                    f"VIOLATION: answer contains prohibited phrase: {prohibited!r}"
                )

        # --- must_include coverage ---
        missing_required: list[str] = []
        for required in record.must_include:
            if required.lower() not in answer_text_lower:
                missing_required.append(required)
        if missing_required:
            evaluator_notes.append(
                f"MISSING required content: {', '.join(missing_required)}"
            )

        # --- Citation check ---
        if not answer.citations:
            evaluator_notes.append(
                "No citations produced — Citation Readiness will likely be low."
            )

        # --- Conflict disclosure check ---
        if answer.conflict_disclosures:
            evaluator_notes.append(
                f"Conflict disclosures present ({len(answer.conflict_disclosures)}) "
                "— verify these are addressed in answer text."
            )

        # --- Mode alignment ---
        if record.target_modes and answer.answer_mode not in record.target_modes:
            evaluator_notes.append(
                f"Mode mismatch: answer used {answer.answer_mode!r}, "
                f"expected one of {record.target_modes}."
            )

        # Placeholder dimension scores (human scoring fills these in)
        dimension_scores = [
            DimensionScore(dimension=dim, score=0.0, notes="Requires human scoring")
            for dim in ALL_DIMENSIONS
        ]

        result = ScoringResult(
            benchmark_id=record.benchmark_id,
            dimension_scores=dimension_scores,
            failure_tags=list(set(failure_tags)),
            evaluator_notes="\n".join(evaluator_notes) if evaluator_notes else "",
        )
        return result

    def score_with_dimensions(
        self,
        record: BenchmarkRecord,
        answer: AnswerResult,
        dimension_scores: dict[str, float],
    ) -> ScoringResult:
        """
        Score an answer with human-provided dimension scores.

        dimension_scores: mapping of dimension name → score (1–5).
        Runs automated checks first, then applies human scores and computes pass/fail.
        """
        base = self.score_answer(record, answer)

        scored_dims: list[DimensionScore] = []
        for dim in ALL_DIMENSIONS:
            raw_score = dimension_scores.get(dim, 0.0)
            if not (1.0 <= raw_score <= 5.0):
                logger.warning(
                    "Score for %s out of range [1,5]: %s — clamping",
                    dim, raw_score,
                )
                raw_score = max(1.0, min(5.0, raw_score))
            scored_dims.append(DimensionScore(dimension=dim, score=raw_score))

        # Hard fail: must_not_say violations force Accuracy to 1
        if FAILURE_MUST_NOT_SAY_VIOLATION in base.failure_tags:
            scored_dims = [
                DimensionScore(
                    dimension=d.dimension,
                    score=1.0 if d.dimension == DIM_ACCURACY else d.score,
                    notes="must_not_say violation detected" if d.dimension == DIM_ACCURACY else d.notes,
                )
                for d in scored_dims
            ]

        result = ScoringResult(
            benchmark_id=record.benchmark_id,
            dimension_scores=scored_dims,
            failure_tags=base.failure_tags,
            evaluator_notes=base.evaluator_notes,
        )
        result.compute()
        return result

    def derive_failure_tags(
        self,
        record: BenchmarkRecord,
        answer: AnswerResult,
    ) -> list[str]:
        """
        Return only the failure tags without building a full ScoringResult.
        Convenience method for quick failure detection.
        """
        result = self.score_answer(record, answer)
        return result.failure_tags
