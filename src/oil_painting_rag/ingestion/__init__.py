"""ingestion — Source capture, loading, and registry for the Oil Painting Research Assistant."""

from oil_painting_rag.ingestion.capture import SourceCapture
from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
from oil_painting_rag.ingestion.intake_runner import process_file
from oil_painting_rag.ingestion.loader import SourceLoader
from oil_painting_rag.ingestion.source_registry import SourceRegistry

__all__ = ["IntakeClassifier", "SourceCapture", "SourceLoader", "SourceRegistry", "process_file"]
