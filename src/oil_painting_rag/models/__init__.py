"""models — Pydantic v2 data models for the Oil Painting Research Assistant."""

from oil_painting_rag.models.source_models import SourceRecord
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.provenance_models import (
    FieldProvenance,
    DuplicateCluster,
    ConflictRecord,
    ReviewRecord,
)
from oil_painting_rag.models.retrieval_models import (
    QueryClassification,
    RetrievalRequest,
    VectorCandidate,
    LexicalCandidate,
    MergedCandidate,
    RerankedResult,
    SelectedChunk,
    ExcludedCandidate,
    DuplicateSuppressionNote,
    ConflictNote,
    ContextPackage,
    RetrievalTrace,
    AnswerLabel,
    AnswerResult,
)
from oil_painting_rag.models.benchmark_models import (
    BenchmarkRecord,
    DimensionScore,
    ScoringResult,
    BenchmarkRunResult,
    FailureRecord,
)

__all__ = [
    "SourceRecord",
    "ChunkRecord",
    "FieldProvenance",
    "DuplicateCluster",
    "ConflictRecord",
    "ReviewRecord",
    "QueryClassification",
    "RetrievalRequest",
    "VectorCandidate",
    "LexicalCandidate",
    "MergedCandidate",
    "RerankedResult",
    "SelectedChunk",
    "ExcludedCandidate",
    "DuplicateSuppressionNote",
    "ConflictNote",
    "ContextPackage",
    "RetrievalTrace",
    "AnswerLabel",
    "AnswerResult",
    "BenchmarkRecord",
    "DimensionScore",
    "ScoringResult",
    "BenchmarkRunResult",
    "FailureRecord",
]
