"""
intake_classifier.py — Content-scanning metadata inference for source intake.

Reads file content and filenames, matches against keyword patterns from
intake_patterns.json, and infers source_family, domain, capture_method.
Auto-assigns source_id by incrementing from existing registrations.

Does NOT move files or register sources — that is the intake runner's job.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

_PATTERNS_FILE = Path(__file__).parent / "intake_patterns.json"


@dataclass
class InferenceResult:
    """Result of a single metadata inference."""
    value: str
    confidence: str  # "high", "medium", "low"
    hits: int


def _load_patterns() -> dict:
    """Load keyword patterns from intake_patterns.json."""
    with _PATTERNS_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_family_codes() -> dict[str, str]:
    """Load family_codes from controlled_vocabulary.json."""
    with cfg.CONTROLLED_VOCABULARY_PATH.open("r", encoding="utf-8") as fh:
        vocab = json.load(fh)
    return vocab["source_family"]["family_codes"]


def sanitize_short_title(title: str) -> str:
    """
    Sanitize a short_title for use in filenames.

    Rules: lowercase, spaces/hyphens to underscores, strip non-alphanumeric
    except underscores, collapse consecutive underscores, truncate to 60 chars.
    """
    result = title.lower()
    result = re.sub(r"[\s\-]+", "_", result)
    result = re.sub(r"[^a-z0-9_]", "", result)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_")
    return result[:60]


def build_intake_filename(
    source_id: str, short_title: str, extension: str, dest_dir: Optional[Path] = None
) -> str:
    """
    Build the standardized filename: {source_id}_{sanitized_short_title}.{ext}

    The source_id prefix keeps its hyphens. Only short_title is sanitized.
    If dest_dir is provided and a collision exists, appends _2, _3, etc.
    """
    sanitized = sanitize_short_title(short_title)
    ext = extension if extension.startswith(".") else f".{extension}"
    base = f"{source_id}_{sanitized}"
    candidate = f"{base}{ext}"

    if dest_dir is not None:
        counter = 2
        while (dest_dir / candidate).exists():
            candidate = f"{base}_{counter}{ext}"
            counter += 1

    return candidate


def next_source_id(family_code: str, existing_ids: list[str]) -> str:
    """
    Auto-assign the next source_id for a given family code.

    Scans existing_ids for SRC-{family_code}-NNN, takes max+1, zero-pads to 3.
    """
    pattern = re.compile(rf"^SRC-{re.escape(family_code)}-(\d+)$")
    max_num = 0
    for sid in existing_ids:
        m = pattern.match(sid)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"SRC-{family_code}-{max_num + 1:03d}"


class IntakeClassifier:
    """
    Infers source metadata from file content and filename.

    Uses keyword patterns from intake_patterns.json and family codes
    from controlled_vocabulary.json.
    """

    def __init__(self) -> None:
        self._patterns = _load_patterns()
        self._family_codes = _load_family_codes()

    @property
    def family_codes(self) -> dict[str, str]:
        """Map of source_family -> family_code (e.g. museum_conservation -> MUS)."""
        return dict(self._family_codes)

    @property
    def capture_method_map(self) -> dict[str, str]:
        return dict(self._patterns["capture_method_map"])

    @property
    def source_type_by_family(self) -> dict[str, list[str]]:
        return dict(self._patterns.get("source_type_by_family", {}))

    def _scan_text(self, filename: str, content: str) -> str:
        """Combine filename and content into a single lowercase search string."""
        return f"{filename} {content}".lower()

    def _count_keyword_hits(self, text: str, keywords: list[str]) -> int:
        """Count how many keywords appear in the text."""
        return sum(1 for kw in keywords if kw.lower() in text)

    def _confidence_from_hits(self, hits: int) -> str:
        if hits >= 3:
            return "high"
        if hits >= 1:
            return "medium"
        return "low"

    def infer_source_family(self, filename: str, content: str) -> InferenceResult:
        """Infer source_family from filename + content keywords."""
        text = self._scan_text(filename, content)
        best_family = "unknown"
        best_hits = 0

        for family, config in self._patterns["source_family_patterns"].items():
            hits = self._count_keyword_hits(text, config["keywords"])
            if hits > best_hits:
                best_hits = hits
                best_family = family

        return InferenceResult(
            value=best_family,
            confidence=self._confidence_from_hits(best_hits),
            hits=best_hits,
        )

    def infer_domain(self, filename: str, content: str) -> InferenceResult:
        """Infer domain from filename + content keywords."""
        text = self._scan_text(filename, content)
        scores: dict[str, int] = {}

        for domain, keywords in self._patterns["domain_patterns"].items():
            hits = self._count_keyword_hits(text, keywords)
            if hits > 0:
                scores[domain] = hits

        if not scores:
            return InferenceResult(value="mixed", confidence="low", hits=0)

        max_hits = max(scores.values())
        top_domains = [d for d, h in scores.items() if h == max_hits]

        if len(top_domains) == 1:
            return InferenceResult(
                value=top_domains[0],
                confidence=self._confidence_from_hits(max_hits),
                hits=max_hits,
            )

        return InferenceResult(value="mixed", confidence="medium", hits=max_hits)

    def infer_capture_method(self, inbox_subfolder: str) -> str:
        """Infer capture_method from inbox subdirectory name."""
        return self._patterns["capture_method_map"].get(inbox_subfolder, "manual_entry")

    def read_content_preview(self, filepath: Path, max_chars: int = 2000) -> str:
        """
        Read the first max_chars of a file for keyword scanning.

        Returns empty string for binary files or read errors.
        """
        suffix = filepath.suffix.lower()
        if suffix in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"):
            return ""
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
            return text[:max_chars]
        except Exception as exc:
            logger.warning("Could not read %s for preview: %s", filepath, exc)
            return ""
