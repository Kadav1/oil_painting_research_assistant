"""evaluation — Benchmark runner, scorer, and failure logger."""

from oil_painting_rag.evaluation.benchmark_runner import BenchmarkRunner, load_gold_set
from oil_painting_rag.evaluation.failure_logger import FailureLogger
from oil_painting_rag.evaluation.scorer import Scorer

__all__ = [
    "BenchmarkRunner",
    "load_gold_set",
    "FailureLogger",
    "Scorer",
]
