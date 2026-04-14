# Intake Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a content-scanning intake tool that auto-classifies source files, prompts for missing metadata, renames to a standard convention, and registers them in the source register.

**Architecture:** A new `IntakeClassifier` reads files and infers metadata via keyword matching against a pattern config. A standalone `scripts/intake.py` orchestrates the interactive flow — scanning inbox or processing a single file — then delegates to existing `SourceCapture` for registration. The CLI gets an `intake` subcommand that delegates to the same logic, replacing the broken `ingest`/`scan-inbox` commands.

**Tech Stack:** Python 3.12, Pydantic v2, Typer, Rich (for prompts/tables), shutil (file moves), json (pattern config)

**Spec:** `docs/superpowers/specs/2026-03-19-intake-standardization-design.md`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `src/oil_painting_rag/ingestion/intake_patterns.json` | Keyword config for source_family, domain, and capture_method inference |
| `src/oil_painting_rag/ingestion/intake_classifier.py` | Reads files, matches keywords, infers metadata, assigns source_id |
| `src/oil_painting_rag/ingestion/intake_runner.py` | Shared intake logic — `process_file`, inbox scanning, prompt helpers (used by both CLI and script) |
| `scripts/intake.py` | Standalone entry point — thin wrapper calling `intake_runner.main()` |
| `src/oil_painting_rag/cli.py` | Modified — remove broken `ingest`/`scan-inbox`, add `intake` subcommand, fix broken `review`/`sources` |
| `src/oil_painting_rag/ingestion/__init__.py` | Modified — export `IntakeClassifier` |
| `tests/test_intake.py` | Tests for classifier inference, sanitization, source ID generation |

---

## Task 1: Create intake_patterns.json

**Files:**
- Create: `src/oil_painting_rag/ingestion/intake_patterns.json`

- [ ] **Step 1: Create the pattern config file**

```json
{
  "source_family_patterns": {
    "museum_conservation": {
      "keywords": ["national gallery", "tate", "rijksmuseum", "met", "getty", "technical bulletin", "conservation report", "examination report", "treatment record"],
      "weight": 1.0
    },
    "pigment_reference": {
      "keywords": ["kremer", "pigment", "colour index", "color of art", "artists pigments", "pigment handbook", "color chart"],
      "weight": 1.0
    },
    "manufacturer": {
      "keywords": ["gamblin", "williamsburg", "old holland", "winsor", "schmincke", "blockx", "vasari", "rublev", "tds", "sds", "product catalog", "technical data sheet", "safety data sheet"],
      "weight": 1.0
    },
    "historical_practice": {
      "keywords": ["treatise", "de mayerne", "cennini", "vasari", "atelier", "recipe", "guild", "historical"],
      "weight": 1.0
    },
    "color_theory": {
      "keywords": ["color theory", "colour theory", "color mixing", "munsell", "color wheel", "gamut", "complementary"],
      "weight": 1.0
    },
    "scientific_paper": {
      "keywords": ["doi", "abstract", "peer-reviewed", "journal", "spectroscopy", "chromatography", "raman", "ftir", "xrf"],
      "weight": 1.0
    }
  },
  "domain_patterns": {
    "pigment": ["pigment", "lead white", "ultramarine", "vermilion", "ochre", "cadmium", "cobalt", "titanium white", "zinc white", "umber", "sienna"],
    "binder": ["linseed", "walnut oil", "poppy oil", "medium", "binder", "drying oil", "varnish", "stand oil", "alkyd"],
    "conservation": ["conservation", "restoration", "degradation", "cleaning", "retouching", "x-ray", "cross-section", "inpainting"],
    "historical_practice": ["treatise", "historical", "recipe", "guild", "apprentice", "palette", "practice"],
    "color_theory": ["color theory", "color mixing", "optical", "complementary", "value", "chroma", "hue"],
    "product": ["product", "catalog", "tds", "sds", "safety data", "technical data"],
    "technique": ["technique", "impasto", "glazing", "scumbling", "alla prima", "underpainting", "grisaille"]
  },
  "capture_method_map": {
    "pdf": "pdf_download",
    "html": "html_scrape",
    "markdown": "manual_transcription",
    "text": "manual_transcription",
    "other": "manual_entry"
  },
  "source_type_by_family": {
    "museum_conservation": ["technical_bulletin", "conservation_report", "examination_report", "treatment_record"],
    "pigment_reference": ["pigment_handbook", "pigment_database", "material_reference"],
    "manufacturer": ["tds", "product_catalog", "sds"],
    "historical_practice": ["historical_treatise", "atelier_manual", "period_recipe"],
    "color_theory": ["color_theory_text", "color_reference"],
    "scientific_paper": ["peer_reviewed_paper", "conference_paper", "technical_monograph"]
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/oil_painting_rag/ingestion/intake_patterns.json
git commit -m "feat: add intake keyword patterns config"
```

---

## Task 2: Build IntakeClassifier with tests (TDD)

**Files:**
- Create: `src/oil_painting_rag/ingestion/intake_classifier.py`
- Create: `tests/test_intake.py`

- [ ] **Step 1: Write failing tests for filename sanitization**

Create `tests/test_intake.py`:

```python
"""Tests for intake classifier — metadata inference, sanitization, source ID generation."""

from __future__ import annotations

import pytest


class TestSanitizeShortTitle:
    """Test the short_title → filename-safe string sanitization."""

    def test_basic_sanitization(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

        assert sanitize_short_title("NGA Tech Bulletin 35") == "nga_tech_bulletin_35"

    def test_hyphens_become_underscores(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

        assert sanitize_short_title("Lead-White Study") == "lead_white_study"

    def test_special_chars_stripped(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

        assert sanitize_short_title("Pigment (Vol. 3): Analysis!") == "pigment_vol_3_analysis"

    def test_consecutive_underscores_collapsed(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

        assert sanitize_short_title("A   B---C") == "a_b_c"

    def test_truncation_at_60_chars(self):
        from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

        long_title = "a" * 80
        result = sanitize_short_title(long_title)
        assert len(result) == 60
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_intake.py -v`
Expected: FAIL — `intake_classifier` module does not exist yet.

- [ ] **Step 3: Write failing tests for source family inference**

Append to `tests/test_intake.py`:

```python
class TestInferSourceFamily:
    """Test keyword-based source_family inference."""

    def test_museum_conservation_from_content(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier

        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="bulletin.pdf",
            content="National Gallery Technical Bulletin conservation report on lead white"
        )
        assert result.value == "museum_conservation"
        assert result.confidence == "high"

    def test_manufacturer_from_filename(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier

        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="gamblin_tds_titanium_white.pdf",
            content=""
        )
        assert result.value == "manufacturer"

    def test_unknown_when_no_match(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier

        clf = IntakeClassifier()
        result = clf.infer_source_family(
            filename="notes.txt",
            content="some generic text"
        )
        assert result.value == "unknown"
        assert result.confidence == "low"
```

- [ ] **Step 4: Write failing tests for domain inference**

Append to `tests/test_intake.py`:

```python
class TestInferDomain:
    """Test keyword-based domain inference."""

    def test_pigment_domain(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier

        clf = IntakeClassifier()
        result = clf.infer_domain(
            filename="lead_white.pdf",
            content="Lead white pigment analysis with titanium white comparison"
        )
        assert result.value == "pigment"

    def test_mixed_domain_on_tie(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier

        clf = IntakeClassifier()
        result = clf.infer_domain(
            filename="study.pdf",
            content="pigment conservation lead white degradation"
        )
        # pigment: "pigment", "lead white" = 2 hits; conservation: "conservation", "degradation" = 2 hits — tie → mixed
        assert result.value == "mixed"
```

- [ ] **Step 5: Write failing tests for source ID auto-assignment**

Append to `tests/test_intake.py`:

```python
class TestNextSourceId:
    """Test source_id auto-increment logic."""

    def test_first_source_in_family(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id

        # No existing IDs for MUS family
        result = next_source_id("MUS", existing_ids=[])
        assert result == "SRC-MUS-001"

    def test_increment_from_existing(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id

        result = next_source_id("MUS", existing_ids=["SRC-MUS-001", "SRC-MUS-002", "SRC-PIG-001"])
        assert result == "SRC-MUS-003"

    def test_handles_gaps(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id

        # Gap at 002 — should still use max+1
        result = next_source_id("PIG", existing_ids=["SRC-PIG-001", "SRC-PIG-005"])
        assert result == "SRC-PIG-006"
```

- [ ] **Step 6: Write failing test for build_filename**

Append to `tests/test_intake.py`:

```python
class TestBuildFilename:
    """Test standardized filename construction."""

    def test_basic_filename(self):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename

        result = build_intake_filename("SRC-MUS-001", "NGA Tech Bulletin 35", ".pdf")
        assert result == "SRC-MUS-001_nga_tech_bulletin_35.pdf"

    def test_long_title_truncated(self):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename

        long_title = "a" * 80
        result = build_intake_filename("SRC-MUS-001", long_title, ".pdf")
        # source_id prefix is prepended as-is, only short_title portion truncated to 60
        assert result == f"SRC-MUS-001_{'a' * 60}.pdf"

    def test_collision_suffix(self, tmp_path):
        from oil_painting_rag.ingestion.intake_classifier import build_intake_filename

        # Create a file that would collide
        (tmp_path / "SRC-MUS-001_bulletin.pdf").touch()
        result = build_intake_filename("SRC-MUS-001", "Bulletin", ".pdf", dest_dir=tmp_path)
        assert result == "SRC-MUS-001_bulletin_2.pdf"
```

- [ ] **Step 7: Run all tests to confirm they fail**

Run: `pytest tests/test_intake.py -v`
Expected: all FAIL — module does not exist.

- [ ] **Step 8: Implement IntakeClassifier**

Create `src/oil_painting_rag/ingestion/intake_classifier.py`:

```python
"""
intake_classifier.py — Content-scanning metadata inference for source intake.

Reads file content and filenames, matches against keyword patterns from
intake_patterns.json, and infers source_family, domain, capture_method.
Auto-assigns source_id by incrementing from existing registrations.

Does NOT move files or register sources — that is the intake script's job.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
    import oil_painting_rag.config as cfg

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
        """Map of source_family → family_code (e.g. museum_conservation → MUS)."""
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

    def infer_source_family(
        self, filename: str, content: str
    ) -> InferenceResult:
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
        # Skip binary formats — use filename only
        if suffix in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"):
            return ""
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
            return text[:max_chars]
        except Exception as exc:
            logger.warning("Could not read %s for preview: %s", filepath, exc)
            return ""
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `pytest tests/test_intake.py -v`
Expected: all PASS.

- [ ] **Step 10: Commit**

```bash
git add src/oil_painting_rag/ingestion/intake_classifier.py tests/test_intake.py
git commit -m "feat: add IntakeClassifier with keyword inference and tests"
```

---

## Task 3: Build the intake runner and standalone script

**Files:**
- Create: `src/oil_painting_rag/ingestion/intake_runner.py`
- Create: `scripts/intake.py`

- [ ] **Step 1: Create the scripts directory**

```bash
mkdir -p scripts
```

- [ ] **Step 2: Write the shared intake runner**

Create `src/oil_painting_rag/ingestion/intake_runner.py` — this contains all the shared logic (`process_file`, `_collect_inbox_files`, prompt helpers, `main`). Both `scripts/intake.py` and `cli.py` import from here:

```python
"""
intake_runner.py — Shared intake orchestration logic.

Contains process_file(), prompt helpers, inbox scanning, and main().
Used by both scripts/intake.py and the CLI intake subcommand.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.ingestion.capture import SourceCapture
from oil_painting_rag.ingestion.intake_classifier import (
    IntakeClassifier,
    build_intake_filename,
    next_source_id,
)
from oil_painting_rag.ingestion.source_registry import SourceRegistry
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


def _prompt(label: str, default: Optional[str] = None) -> str:
    """Prompt user for input with optional default."""
    if default:
        raw = input(f"  {label} [{default}]: ").strip()
        return raw if raw else default
    while True:
        raw = input(f"  {label}: ").strip()
        if raw:
            return raw
        print("    (required)")


def _prompt_pick(label: str, options: list[str], default: Optional[str] = None) -> str:
    """Prompt user to pick from a numbered list."""
    print(f"  {label}:")
    for i, opt in enumerate(options, 1):
        marker = " *" if opt == default else ""
        print(f"    {i}. {opt}{marker}")
    while True:
        raw = input(f"  Pick [1-{len(options)}]: ").strip()
        if not raw and default:
            return default
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            # Allow typing the value directly
            if raw in options:
                return raw
        print(f"    (enter 1-{len(options)})")


def _collect_inbox_files() -> list[tuple[Path, str]]:
    """Scan inbox subdirectories for files. Returns (path, subfolder_name) pairs."""
    inbox_subdirs = {
        "pdf": cfg.INBOX_PDF_DIR,
        "html": cfg.INBOX_HTML_DIR,
        "markdown": cfg.INBOX_MARKDOWN_DIR,
        "text": cfg.INBOX_TEXT_DIR,
        "other": cfg.INBOX_OTHER_DIR,
    }
    files: list[tuple[Path, str]] = []
    for label, inbox_path in inbox_subdirs.items():
        if not inbox_path.exists():
            continue
        for fpath in sorted(inbox_path.iterdir()):
            if fpath.is_file() and fpath.name != ".gitkeep" and not fpath.name.startswith("."):
                files.append((fpath, label))
    return files


def _load_vocab_values(key: str) -> list[str]:
    """Load valid values for a vocabulary key from controlled_vocabulary.json."""
    import json

    vocab_path = cfg.VOCAB_DIR / "controlled_vocabulary.json"
    with vocab_path.open("r", encoding="utf-8") as fh:
        vocab = json.load(fh)
    return vocab.get(key, {}).get("values", [])


def process_file(
    filepath: Path,
    inbox_subfolder: Optional[str],
    classifier: IntakeClassifier,
    registry: SourceRegistry,
    capture: SourceCapture,
) -> Optional[str]:
    """
    Process a single file through intake. Returns source_id on success, None on skip.
    """
    print(f"\n{'─' * 60}")
    print(f"  Intake: {filepath.name}")
    print(f"{'─' * 60}")

    # --- Inference ---
    content = classifier.read_content_preview(filepath)
    family_result = classifier.infer_source_family(filepath.name, content)
    domain_result = classifier.infer_domain(filepath.name, content)
    capture_method = classifier.infer_capture_method(inbox_subfolder or "other")

    # Get family code and next source_id
    family_codes = classifier.family_codes
    family_code = family_codes.get(family_result.value)

    if family_code:
        existing_ids = registry.list_ids()
        source_id = next_source_id(family_code, existing_ids)
    else:
        source_id = "SRC-???-001"

    # --- Display inferred values ---
    print(f"\n  Inferred:")
    print(f"    source_family : {family_result.value}  (confidence: {family_result.confidence})")
    print(f"    domain        : {domain_result.value}  (confidence: {domain_result.confidence})")
    print(f"    capture_method: {capture_method}")
    print(f"    source_id     : {source_id}")
    print()

    # --- Accept/override inferred values ---
    raw = input("  [Enter] to accept inferred, 'skip' to skip, 'quit' to stop: ").strip().lower()
    if raw == "quit":
        return "QUIT"
    if raw == "skip":
        print("  Skipped.")
        return None

    # Allow overriding inferred values
    if raw:
        if family_result.confidence == "low" or raw == "source_family":
            families = list(family_codes.keys())
            family_result_value = _prompt_pick("source_family", families)
            family_code = family_codes[family_result_value]
            existing_ids = registry.list_ids()
            source_id = next_source_id(family_code, existing_ids)
        if raw == "domain":
            domains = _load_vocab_values("domain")
            domain_result_value = _prompt_pick("domain", domains, domain_result.value)
    else:
        # If family was unknown, must pick
        if family_result.value == "unknown":
            families = list(family_codes.keys())
            family_result_value = _prompt_pick("source_family", families)
            family_code = family_codes[family_result_value]
            family_result = type(family_result)(value=family_result_value, confidence="manual", hits=0)
            existing_ids = registry.list_ids()
            source_id = next_source_id(family_code, existing_ids)

    # --- Prompt for required fields ---
    # Source type — filtered by family
    source_types = classifier.source_type_by_family.get(family_result.value, [])
    if not source_types:
        source_types = _load_vocab_values("source_type")
    source_type = _prompt_pick("source_type", source_types)

    title = _prompt("Title")
    short_title = _prompt("Short title")
    institution = _prompt("Institution/publisher")

    access_types = _load_vocab_values("access_type")
    access_type = _prompt_pick("access_type", access_types)

    # Optional fields
    author = input("  Author (optional): ").strip() or None
    pub_year_raw = input("  Publication year (optional): ").strip()
    publication_year = int(pub_year_raw) if pub_year_raw.isdigit() else None
    source_url = input("  Source URL (optional): ").strip() or None

    # --- File operations ---
    extension = filepath.suffix
    dest_dir = cfg.RAW_DIR / source_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_filename = build_intake_filename(source_id, short_title, extension, dest_dir=dest_dir)
    dest_path = dest_dir / new_filename

    # Move file
    original_path = filepath
    shutil.move(str(filepath), str(dest_path))
    print(f"\n  Moved: {filepath.name} → data/raw/{source_id}/{new_filename}")

    # Register — rollback file move on failure
    try:
        capture.register_source(
            source_id=source_id,
            title=title,
            short_title=short_title,
            source_family=family_result.value,
            source_type=source_type,
            institution_or_publisher=institution,
            domain=domain_result.value,
            capture_method=capture_method,
            access_type=access_type,
            raw_file_name=new_filename,
            author=author,
            publication_year=publication_year,
            source_url=source_url,
        )
        # Set raw_captured flag
        registry.update_field(source_id, "raw_captured", True)
        print(f"  Registered: {source_id} — {short_title}")
        return source_id

    except Exception as exc:
        # Rollback: move file back to original location
        logger.error("Registration failed for %s: %s", source_id, exc)
        print(f"  [ERROR] Registration failed: {exc}")
        try:
            shutil.move(str(dest_path), str(original_path))
            # Clean up empty dest dir
            if dest_dir.exists() and not any(dest_dir.iterdir()):
                dest_dir.rmdir()
            print(f"  Rolled back file move.")
        except Exception as rollback_exc:
            logger.error("Rollback failed: %s", rollback_exc)
            print(f"  [ERROR] Rollback also failed: {rollback_exc}")
        return None


def main() -> None:
    """Entry point for the intake script."""
    import argparse

    parser = argparse.ArgumentParser(description="Oil Painting RAG — Source Intake")
    parser.add_argument("--file", type=Path, help="Process a single file (skip inbox scan)")
    args = parser.parse_args()

    cfg.ensure_data_dirs()
    classifier = IntakeClassifier()
    registry = SourceRegistry()
    capture = SourceCapture()

    if args.file:
        # Single file mode
        if not args.file.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        result = process_file(args.file, None, classifier, registry, capture)
        if result and result != "QUIT":
            print(f"\nDone: registered {result}")
    else:
        # Batch mode — scan inbox
        files = _collect_inbox_files()
        if not files:
            print("No files found in data/inbox/")
            return

        print(f"Found {len(files)} file(s) in inbox:")
        for fpath, label in files:
            print(f"  [{label}] {fpath.name}")
        print()

        registered: list[str] = []
        skipped = 0

        for fpath, label in files:
            result = process_file(fpath, label, classifier, registry, capture)
            if result == "QUIT":
                print("\nStopped by user.")
                break
            elif result:
                registered.append(result)
            else:
                skipped += 1

        print(f"\nDone: {len(registered)} registered, {skipped} skipped, {len(files)} total")
        if registered:
            print("Registered IDs:")
            for sid in registered:
                print(f"  {sid}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write the standalone script wrapper**

Create `scripts/intake.py`:

```python
#!/usr/bin/env python3
"""Standalone entry point for source intake. Delegates to intake_runner."""

import sys
from pathlib import Path

# Ensure project root is on sys.path when run as standalone script
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from oil_painting_rag.ingestion.intake_runner import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Make the script executable**

```bash
chmod +x scripts/intake.py
```

- [ ] **Step 5: Commit**

```bash
git add src/oil_painting_rag/ingestion/intake_runner.py scripts/intake.py
git commit -m "feat: add intake runner and standalone script"
```

---

## Task 4: Update CLI — replace broken commands, add intake subcommand

**Files:**
- Modify: `src/oil_painting_rag/cli.py`

- [ ] **Step 1: Remove broken `ingest` command**

Remove the `ingest` function (cli.py lines 132-181) entirely — the `@app.command()` decorator, the function signature, and the function body.

- [ ] **Step 2: Remove broken `scan-inbox` command**

Remove the `scan_inbox` function (cli.py lines 188-271) entirely.

- [ ] **Step 3: Add `intake` subcommand**

Add the new `intake` command in place of the removed commands:

```python
@app.command()
def intake(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Process a single file (skip inbox scan)"),
) -> None:
    """Intake source files — scan inbox or process a single file."""
    from oil_painting_rag.ingestion.intake_runner import process_file, _collect_inbox_files
    from oil_painting_rag.ingestion.capture import SourceCapture
    from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    cfg.ensure_data_dirs()

    classifier = IntakeClassifier()
    registry = SourceRegistry()
    capture = SourceCapture()

    if file:
        if not file.exists():
            console.print(f"[red]File not found:[/red] {file}")
            raise typer.Exit(1)
        result = process_file(file, None, classifier, registry, capture)
        if result and result != "QUIT":
            console.print(f"[green]Done:[/green] registered {result}")
    else:
        files = _collect_inbox_files()
        if not files:
            console.print("[yellow]No files found in data/inbox/[/yellow]")
            return

        console.print(f"Found [bold]{len(files)}[/bold] file(s) in inbox:")
        for fpath, label in files:
            console.print(f"  [{label}] {fpath.name}")

        registered: list[str] = []
        skipped = 0
        for fpath, label in files:
            result = process_file(fpath, label, classifier, registry, capture)
            if result == "QUIT":
                console.print("\nStopped by user.")
                break
            elif result:
                registered.append(result)
            else:
                skipped += 1

        console.print(f"\n[bold]Done:[/bold] {len(registered)} registered, {skipped} skipped, {len(files)} total")
```

- [ ] **Step 4: Fix broken `review` command**

In the `review` function (cli.py around line 405-428), fix the broken field references:

Replace `s.approval_state` filter (line 415) — change the command to filter by `qa_reviewed` status:

```python
@app.command()
def review(
    reviewed: bool = typer.Option(False, "--reviewed", help="Show reviewed sources (default: unreviewed)"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Show sources pending review."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    registry = SourceRegistry()
    sources = [s for s in registry.all_sources() if s.qa_reviewed == reviewed][:limit]

    label = "Reviewed" if reviewed else "Pending Review"
    if not sources:
        console.print(f"No {label.lower()} sources found.")
        return

    t = Table(title=f"Sources — {label}")
    t.add_column("Source ID")
    t.add_column("Title")
    t.add_column("Domain")
    t.add_column("Tier", justify="right")
    for s in sources:
        t.add_row(s.source_id, s.short_title[:50], s.domain, str(s.trust_tier))
    console.print(t)
```

- [ ] **Step 5: Fix broken `sources` command**

In the `sources` function (cli.py around line 486-517), fix the broken field references:

Replace `s.source_title` with `s.short_title` and `s.approval_state` with `s.ready_for_use`:

```python
@app.command()
def sources(
    domain: Optional[str] = typer.Option(None, "--domain"),
    tier: Optional[int] = typer.Option(None, "--tier"),
    limit: int = typer.Option(50, "--limit", "-n"),
) -> None:
    """List registered sources."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    registry = SourceRegistry()
    all_src = registry.all_sources()

    if domain:
        all_src = [s for s in all_src if s.domain == domain]
    if tier is not None:
        all_src = [s for s in all_src if s.trust_tier == tier]

    all_src = all_src[:limit]
    if not all_src:
        console.print("No sources found.")
        return

    t = Table(title="Registered Sources")
    t.add_column("Source ID")
    t.add_column("Title")
    t.add_column("Domain")
    t.add_column("Tier", justify="right")
    t.add_column("Ready")
    for s in all_src:
        ready = "Yes" if s.ready_for_use else "No"
        t.add_row(s.source_id, s.short_title[:40], s.domain, str(s.trust_tier), ready)
    console.print(t)
```

- [ ] **Step 6: Update CLI docstring**

Update the module docstring at the top of cli.py to reflect the new command list:

```python
"""
cli.py — Typer command-line interface for the Oil Painting Research Assistant.

Commands:
    ask         Ask a question using the full RAG pipeline
    intake      Intake source files — scan inbox or process a single file
    chunk       Chunk an ingested source
    index       Index chunked sources into ChromaDB + BM25
    status      Show index and source register status
    benchmark   Run the benchmark gold set
    review      Show sources pending review
    rebuild     Rebuild indexes from stored chunks
    conflicts   List active conflict records
    sources     List registered sources
    vocab       Show controlled vocabulary summary
"""
```

- [ ] **Step 7: Run existing tests to check for regressions**

Run: `pytest tests/ -v`
Expected: all 60 existing tests PASS.

- [ ] **Step 8: Commit**

```bash
git add src/oil_painting_rag/cli.py
git commit -m "feat: replace broken ingest/scan-inbox with intake command, fix review/sources"
```

---

## Task 5: Update ingestion __init__.py exports

**Files:**
- Modify: `src/oil_painting_rag/ingestion/__init__.py`

- [ ] **Step 1: Add IntakeClassifier to exports**

```python
"""ingestion — Source capture, loading, and registry for the Oil Painting Research Assistant."""

from oil_painting_rag.ingestion.capture import SourceCapture
from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
from oil_painting_rag.ingestion.intake_runner import process_file
from oil_painting_rag.ingestion.loader import SourceLoader
from oil_painting_rag.ingestion.source_registry import SourceRegistry

__all__ = ["IntakeClassifier", "SourceCapture", "SourceLoader", "SourceRegistry", "process_file"]
```

- [ ] **Step 2: Run all tests**

Run: `pytest tests/ -v`
Expected: all tests PASS (existing 60 + new intake tests).

- [ ] **Step 3: Commit**

```bash
git add src/oil_painting_rag/ingestion/__init__.py
git commit -m "chore: export IntakeClassifier from ingestion package"
```

---

## Task 6: End-to-end smoke test

- [ ] **Step 1: Create a test file in inbox**

```bash
echo "National Gallery Technical Bulletin on lead white pigment conservation and degradation mechanisms" > data/inbox/text/test_nga_bulletin.txt
```

- [ ] **Step 2: Run the intake script in single-file mode**

```bash
python scripts/intake.py --file data/inbox/text/test_nga_bulletin.txt
```

Expected: infers `museum_conservation` (high), `pigment` or `conservation` domain, prompts for title/short_title/source_type/institution/access_type, moves file, registers.

- [ ] **Step 3: Verify the file was moved and registered**

```bash
ls data/raw/SRC-MUS-*/
python -m oil_painting_rag.cli sources
```

Expected: file present in `data/raw/SRC-MUS-001/`, source listed in CLI output.

- [ ] **Step 4: Clean up test data**

```bash
rm -rf data/raw/SRC-MUS-001
# Remove the source registration if needed for re-testing
```

- [ ] **Step 5: Final commit — all tests pass**

Run: `pytest tests/ -v`

```bash
git add src/oil_painting_rag/ingestion/ scripts/intake.py src/oil_painting_rag/cli.py tests/test_intake.py
git commit -m "feat: complete intake standardization — classifier, script, CLI integration"
```
