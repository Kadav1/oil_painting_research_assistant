"""
benchmark_models.py — Pydantic v2 models for benchmark records and evaluation results.

Maps to benchmark_template.json, benchmark_gold_set_v1.json, and the
6-dimension scoring scheme from benchmark_template.md.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BenchmarkRecord(BaseModel):
    """
    One benchmark question record.

    Maps to benchmark_template.json fields.
    """

    benchmark_id: str = Field(
        ...,
        description="Format: BMK-{CATEGORY_CODE}-{NNN}",
    )
    category: str               # controlled_vocabulary.benchmark_category
    question: str
    difficulty: str             # controlled_vocabulary.benchmark_difficulty
    status: str                 # controlled_vocabulary.benchmark_status
    target_modes: list[str] = Field(default_factory=list)
    expected_source_tiers: list[int] = Field(default_factory=list)
    must_use_domains: list[str] = Field(default_factory=list)
    must_not_confuse: list[str] = Field(default_factory=list)
    expected_answer_shape: str = ""
    gold_claims: list[str] = Field(default_factory=list)
    known_uncertainties: list[str] = Field(default_factory=list)
    evaluation_notes: str = ""
    must_include: list[str] = Field(default_factory=list)
    required_distinctions: list[str] = Field(default_factory=list)
    must_not_say: list[str] = Field(default_factory=list)
    uncertainty_handling: str = ""
    citation_expectation: str = ""
    failure_tags_if_wrong: list[str] = Field(default_factory=list)

    model_config = {"extra": "ignore"}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class DimensionScore(BaseModel):
    """Score on one of the 6 evaluation dimensions."""

    dimension: str      # "Accuracy" | "Source Fitness" | "Usefulness" | etc.
    score: float        # 1.0–5.0
    notes: str = ""


class ScoringResult(BaseModel):
    """
    6-dimension scoring result for one benchmark answer.

    Pass threshold: average >= 4.0, Accuracy >= 3, Source Fitness >= 3.
    """

    benchmark_id: str
    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    average_score: float = 0.0
    passed: bool = False
    failure_tags: list[str] = Field(default_factory=list)
    evaluator_notes: str = ""

    def compute(self) -> None:
        """Compute average score and passed flag from dimension_scores."""
        if not self.dimension_scores:
            return
        scores = [d.score for d in self.dimension_scores]
        self.average_score = sum(scores) / len(scores)

        accuracy = next((d.score for d in self.dimension_scores if d.dimension == "Accuracy"), None)
        source_fitness = next((d.score for d in self.dimension_scores if d.dimension == "Source Fitness"), None)

        floors_met = (
            (accuracy is None or accuracy >= 3) and
            (source_fitness is None or source_fitness >= 3)
        )
        self.passed = self.average_score >= 4.0 and floors_met


# ---------------------------------------------------------------------------
# Benchmark run result
# ---------------------------------------------------------------------------

class BenchmarkRunResult(BaseModel):
    """
    Full output for one benchmark evaluation run.

    Stores both the generated answer and the scoring result.
    """

    run_id: str
    benchmark_id: str
    question: str
    generated_answer: str
    context_chunk_ids: list[str] = Field(default_factory=list)
    trace_id: Optional[str] = None
    scoring: Optional[ScoringResult] = None
    failure_tags: list[str] = Field(default_factory=list)
    run_timestamp: str = ""


# ---------------------------------------------------------------------------
# Failure record
# ---------------------------------------------------------------------------

class FailureRecord(BaseModel):
    """
    A logged retrieval or answer failure for later inspection.

    Failure tags from benchmark_template.md §9.
    """

    failure_id: str
    benchmark_id: str
    question: str
    failure_tags: list[str] = Field(default_factory=list)
    answer_produced: str = ""
    expected_answer_shape: str = ""
    retrieval_notes: str = ""
    logged_at: str = ""
    reviewer_notes: str = ""
