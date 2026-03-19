"""retrieval — Hybrid retrieval pipeline for the Oil Painting Research Assistant."""

from oil_painting_rag.retrieval.classifier import classify_query
from oil_painting_rag.retrieval.hybrid_retriever import HybridRetriever
from oil_painting_rag.retrieval.reranker import Reranker
from oil_painting_rag.retrieval.diversity import DiversityFilter
from oil_painting_rag.retrieval.citation_assembler import CitationAssembler

__all__ = [
    "classify_query",
    "HybridRetriever",
    "Reranker",
    "DiversityFilter",
    "CitationAssembler",
]
