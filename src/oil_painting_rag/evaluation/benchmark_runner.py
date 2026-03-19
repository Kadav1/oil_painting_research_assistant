"""
benchmark_runner.py — Benchmark execution harness for the Oil Painting Research Assistant.

Loads BenchmarkRecord entries from the gold set JSON, runs each question through the
full retrieval + generation pipeline, logs failures, and writes a summary report.

Usage (module):
    from oil_painting_rag.evaluation.benchmark_runner import BenchmarkRunner
    runner = BenchmarkRunner(index_manager=mgr)
    report = runner.run()

Usage (CLI):
    python -m oil_painting_rag.evaluation.benchmark_runner
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.evaluation.failure_logger import FailureLogger
from oil_painting_rag.evaluation.scorer import Scorer
from oil_painting_rag.generation.answerer import Answerer
from oil_painting_rag.indexing.index_manager import IndexManager
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.benchmark_models import (
    BenchmarkRecord,
    BenchmarkRunResult,
    ScoringResult,
)
from oil_painting_rag.models.retrieval_models import RetrievalRequest
from oil_painting_rag.retrieval.hybrid_retriever import HybridRetriever
from oil_painting_rag.utils.hash_utils import make_trace_id

logger = get_logger(__name__)


def load_gold_set(path: Path = cfg.BENCHMARK_GOLD_SET_PATH) -> list[BenchmarkRecord]:
    """
    Load the benchmark gold set from JSON.

    The JSON file is expected to contain either:
    - A list of benchmark records at the top level, or
    - An object with a "records" or "benchmarks" key containing the list.
    """
    if not path.exists():
        logger.warning("Benchmark gold set not found: %s", path)
        return []
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Could not load benchmark gold set: %s", exc)
        return []

    raw_records: list[dict] = []
    if isinstance(data, list):
        raw_records = data
    elif isinstance(data, dict):
        for key in ("records", "benchmarks", "items"):
            if key in data and isinstance(data[key], list):
                raw_records = data[key]
                break

    records: list[BenchmarkRecord] = []
    for raw in raw_records:
        try:
            records.append(BenchmarkRecord.model_validate(raw))
        except Exception as exc:
            logger.warning("Skipping invalid benchmark record: %s", exc)

    logger.info("Loaded %d benchmark records from %s", len(records), path)
    return records


class BenchmarkRunner:
    """
    Runs the benchmark gold set through the full retrieval + generation pipeline.

    For each record:
    1. Build a RetrievalRequest from the question
    2. Run HybridRetriever.retrieve()
    3. Run Answerer.answer()
    4. Run Scorer automated checks
    5. Log failures via FailureLogger
    6. Collect results into BenchmarkRunResult list

    Human dimension scores must be added externally after the run.
    """

    def __init__(
        self,
        index_manager: IndexManager,
        answerer: Optional[Answerer] = None,
        gold_set_path: Path = cfg.BENCHMARK_GOLD_SET_PATH,
        approval_gate: str = cfg.DEFAULT_RETRIEVAL_GATE,
        enable_trace: bool = False,
    ) -> None:
        self._retriever = HybridRetriever(index_manager)
        self._answerer = answerer or Answerer()
        self._scorer = Scorer()
        self._failure_logger = FailureLogger()
        self._gold_set_path = gold_set_path
        self._approval_gate = approval_gate
        self._enable_trace = enable_trace

    def run(
        self,
        records: Optional[list[BenchmarkRecord]] = None,
        max_records: Optional[int] = None,
    ) -> list[BenchmarkRunResult]:
        """
        Execute the benchmark run.

        If records is None, loads from the gold set path.
        Returns a list of BenchmarkRunResult for all attempted records.
        """
        if records is None:
            records = load_gold_set(self._gold_set_path)

        if not records:
            logger.warning("No benchmark records to run")
            return []

        if max_records is not None:
            records = records[:max_records]

        logger.info("Starting benchmark run: %d questions", len(records))
        results: list[BenchmarkRunResult] = []

        for record in records:
            result = self._run_one(record)
            results.append(result)

        passed = sum(1 for r in results if r.scoring and r.scoring.passed)
        logger.info(
            "Benchmark run complete: %d/%d records attempted. "
            "Automated pass (requires human scoring): n/a",
            len(results), len(records),
        )
        return results

    def _run_one(self, record: BenchmarkRecord) -> BenchmarkRunResult:
        """Execute a single benchmark record and return the result."""
        run_id = make_trace_id()
        now = datetime.now(tz=timezone.utc).isoformat()
        logger.debug("Running benchmark %s: %r", record.benchmark_id, record.question[:60])

        # Build retrieval request
        request = RetrievalRequest(
            query=record.question,
            top_k=cfg.RETRIEVAL_TOP_K,
            token_budget=cfg.RETRIEVAL_TOKEN_BUDGET,
            approval_gate=self._approval_gate,
            enable_trace=self._enable_trace,
        )

        generated_answer = ""
        chunk_ids: list[str] = []
        trace_id: Optional[str] = None
        failure_tags: list[str] = []
        scoring: Optional[ScoringResult] = None

        try:
            context = self._retriever.retrieve(request)
            chunk_ids = [sc.chunk_id for sc in context.selected_chunks]
            trace_id = context.retrieval_trace_id

            answer = self._answerer.answer(record.question, context)
            generated_answer = answer.answer_text

            # Automated pre-scoring
            scoring = self._scorer.score_answer(record, answer)
            failure_tags = scoring.failure_tags

        except Exception as exc:
            logger.error("Benchmark %s failed with exception: %s", record.benchmark_id, exc)
            generated_answer = f"[ERROR: {exc}]"
            failure_tags = ["PIPELINE_ERROR"]

        result = BenchmarkRunResult(
            run_id=run_id,
            benchmark_id=record.benchmark_id,
            question=record.question,
            generated_answer=generated_answer,
            context_chunk_ids=chunk_ids,
            trace_id=trace_id,
            scoring=scoring,
            failure_tags=failure_tags,
            run_timestamp=now,
        )

        # Log failures
        if failure_tags:
            self._failure_logger.log_run_result(result, record)

        return result

    def save_results(
        self,
        results: list[BenchmarkRunResult],
        output_dir: Path = cfg.BENCHMARKS_DIR,
    ) -> Path:
        """
        Write the full run results to a timestamped JSON file.

        Returns the path to the written file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
        output_path = output_dir / f"benchmark_run_{ts}.json"

        serialized: list[dict[str, Any]] = [r.model_dump() for r in results]
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(serialized, fh, indent=2, default=str)

        logger.info("Benchmark results saved to %s", output_path)
        return output_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli_main() -> None:
    """Run the benchmark from the command line with the default index manager."""
    from oil_painting_rag.indexing.index_manager import IndexManager

    cfg.ensure_data_dirs()
    index_manager = IndexManager()
    runner = BenchmarkRunner(index_manager=index_manager)
    results = runner.run()
    if results:
        out = runner.save_results(results)
        print(f"Results written to: {out}")
    else:
        print("No results produced.")


if __name__ == "__main__":
    _cli_main()
