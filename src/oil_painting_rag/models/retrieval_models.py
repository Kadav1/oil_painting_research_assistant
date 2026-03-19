"""
retrieval_models.py — Pydantic v2 models for the retrieval pipeline.

Covers: query classification, context packages, retrieval traces,
candidate scoring, and answer labeling.

All models map to their respective JSON schemas.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Query classification
# ---------------------------------------------------------------------------

class QueryClassification(BaseModel):
    """Result of classifying an incoming query."""

    inferred_modes: list[str] = Field(default_factory=list)
    inferred_domains: list[str] = Field(default_factory=list)
    inferred_question_types: list[str] = Field(default_factory=list)
    classification_method: str = "keyword_rules"


# ---------------------------------------------------------------------------
# Retrieval request
# ---------------------------------------------------------------------------

class RetrievalRequest(BaseModel):
    """Parameters for a hybrid retrieval call."""

    query: str
    top_k: int = 8
    token_budget: int = 3000
    approval_gate: str = "retrieval_allowed"   # "retrieval_allowed" | "live_allowed" | "testing_only"
    filters: dict[str, Any] = Field(default_factory=dict)
    enable_trace: bool = False


# ---------------------------------------------------------------------------
# Candidate pool entries
# ---------------------------------------------------------------------------

class VectorCandidate(BaseModel):
    """A chunk returned from ChromaDB vector search."""

    chunk_id: str
    cosine_distance: float
    rank: int


class LexicalCandidate(BaseModel):
    """A chunk returned from BM25 lexical search."""

    chunk_id: str
    bm25_score: float
    rank: int


class MergedCandidate(BaseModel):
    """A chunk after merging vector and lexical legs (RRF)."""

    chunk_id: str
    merge_score: float
    sources: list[str] = Field(default_factory=list)  # "vector" | "lexical" | both


class RerankedResult(BaseModel):
    """A candidate after multi-factor reranking."""

    chunk_id: str
    rerank_score: float
    trust_tier: int
    domain: str
    case_specificity: str
    rank_after_rerank: int


# ---------------------------------------------------------------------------
# Selected context chunk (in context package)
# ---------------------------------------------------------------------------

class SelectedChunk(BaseModel):
    """A chunk selected for the final context window."""

    chunk_id: str
    source_id: str
    chunk_title: str
    text: str
    trust_tier: int
    domain: str
    case_specificity: str
    citability: str
    citation_format: str
    rerank_score: Optional[float] = None
    selection_reason: str = ""


class ExcludedCandidate(BaseModel):
    """A candidate excluded from the context window with reason."""

    chunk_id: str
    exclusion_reason: str  # "approval_gate" | "duplicate_suppressed" | "token_budget_exceeded" | "diversity_cap" | "tier_superseded" | "manual_exclude"


class DuplicateSuppressionNote(BaseModel):
    """Records one duplicate suppression decision."""

    suppressed_chunk_id: str
    kept_chunk_id: str
    cluster_id: str
    reason: str


class ConflictNote(BaseModel):
    """Signals a conflict between selected chunks that must be disclosed."""

    conflict_id: str
    topic: str
    entity_ids_in_context: list[str] = Field(default_factory=list)
    requires_disclosure: bool = True
    summary: str = ""


# ---------------------------------------------------------------------------
# Context package
# ---------------------------------------------------------------------------

class ContextPackage(BaseModel):
    """
    The assembled retrieval result passed to the generation layer.

    Maps to context_package_schema.json.
    """

    package_id: str
    query: str
    query_classification: QueryClassification
    filters_applied: dict[str, Any] = Field(default_factory=dict)
    selected_chunks: list[SelectedChunk] = Field(default_factory=list)
    token_budget_used: int = 0
    token_budget_limit: int = 3000
    conflict_notes: list[ConflictNote] = Field(default_factory=list)
    retrieval_notes: list[str] = Field(default_factory=list)
    assembly_timestamp: str = ""
    retrieval_trace_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Retrieval trace (for debugging and evaluation)
# ---------------------------------------------------------------------------

class RetrievalTrace(BaseModel):
    """
    Full pipeline execution record for one query.

    Maps to retrieval_trace_schema.json.
    Not stored in ChromaDB — written to metadata store on demand.
    """

    trace_id: str
    query: str
    query_classification: QueryClassification
    filters_applied: dict[str, Any] = Field(default_factory=dict)
    lexical_candidates: list[LexicalCandidate] = Field(default_factory=list)
    vector_candidates: list[VectorCandidate] = Field(default_factory=list)
    merged_candidate_pool: list[MergedCandidate] = Field(default_factory=list)
    reranked_results: list[RerankedResult] = Field(default_factory=list)
    selected_context_chunks: list[dict[str, Any]] = Field(default_factory=list)
    excluded_candidates: list[ExcludedCandidate] = Field(default_factory=list)
    duplicate_suppression_notes: list[DuplicateSuppressionNote] = Field(default_factory=list)
    conflict_notes: list[ConflictNote] = Field(default_factory=list)
    tier_coverage: dict[str, int] = Field(default_factory=dict)
    trace_timestamp: str = ""
    context_package_id: Optional[str] = None
    pipeline_warnings: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Answer label
# ---------------------------------------------------------------------------

class AnswerLabel(BaseModel):
    """A label applied to a claim in an answer."""

    label: str           # controlled_vocabulary.answer_label
    scope_level: str     # "general" | "historical" | "product" | "case" | etc.
    display_phrase: str  # one of the allowed_user_facing_phrases


class AnswerResult(BaseModel):
    """The final output of the generation pipeline."""

    query: str
    answer_text: str
    answer_mode: str                        # controlled_vocabulary.answer_mode
    answer_labels: list[AnswerLabel] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    conflict_disclosures: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    context_package_id: Optional[str] = None
    trace_id: Optional[str] = None
