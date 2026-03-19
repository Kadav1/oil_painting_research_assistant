"""
api.py — FastAPI REST interface for the Oil Painting Research Assistant.

Endpoints:
    POST /ask               Ask a question (full RAG pipeline)
    GET  /status            Index and system status
    GET  /sources           List registered sources
    GET  /conflicts         List active conflicts
    POST /benchmark/run     Run benchmark (async — returns run ID)
    GET  /benchmark/{run_id} Get benchmark run results

Run with:
    uvicorn oil_painting_rag.api:app --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Oil Painting Research Assistant",
    version="1.0.0",
    description=(
        "Domain-specific RAG system for oil painting research. "
        "Covers pigment chemistry, historical practices, conservation, and manufacturer data."
    ),
)


# ---------------------------------------------------------------------------
# Lazy singletons (avoid heavy init on import)
# ---------------------------------------------------------------------------

_index_manager = None
_retriever = None
_answerer = None


def _get_index_manager():
    global _index_manager
    if _index_manager is None:
        from oil_painting_rag.indexing.index_manager import IndexManager
        cfg.ensure_data_dirs()
        _index_manager = IndexManager()
    return _index_manager


def _get_retriever():
    global _retriever
    if _retriever is None:
        from oil_painting_rag.retrieval.hybrid_retriever import HybridRetriever
        _retriever = HybridRetriever(_get_index_manager())
    return _retriever


def _get_answerer():
    global _answerer
    if _answerer is None:
        from oil_painting_rag.generation.answerer import Answerer
        _answerer = Answerer()
    return _answerer


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(cfg.RETRIEVAL_TOP_K, ge=1, le=20)
    token_budget: int = Field(cfg.RETRIEVAL_TOKEN_BUDGET, ge=100, le=8000)
    approval_gate: str = Field(cfg.DEFAULT_RETRIEVAL_GATE)
    enable_trace: bool = False


class AskResponse(BaseModel):
    query: str
    answer_text: str
    answer_mode: str
    answer_labels: list[dict[str, str]] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    conflict_disclosures: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    context_package_id: Optional[str] = None
    trace_id: Optional[str] = None
    retrieval_notes: list[str] = Field(default_factory=list)
    chunks_used: int = 0
    tokens_used: int = 0


class StatusResponse(BaseModel):
    status: str
    chroma_counts: dict[str, int] = Field(default_factory=dict)
    lexical_doc_count: int = 0
    source_count: int = 0
    timestamp: str = ""


class SourceSummary(BaseModel):
    source_id: str
    source_title: str
    domain: str
    trust_tier: int
    approval_state: str
    review_status: str


class ConflictSummary(BaseModel):
    conflict_id: str
    topic: str
    entity_ids: list[str] = Field(default_factory=list)
    resolution_status: str


class BenchmarkRunRequest(BaseModel):
    max_records: Optional[int] = None
    approval_gate: str = Field(cfg.DEFAULT_RETRIEVAL_GATE)
    enable_trace: bool = False


class BenchmarkRunResponse(BaseModel):
    run_id: str
    records_attempted: int
    failures_logged: int
    output_path: Optional[str] = None
    timestamp: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """
    Ask a research question using the full hybrid RAG pipeline.

    The response includes the generated answer, citations, conflict disclosures,
    and uncertainty notes derived from retrieved source material.
    """
    from oil_painting_rag.models.retrieval_models import RetrievalRequest

    retrieval_request = RetrievalRequest(
        query=request.query,
        top_k=request.top_k,
        token_budget=request.token_budget,
        approval_gate=request.approval_gate,
        enable_trace=request.enable_trace,
    )

    try:
        context = _get_retriever().retrieve(retrieval_request)
    except Exception as exc:
        logger.error("Retrieval error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Retrieval error: {exc}") from exc

    try:
        result = _get_answerer().answer(request.query, context)
    except Exception as exc:
        logger.error("Generation error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Generation error: {exc}") from exc

    return AskResponse(
        query=result.query,
        answer_text=result.answer_text,
        answer_mode=result.answer_mode,
        answer_labels=[lb.model_dump() for lb in result.answer_labels],
        citations=result.citations,
        conflict_disclosures=result.conflict_disclosures,
        uncertainty_notes=result.uncertainty_notes,
        context_package_id=result.context_package_id,
        trace_id=result.trace_id,
        retrieval_notes=context.retrieval_notes,
        chunks_used=len(context.selected_chunks),
        tokens_used=context.token_budget_used,
    )


@app.get("/status", response_model=StatusResponse)
def status() -> StatusResponse:
    """Return index health and source register summary."""
    try:
        idx = _get_index_manager().status()
        chroma_counts: dict[str, int] = idx.get("chroma_counts", {})
        lex_count: int = idx.get("bm25_size", 0)
    except Exception as exc:
        logger.warning("Could not fetch index status: %s", exc)
        chroma_counts = {}
        lex_count = 0

    source_count = 0
    try:
        from oil_painting_rag.ingestion.source_registry import SourceRegistry
        source_count = len(SourceRegistry().all_sources())
    except Exception:
        pass

    return StatusResponse(
        status="ok",
        chroma_counts=chroma_counts,
        lexical_doc_count=lex_count,
        source_count=source_count,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
    )


@app.get("/sources", response_model=list[SourceSummary])
def list_sources(
    domain: Optional[str] = Query(None),
    tier: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[SourceSummary]:
    """List registered sources, optionally filtered by domain or trust tier."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    all_src = SourceRegistry().all_sources()
    if domain:
        all_src = [s for s in all_src if s.domain == domain]
    if tier is not None:
        all_src = [s for s in all_src if s.trust_tier == tier]

    return [
        SourceSummary(
            source_id=s.source_id,
            source_title=s.source_title,
            domain=s.domain,
            trust_tier=s.trust_tier,
            approval_state=s.approval_state,
            review_status=s.review_status,
        )
        for s in all_src[:limit]
    ]


@app.get("/conflicts", response_model=list[ConflictSummary])
def list_conflicts(
    resolved: bool = Query(False, description="Include resolved conflicts"),
) -> list[ConflictSummary]:
    """List conflict records, by default only unresolved."""
    from oil_painting_rag.storage.metadata_store import MetadataStore

    all_conflicts = MetadataStore().load_all_conflicts()
    if not resolved:
        all_conflicts = [c for c in all_conflicts if c.get("resolution_status") != "resolved"]

    return [
        ConflictSummary(
            conflict_id=c.get("conflict_id", ""),
            topic=str(c.get("topic", "")),
            entity_ids=c.get("entity_ids", []),
            resolution_status=c.get("resolution_status", ""),
        )
        for c in all_conflicts[:100]
    ]


@app.post("/benchmark/run", response_model=BenchmarkRunResponse)
def run_benchmark(request: BenchmarkRunRequest) -> BenchmarkRunResponse:
    """
    Run the benchmark gold set through the RAG pipeline.

    Returns a summary including the path to the full results JSON.
    Note: This is a synchronous endpoint — large gold sets may take time.
    """
    from oil_painting_rag.evaluation.benchmark_runner import BenchmarkRunner
    from oil_painting_rag.utils.hash_utils import make_trace_id

    run_id = make_trace_id()
    now = datetime.now(tz=timezone.utc).isoformat()

    try:
        runner = BenchmarkRunner(
            index_manager=_get_index_manager(),
            approval_gate=request.approval_gate,
            enable_trace=request.enable_trace,
        )
        results = runner.run(max_records=request.max_records)
        out = runner.save_results(results)
        failures = sum(1 for r in results if r.failure_tags)
    except Exception as exc:
        logger.error("Benchmark error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Benchmark error: {exc}") from exc

    return BenchmarkRunResponse(
        run_id=run_id,
        records_attempted=len(results),
        failures_logged=failures,
        output_path=str(out),
        timestamp=now,
    )


@app.get("/benchmark/{output_filename}", response_model=list[dict[str, Any]])
def get_benchmark_results(output_filename: str) -> list[dict[str, Any]]:
    """
    Retrieve stored benchmark run results by filename.

    The filename should be the basename of a file in the benchmark_runs/ directory.
    """
    import json
    from pathlib import Path

    if "/" in output_filename or "\\" in output_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    result_path = cfg.BENCHMARKS_DIR / output_filename
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark results not found")

    try:
        with result_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not load results: {exc}") from exc


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import uvicorn
    uvicorn.run(
        "oil_painting_rag.api:app",
        host=cfg.API_HOST,
        port=cfg.API_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
