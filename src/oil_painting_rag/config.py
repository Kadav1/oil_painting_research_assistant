"""
config.py — Central configuration for the Oil Painting Research Assistant.

All paths, model names, collection names, and thresholds live here.
Every other module imports from this file rather than hardcoding values.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------------------------
# Project root — resolve relative to this file
# ---------------------------------------------------------------------------

_SRC = Path(__file__).resolve().parent          # src/oil_painting_rag/
_PKG_ROOT = _SRC.parent                          # src/
PROJECT_ROOT: Path = _PKG_ROOT.parent            # project root


# ---------------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------------

DATA_DIR: Path = PROJECT_ROOT / "data"

# Inbox — pre-ingestion staging area, organized by file type
INBOX_DIR: Path = DATA_DIR / "inbox"
INBOX_PDF_DIR: Path = INBOX_DIR / "pdf"
INBOX_HTML_DIR: Path = INBOX_DIR / "html"
INBOX_MARKDOWN_DIR: Path = INBOX_DIR / "markdown"
INBOX_TEXT_DIR: Path = INBOX_DIR / "text"
INBOX_OTHER_DIR: Path = INBOX_DIR / "other"

# Extension-to-inbox subfolder mapping
INBOX_EXT_MAP: dict[str, str] = {
    ".pdf": "pdf",
    ".html": "html",
    ".htm": "html",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".text": "text",
}

RAW_DIR: Path = DATA_DIR / "raw"
CLEAN_DIR: Path = DATA_DIR / "clean"
CHUNKS_DIR: Path = DATA_DIR / "chunks"
INDEXES_DIR: Path = DATA_DIR / "indexes"
REGISTER_DIR: Path = DATA_DIR / "register"
LOGS_DIR: Path = DATA_DIR / "logs"
BENCHMARKS_DIR: Path = DATA_DIR / "benchmark_runs"

# Chunk sub-dirs
CHUNKS_TEXT_DIR: Path = CHUNKS_DIR / "text"
CHUNKS_TABLES_DIR: Path = CHUNKS_DIR / "tables"
CHUNKS_METADATA_DIR: Path = CHUNKS_DIR / "metadata"

# Index sub-dirs
CHROMA_DIR: Path = INDEXES_DIR / "chroma"
LEXICAL_DIR: Path = INDEXES_DIR / "lexical"
CACHE_DIR: Path = INDEXES_DIR / "cache"


# ---------------------------------------------------------------------------
# Schema and vocab directories
# ---------------------------------------------------------------------------

SCHEMAS_DIR: Path = PROJECT_ROOT / "schemas"
VOCAB_DIR: Path = PROJECT_ROOT / "vocab"
BENCHMARKS_SRC_DIR: Path = PROJECT_ROOT / "benchmarks"
DOCS_DIR: Path = PROJECT_ROOT / "docs"


# ---------------------------------------------------------------------------
# Vocabulary files
# ---------------------------------------------------------------------------

CONTROLLED_VOCABULARY_PATH: Path = VOCAB_DIR / "controlled_vocabulary.json"
MATERIAL_ALIAS_MAP_PATH: Path = VOCAB_DIR / "material_alias_map.json"
PRODUCT_ALIAS_MAP_PATH: Path = VOCAB_DIR / "product_alias_map.json"
MATERIAL_ONTOLOGY_PATH: Path = VOCAB_DIR / "material_ontology_v1.json"


# ---------------------------------------------------------------------------
# Register / audit files
# ---------------------------------------------------------------------------

ACQUISITION_LOG_PATH: Path = REGISTER_DIR / "acquisition_log.csv"
CHUNK_REVIEW_LOG_PATH: Path = REGISTER_DIR / "chunk_review_log.csv"
CONFLICT_REVIEW_LOG_PATH: Path = REGISTER_DIR / "conflict_review_log.csv"
CONFLICT_LOG_PATH: Path = LOGS_DIR / "conflict_log.csv"
RETRIEVAL_FAILURE_LOG_PATH: Path = LOGS_DIR / "retrieval_failure_log.csv"


# ---------------------------------------------------------------------------
# ChromaDB collections
# Per approval_state_schema.json chromadb_collection_names
# ---------------------------------------------------------------------------

CHROMA_COLLECTION_LIVE: str = "chunks_live"
CHROMA_COLLECTION_RETRIEVAL: str = "chunks_retrieval"
CHROMA_COLLECTION_DRAFT: str = "chunks_draft"

# Approval states that are indexed per collection
# (mirrored from approval_state_schema.json)
LIVE_APPROVAL_STATES: list[str] = ["live_allowed"]
RETRIEVAL_APPROVAL_STATES: list[str] = ["retrieval_allowed", "live_allowed"]
DRAFT_APPROVAL_STATES: list[str] = ["testing_only", "retrieval_allowed", "live_allowed"]


# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)
EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")

# Max tokens for a single embedded chunk
EMBEDDING_MAX_TOKENS: int = int(os.getenv("EMBEDDING_MAX_TOKENS", "512"))


# ---------------------------------------------------------------------------
# LLM / generation backend
# ---------------------------------------------------------------------------

LLM_BACKEND: str = os.getenv("LLM_BACKEND", "openai")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
LLM_API_KEY: str | None = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
LLM_BASE_URL: str | None = os.getenv("LLM_BASE_URL")  # for local models
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))


# ---------------------------------------------------------------------------
# Retrieval settings
# ---------------------------------------------------------------------------

# Default number of candidates from each search leg
VECTOR_CANDIDATE_COUNT: int = int(os.getenv("VECTOR_CANDIDATE_COUNT", "20"))
LEXICAL_CANDIDATE_COUNT: int = int(os.getenv("LEXICAL_CANDIDATE_COUNT", "20"))

# Final context window chunk limit
RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "8"))

# Token budget for the context window
RETRIEVAL_TOKEN_BUDGET: int = int(os.getenv("RETRIEVAL_TOKEN_BUDGET", "3000"))

# Minimum approval state required for user-facing retrieval
# Options: "retrieval_allowed" | "live_allowed"
DEFAULT_RETRIEVAL_GATE: str = os.getenv("DEFAULT_RETRIEVAL_GATE", "retrieval_allowed")

# Diversity: maximum chunks per source_id in final context
MAX_CHUNKS_PER_SOURCE: int = int(os.getenv("MAX_CHUNKS_PER_SOURCE", "3"))

# RRF (Reciprocal Rank Fusion) constant
RRF_K: int = int(os.getenv("RRF_K", "60"))

# Reranker weights (multipliers; semantic + lexical dominate)
RERANK_WEIGHT_SEMANTIC: float = float(os.getenv("RERANK_WEIGHT_SEMANTIC", "0.35"))
RERANK_WEIGHT_LEXICAL: float = float(os.getenv("RERANK_WEIGHT_LEXICAL", "0.20"))
RERANK_WEIGHT_TRUST_TIER: float = float(os.getenv("RERANK_WEIGHT_TRUST_TIER", "0.15"))
RERANK_WEIGHT_REVIEW_STATE: float = float(os.getenv("RERANK_WEIGHT_REVIEW_STATE", "0.10"))
RERANK_WEIGHT_DOMAIN_FIT: float = float(os.getenv("RERANK_WEIGHT_DOMAIN_FIT", "0.08"))
RERANK_WEIGHT_QUESTION_TYPE_FIT: float = float(os.getenv("RERANK_WEIGHT_QUESTION_TYPE_FIT", "0.05"))
RERANK_WEIGHT_CASE_SPECIFICITY: float = float(os.getenv("RERANK_WEIGHT_CASE_SPECIFICITY", "0.03"))
RERANK_WEIGHT_QUALITY: float = float(os.getenv("RERANK_WEIGHT_QUALITY", "0.02"))
RERANK_WEIGHT_CITABILITY: float = float(os.getenv("RERANK_WEIGHT_CITABILITY", "0.01"))
RERANK_WEIGHT_RETRIEVAL_HINT: float = float(os.getenv("RERANK_WEIGHT_RETRIEVAL_HINT", "0.01"))


# ---------------------------------------------------------------------------
# Chunking settings
# ---------------------------------------------------------------------------

CHUNK_MAX_TOKENS: int = int(os.getenv("CHUNK_MAX_TOKENS", "400"))
CHUNK_MIN_TOKENS: int = int(os.getenv("CHUNK_MIN_TOKENS", "40"))
CHUNK_OVERLAP_SENTENCES: int = int(os.getenv("CHUNK_OVERLAP_SENTENCES", "1"))


# ---------------------------------------------------------------------------
# API server
# ---------------------------------------------------------------------------

API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
API_PORT: int = int(os.getenv("API_PORT", "8765"))


# ---------------------------------------------------------------------------
# Benchmark settings
# ---------------------------------------------------------------------------

BENCHMARK_GOLD_SET_PATH: Path = BENCHMARKS_SRC_DIR / "benchmark_gold_set_v1.json"
BENCHMARK_PASS_THRESHOLD: float = 4.0


def ensure_data_dirs() -> None:
    """Create all required data directories if they do not exist."""
    dirs = [
        INBOX_PDF_DIR, INBOX_HTML_DIR, INBOX_MARKDOWN_DIR,
        INBOX_TEXT_DIR, INBOX_OTHER_DIR,
        RAW_DIR, CLEAN_DIR,
        CHUNKS_TEXT_DIR, CHUNKS_TABLES_DIR, CHUNKS_METADATA_DIR,
        CHROMA_DIR, LEXICAL_DIR, CACHE_DIR,
        REGISTER_DIR, LOGS_DIR, BENCHMARKS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
