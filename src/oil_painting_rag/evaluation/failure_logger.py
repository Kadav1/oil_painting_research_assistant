"""
failure_logger.py — Retrieval and answer failure logging for the benchmark.

Logs FailureRecord entries to the retrieval_failure_log.csv file for later
inspection and debugging. All failures are appended — never overwritten.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.benchmark_models import BenchmarkRecord, BenchmarkRunResult, FailureRecord
from oil_painting_rag.utils.hash_utils import sha256_hex

logger = get_logger(__name__)

_FAILURE_LOG_COLUMNS = [
    "failure_id",
    "benchmark_id",
    "question",
    "failure_tags",
    "answer_produced",
    "expected_answer_shape",
    "retrieval_notes",
    "logged_at",
    "reviewer_notes",
]


class FailureLogger:
    """
    Appends FailureRecord entries to the retrieval failure log CSV.

    One row per failure; all failures are cumulative across runs.
    """

    def __init__(self, log_path: Path = cfg.RETRIEVAL_FAILURE_LOG_PATH) -> None:
        self._log_path = log_path

    def log_failure(self, record: FailureRecord) -> None:
        """Append one FailureRecord to the failure log CSV."""
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

        write_header = not self._log_path.exists()
        try:
            with self._log_path.open("a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=_FAILURE_LOG_COLUMNS)
                if write_header:
                    writer.writeheader()
                writer.writerow({
                    "failure_id": record.failure_id,
                    "benchmark_id": record.benchmark_id,
                    "question": record.question,
                    "failure_tags": "|".join(record.failure_tags),
                    "answer_produced": record.answer_produced[:500],
                    "expected_answer_shape": record.expected_answer_shape[:200],
                    "retrieval_notes": record.retrieval_notes,
                    "logged_at": record.logged_at,
                    "reviewer_notes": record.reviewer_notes,
                })
        except OSError as exc:
            logger.error("Could not write failure log: %s", exc)

    def log_run_result(
        self,
        run_result: BenchmarkRunResult,
        benchmark_record: BenchmarkRecord,
    ) -> None:
        """
        Log a FailureRecord from a BenchmarkRunResult that did not pass.

        No-op if the run has no failure tags.
        """
        tags = run_result.failure_tags
        if not tags:
            return

        failure_id = f"FAIL-{sha256_hex(run_result.run_id)[:8].upper()}"
        now = datetime.now(tz=timezone.utc).isoformat()

        failure = FailureRecord(
            failure_id=failure_id,
            benchmark_id=run_result.benchmark_id,
            question=run_result.question,
            failure_tags=tags,
            answer_produced=run_result.generated_answer,
            expected_answer_shape=benchmark_record.expected_answer_shape,
            retrieval_notes=", ".join(
                run_result.scoring.evaluator_notes.split("\n")[:3]
            ) if run_result.scoring and run_result.scoring.evaluator_notes else "",
            logged_at=now,
        )
        self.log_failure(failure)

    def load_failures(self) -> list[FailureRecord]:
        """Load all logged failures from the CSV."""
        if not self._log_path.exists():
            return []
        records: list[FailureRecord] = []
        try:
            with self._log_path.open("r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    tags = [t for t in row.get("failure_tags", "").split("|") if t]
                    records.append(FailureRecord(
                        failure_id=row.get("failure_id", ""),
                        benchmark_id=row.get("benchmark_id", ""),
                        question=row.get("question", ""),
                        failure_tags=tags,
                        answer_produced=row.get("answer_produced", ""),
                        expected_answer_shape=row.get("expected_answer_shape", ""),
                        retrieval_notes=row.get("retrieval_notes", ""),
                        logged_at=row.get("logged_at", ""),
                        reviewer_notes=row.get("reviewer_notes", ""),
                    ))
        except OSError as exc:
            logger.error("Could not read failure log: %s", exc)
        return records
