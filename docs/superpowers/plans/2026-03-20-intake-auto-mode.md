# Intake Auto Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--auto` flag to intake that processes files without prompts, using PDF metadata extraction and confidence-based auto-acceptance.

**Architecture:** New `pdf_metadata_reader.py` module for PDF metadata extraction. Modified `process_file()` with `auto` parameter that branches between auto-resolve (PDF meta + filename fallbacks) and existing interactive flow. CLI and script entry points pass through `--auto` flag.

**Tech Stack:** `pypdf` for PDF metadata, existing `IntakeClassifier` for inference, existing `SourceCapture` for registration.

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/oil_painting_rag/ingestion/pdf_metadata_reader.py` | Create | Extract title/author/creator from PDF metadata |
| `tests/test_pdf_metadata.py` | Create | Tests for PDF metadata extraction |
| `src/oil_painting_rag/ingestion/intake_classifier.py` | Modify | Add synthetic `"unknown": "UNK"` family code |
| `src/oil_painting_rag/ingestion/intake_runner.py` | Modify | Add `auto` param, auto-resolve branch, title derivation |
| `tests/test_intake.py` | Modify | Add auto-mode tests |
| `src/oil_painting_rag/cli.py` | Modify | Add `--auto` option to `intake` command |
| `scripts/intake.py` | Modify (via `intake_runner.main()`) | `--auto` argparse flag |
| `pyproject.toml` | Modify | Add `pypdf` dependency |

---

### Task 1: Add `pypdf` dependency and create `pdf_metadata_reader.py` (TDD)

**Files:**
- Modify: `pyproject.toml:6-11`
- Create: `src/oil_painting_rag/ingestion/pdf_metadata_reader.py`
- Create: `tests/test_pdf_metadata.py`

- [ ] **Step 1: Add `pypdf` to dependencies**

In `pyproject.toml`, add `"pypdf>=4.0.0"` to the `dependencies` list:

```toml
dependencies = [
    "chromadb>=0.4.0",
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.0.0",
    "pypdf>=4.0.0",
]
```

Then install: `pip install -e . --break-system-packages`

- [ ] **Step 2: Write failing tests**

Create `tests/test_pdf_metadata.py`:

```python
"""Tests for PDF metadata extraction."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestExtractPdfMetadata:
    def test_non_pdf_returns_none_values(self, tmp_path):
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("hello")
        result = extract_pdf_metadata(txt_file)
        assert result == {"title": None, "author": None, "creator": None}

    def test_missing_file_returns_none_values(self):
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        result = extract_pdf_metadata(Path("/nonexistent/file.pdf"))
        assert result == {"title": None, "author": None, "creator": None}

    def test_valid_pdf_extracts_metadata(self, tmp_path):
        """Create a minimal PDF with metadata using pypdf."""
        from pypdf import PdfWriter

        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata(
            {
                "/Title": "Test Bulletin",
                "/Author": "Jane Doe",
                "/Creator": "National Gallery",
            }
        )
        pdf_path = tmp_path / "test.pdf"
        with pdf_path.open("wb") as f:
            writer.write(f)

        result = extract_pdf_metadata(pdf_path)
        assert result["title"] == "Test Bulletin"
        assert result["author"] == "Jane Doe"
        assert result["creator"] == "National Gallery"

    def test_pdf_without_metadata_returns_none_values(self, tmp_path):
        """PDF with no /Info dictionary returns all None."""
        from pypdf import PdfWriter

        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        pdf_path = tmp_path / "empty_meta.pdf"
        with pdf_path.open("wb") as f:
            writer.write(f)

        result = extract_pdf_metadata(pdf_path)
        # All values should be None (no metadata set)
        assert result["title"] is None
        assert result["author"] is None
        assert result["creator"] is None

    def test_corrupted_file_returns_none_values(self, tmp_path):
        """Corrupted PDF-like file returns all None, no exception."""
        corrupt_pdf = tmp_path / "corrupt.pdf"
        corrupt_pdf.write_bytes(b"%PDF-1.4 this is not valid")
        result = None  # Ensure import works
        from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata

        result = extract_pdf_metadata(corrupt_pdf)
        assert result == {"title": None, "author": None, "creator": None}
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_pdf_metadata.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'oil_painting_rag.ingestion.pdf_metadata_reader'`

- [ ] **Step 4: Implement `pdf_metadata_reader.py`**

Create `src/oil_painting_rag/ingestion/pdf_metadata_reader.py`:

```python
"""
pdf_metadata_reader.py — Extract metadata from PDF files.

Uses pypdf to read the PDF document info dictionary (/Title, /Author, /Creator).
Returns all None on any failure — no exceptions leak out.
"""

from __future__ import annotations

from pathlib import Path

from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

_EMPTY_RESULT: dict[str, str | None] = {"title": None, "author": None, "creator": None}


def extract_pdf_metadata(filepath: Path) -> dict[str, str | None]:
    """
    Extract title, author, and creator from a PDF's document info dictionary.

    Returns {"title": ..., "author": ..., "creator": ...} with str values from
    the PDF metadata, or None for any field that is missing or unreadable.

    Returns all-None dict for non-PDF files, missing files, or read errors.
    """
    if filepath.suffix.lower() != ".pdf":
        return dict(_EMPTY_RESULT)

    try:
        from pypdf import PdfReader

        reader = PdfReader(filepath)
        meta = reader.metadata

        if meta is None:
            return dict(_EMPTY_RESULT)

        title = meta.get("/Title")
        author = meta.get("/Author")
        creator = meta.get("/Creator")

        return {
            "title": str(title).strip() if title else None,
            "author": str(author).strip() if author else None,
            "creator": str(creator).strip() if creator else None,
        }
    except Exception as exc:
        logger.debug("Could not read PDF metadata from %s: %s", filepath, exc)
        return dict(_EMPTY_RESULT)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_pdf_metadata.py -v`
Expected: 5 PASSED

- [ ] **Step 6: Run full test suite for regressions**

Run: `pytest tests/ -v`
Expected: 81 PASSED (76 existing + 5 new)

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/oil_painting_rag/ingestion/pdf_metadata_reader.py tests/test_pdf_metadata.py
git commit -m "feat: add PDF metadata reader with pypdf"
```

---

### Task 2: Add synthetic `"unknown": "UNK"` family code to `IntakeClassifier`

**Files:**
- Modify: `src/oil_painting_rag/ingestion/intake_classifier.py:109-111`
- Modify: `tests/test_intake.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_intake.py`:

```python
class TestUnknownFamilyCode:
    def test_classifier_has_unknown_family_code(self):
        from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
        clf = IntakeClassifier()
        assert "unknown" in clf.family_codes
        assert clf.family_codes["unknown"] == "UNK"

    def test_next_source_id_with_unk(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("UNK", existing_ids=[])
        assert result == "SRC-UNK-001"

    def test_next_source_id_unk_increments(self):
        from oil_painting_rag.ingestion.intake_classifier import next_source_id
        result = next_source_id("UNK", existing_ids=["SRC-UNK-001", "SRC-UNK-002"])
        assert result == "SRC-UNK-003"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_intake.py::TestUnknownFamilyCode -v`
Expected: `test_classifier_has_unknown_family_code` FAILS (no `"unknown"` key in family_codes). The `next_source_id` tests should PASS already since `next_source_id` just uses the string.

- [ ] **Step 3: Add synthetic UNK entry in `IntakeClassifier.__init__`**

In `src/oil_painting_rag/ingestion/intake_classifier.py`, modify the `__init__` method (line 109-111):

```python
    def __init__(self) -> None:
        self._patterns = _load_patterns()
        self._family_codes = _load_family_codes()
        # Synthetic entry for auto-mode unknown family handling
        self._family_codes.setdefault("unknown", "UNK")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_intake.py -v`
Expected: 19 PASSED (16 existing + 3 new)

- [ ] **Step 5: Commit**

```bash
git add src/oil_painting_rag/ingestion/intake_classifier.py tests/test_intake.py
git commit -m "feat: add synthetic UNK family code for auto-mode unknown handling"
```

---

### Task 3: Add auto-mode to `process_file()` and title derivation (TDD)

**Files:**
- Modify: `src/oil_painting_rag/ingestion/intake_runner.py:90-225`
- Modify: `tests/test_intake.py`

This is the largest task. It adds the `auto` parameter to `process_file()` and the auto-resolve branch.

- [ ] **Step 1: Write failing tests for title derivation helper**

Add to `tests/test_intake.py`:

```python
class TestTitleFromFilename:
    def test_hyphens_and_underscores_to_spaces(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("sennelier-NuancierHXF-EN.pdf")
        assert result == "Sennelier Nuancierhxf En"

    def test_extension_stripped(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("my_document.txt")
        assert result == "My Document"

    def test_no_extension(self):
        from oil_painting_rag.ingestion.intake_runner import _title_from_filename
        result = _title_from_filename("some-file")
        assert result == "Some File"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_intake.py::TestTitleFromFilename -v`
Expected: FAIL — `ImportError: cannot import name '_title_from_filename'`

- [ ] **Step 3: Implement `_title_from_filename`**

Add to `src/oil_painting_rag/ingestion/intake_runner.py`, after the existing imports and before `_prompt()`:

```python
import re as _re


def _title_from_filename(filename: str) -> str:
    """Derive a human-readable title from a filename.

    Strips extension, replaces hyphens/underscores with spaces, title-cases.
    """
    stem = Path(filename).stem
    spaced = _re.sub(r"[-_]+", " ", stem)
    return spaced.title()
```

- [ ] **Step 4: Run title derivation tests**

Run: `pytest tests/test_intake.py::TestTitleFromFilename -v`
Expected: 3 PASSED

- [ ] **Step 5: Write failing tests for auto-mode in `process_file`**

Add to `tests/test_intake.py`:

```python
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestAutoMode:
    """Test auto-mode field resolution in process_file."""

    def _make_classifier(self, family="manufacturer", family_conf="high",
                         domain="product", domain_conf="high"):
        """Create a mock classifier with controlled inference results."""
        from oil_painting_rag.ingestion.intake_classifier import InferenceResult

        clf = MagicMock()
        clf.family_codes = {"manufacturer": "MFR", "museum_conservation": "MUS", "unknown": "UNK"}
        clf.source_type_by_family = {"manufacturer": ["tds", "product_catalog", "sds"]}
        clf.read_content_preview.return_value = ""
        clf.infer_source_family.return_value = InferenceResult(
            value=family, confidence=family_conf, hits=3
        )
        clf.infer_domain.return_value = InferenceResult(
            value=domain, confidence=domain_conf, hits=3
        )
        clf.infer_capture_method.return_value = "pdf_download"
        return clf

    def _make_registry(self, existing_ids=None):
        registry = MagicMock()
        registry.list_ids.return_value = existing_ids or []
        return registry

    def _make_capture(self):
        return MagicMock()

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_flag_skips_prompts(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """With auto=True and high confidence, process_file completes without input()."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {
            "title": "Sennelier Product Catalog",
            "author": "Sennelier",
            "creator": "Sennelier SAS",
        }
        test_file = tmp_path / "sennelier-catalog.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier()
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-MFR-001"
        capture.register_source.assert_called_once()
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["title"] == "Sennelier Product Catalog"
        assert call_kwargs["institution_or_publisher"] == "Sennelier SAS"
        assert call_kwargs["source_type"] == "tds"  # first in source_type_by_family
        assert call_kwargs["access_type"] == "open_access"

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_uses_filename_when_no_pdf_title(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """When PDF has no title metadata, falls back to filename-derived title."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": None, "author": None, "creator": None}
        test_file = tmp_path / "sennelier-NuancierHXF-EN.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier()
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-MFR-001"
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["title"] == "Sennelier Nuancierhxf En"
        assert call_kwargs["institution_or_publisher"] == "unknown"

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_auto_unknown_family_uses_unk(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """With auto=True and unknown family, uses SRC-UNK-xxx."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": None, "author": None, "creator": None}
        test_file = tmp_path / "mystery-doc.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier(family="unknown", family_conf="low")
        registry = self._make_registry()
        capture = self._make_capture()

        result = process_file(test_file, "pdf", clf, registry, capture, auto=True)

        assert result == "SRC-UNK-001"
        call_kwargs = capture.register_source.call_args[1]
        assert call_kwargs["source_family"] == "unknown"
        assert call_kwargs["source_type"] == "web_article"  # fallback

    @patch("oil_painting_rag.ingestion.intake_runner.extract_pdf_metadata")
    @patch("oil_painting_rag.ingestion.intake_runner.shutil")
    @patch("oil_painting_rag.ingestion.intake_runner.cfg")
    def test_no_auto_flag_high_confidence_still_auto(self, mock_cfg, mock_shutil, mock_pdf_meta, tmp_path):
        """Without --auto, but high confidence on both family+domain → auto-processes."""
        from oil_painting_rag.ingestion.intake_runner import process_file

        mock_cfg.RAW_DIR = tmp_path
        mock_pdf_meta.return_value = {"title": "Test Title", "author": None, "creator": None}
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        clf = self._make_classifier(family_conf="high", domain_conf="high")
        registry = self._make_registry()
        capture = self._make_capture()

        # auto=False (default), but both confidences high → auto-process
        result = process_file(test_file, "pdf", clf, registry, capture, auto=False)

        assert result == "SRC-MFR-001"
        capture.register_source.assert_called_once()
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `pytest tests/test_intake.py::TestAutoMode -v`
Expected: FAIL — `process_file() got an unexpected keyword argument 'auto'`

- [ ] **Step 7: Implement auto-mode in `process_file()`**

Modify `src/oil_painting_rag/ingestion/intake_runner.py`. Add the PDF metadata import at the top (after existing imports):

```python
from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata
```

Then modify `process_file()` — add `auto: bool = False` parameter and the auto-resolve branch. The full modified function:

```python
def process_file(
    filepath: Path,
    inbox_subfolder: Optional[str],
    classifier: IntakeClassifier,
    registry: SourceRegistry,
    capture: SourceCapture,
    auto: bool = False,
) -> Optional[str]:
    """
    Process a single file through intake. Returns source_id on success, None on skip.
    Returns "QUIT" if user wants to stop batch processing.

    When auto=True, processes without prompts using inference + PDF metadata + fallbacks.
    When auto=False, auto-processes if both family and domain confidence are high/medium,
    otherwise falls back to interactive prompts.
    """
    print(f"\n{'─' * 60}")
    print(f"  Intake: {filepath.name}")
    print(f"{'─' * 60}")

    # --- Inference ---
    content = classifier.read_content_preview(filepath)
    family_result = classifier.infer_source_family(filepath.name, content)
    domain_result = classifier.infer_domain(filepath.name, content)
    capture_method = classifier.infer_capture_method(inbox_subfolder or "other")

    # Determine if we should auto-process
    should_auto = auto or (
        family_result.confidence in ("high", "medium")
        and domain_result.confidence in ("high", "medium")
        and family_result.value != "unknown"
    )

    # Get family code and next source_id
    family_codes = classifier.family_codes
    family_code = family_codes.get(family_result.value)

    if not family_code and should_auto:
        # Auto mode with unknown family → use UNK
        family_code = "UNK"
    elif not family_code and not should_auto:
        family_code = None

    if family_code:
        existing_ids = registry.list_ids()
        source_id = next_source_id(family_code, existing_ids)
    else:
        source_id = "SRC-???-001"

    if should_auto:
        return _auto_process(
            filepath=filepath,
            source_id=source_id,
            family_result=family_result,
            domain_result=domain_result,
            capture_method=capture_method,
            classifier=classifier,
            registry=registry,
            capture=capture,
        )

    # --- Interactive path (unchanged) ---
    # Display inferred values
    print(f"\n  Inferred:")
    print(f"    source_family : {family_result.value}  (confidence: {family_result.confidence})")
    print(f"    domain        : {domain_result.value}  (confidence: {domain_result.confidence})")
    print(f"    capture_method: {capture_method}")
    print(f"    source_id     : {source_id}")
    print()

    # Accept/override inferred values
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
        registry.update_field(source_id, "raw_captured", True)
        print(f"  Registered: {source_id} — {short_title}")
        return source_id

    except Exception as exc:
        logger.error("Registration failed for %s: %s", source_id, exc)
        print(f"  [ERROR] Registration failed: {exc}")
        try:
            shutil.move(str(dest_path), str(original_path))
            if dest_dir.exists() and not any(dest_dir.iterdir()):
                dest_dir.rmdir()
            print(f"  Rolled back file move.")
        except Exception as rollback_exc:
            logger.error("Rollback failed: %s", rollback_exc)
            print(f"  [ERROR] Rollback also failed: {rollback_exc}")
        return None
```

Now add the `_auto_process` helper function, placed after `_title_from_filename` and before `process_file`:

```python
def _auto_process(
    filepath: Path,
    source_id: str,
    family_result,
    domain_result,
    capture_method: str,
    classifier: IntakeClassifier,
    registry: SourceRegistry,
    capture: SourceCapture,
) -> Optional[str]:
    """Auto-process a file without prompts. Uses PDF metadata + filename fallbacks."""
    from oil_painting_rag.ingestion.intake_classifier import sanitize_short_title

    # --- Resolve fields from PDF metadata + fallbacks ---
    pdf_meta = extract_pdf_metadata(filepath)

    # Title
    title = pdf_meta["title"] or _title_from_filename(filepath.name)
    short_title = sanitize_short_title(pdf_meta["title"] or filepath.stem)

    # Institution / author
    institution = pdf_meta["creator"] or "unknown"
    author = pdf_meta["author"]

    # Source type — first from family mapping, fallback to web_article
    source_types = classifier.source_type_by_family.get(family_result.value, [])
    source_type = source_types[0] if source_types else "web_article"

    # Fixed defaults
    access_type = "open_access"
    publication_year = None
    source_url = None

    # --- File operations ---
    extension = filepath.suffix
    dest_dir = cfg.RAW_DIR / source_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_filename = build_intake_filename(source_id, short_title, extension, dest_dir=dest_dir)
    dest_path = dest_dir / new_filename

    original_path = filepath
    shutil.move(str(filepath), str(dest_path))

    # --- Print detailed summary ---
    print(f"[AUTO] {source_id}")
    print(f"  title      : {title}")
    print(f"  family     : {family_result.value} ({family_result.confidence})")
    print(f"  domain     : {domain_result.value} ({domain_result.confidence})")
    print(f"  source_type: {source_type}")
    print(f"  source     : {filepath.name} → data/raw/{source_id}/{new_filename}")

    # --- Register with rollback ---
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
        registry.update_field(source_id, "raw_captured", True)
        return source_id

    except Exception as exc:
        logger.error("Registration failed for %s: %s", source_id, exc)
        print(f"  [ERROR] Registration failed: {exc}")
        try:
            shutil.move(str(dest_path), str(original_path))
            if dest_dir.exists() and not any(dest_dir.iterdir()):
                dest_dir.rmdir()
            print(f"  Rolled back file move.")
        except Exception as rollback_exc:
            logger.error("Rollback failed: %s", rollback_exc)
            print(f"  [ERROR] Rollback also failed: {rollback_exc}")
        return None
```

- [ ] **Step 8: Run auto-mode tests**

Run: `pytest tests/test_intake.py::TestAutoMode -v`
Expected: 4 PASSED

- [ ] **Step 9: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS (previous tests + new tests)

- [ ] **Step 10: Commit**

```bash
git add src/oil_painting_rag/ingestion/intake_runner.py tests/test_intake.py
git commit -m "feat: add auto-mode to process_file with PDF metadata and filename fallbacks"
```

---

### Task 4: Wire `--auto` flag through CLI and script entry points

**Files:**
- Modify: `src/oil_painting_rag/cli.py:131-178`
- Modify: `src/oil_painting_rag/ingestion/intake_runner.py:228-282` (the `main()` function)

- [ ] **Step 1: Add `--auto` to CLI `intake` command**

In `src/oil_painting_rag/cli.py`, modify the `intake` function signature (line 132-134):

```python
@app.command()
def intake(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Process a single file (skip inbox scan)"),
    auto: bool = typer.Option(False, "--auto", help="Auto-process without prompts"),
) -> None:
```

Then pass `auto=auto` to both `process_file()` calls in the function body. Change line 153:

```python
        result = process_file(file, None, classifier, registry, capture, auto=auto)
```

And change line 169:

```python
            result = process_file(fpath, label, classifier, registry, capture, auto=auto)
```

- [ ] **Step 2: Add `--auto` to `intake_runner.main()`**

In `src/oil_painting_rag/ingestion/intake_runner.py`, modify the `main()` function. Add the argparse flag (after line 233):

```python
    parser.add_argument("--auto", action="store_true", help="Auto-process without prompts")
```

Then pass `auto=args.auto` to both `process_file()` calls. Change the single-file call:

```python
        result = process_file(args.file, None, classifier, registry, capture, auto=args.auto)
```

And the batch call:

```python
            result = process_file(fpath, label, classifier, registry, capture, auto=args.auto)
```

- [ ] **Step 3: Verify CLI shows `--auto` flag**

Run: `python -m oil_painting_rag.cli intake --help`
Expected: Shows `--auto` option in the output

- [ ] **Step 4: Verify scripts/intake.py shows `--auto` flag**

Run: `python scripts/intake.py --help`
Expected: Shows `--auto` option

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/oil_painting_rag/cli.py src/oil_painting_rag/ingestion/intake_runner.py
git commit -m "feat: wire --auto flag through CLI and script entry points"
```

---

### Task 5: End-to-end verification

- [ ] **Step 1: Run full test suite one final time**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Verify CLI --auto help text**

Run: `python -m oil_painting_rag.cli intake --help`
Expected: Shows both `--file` and `--auto` options

- [ ] **Step 3: Verify script --auto help text**

Run: `python scripts/intake.py --help`
Expected: Shows both `--file` and `--auto` options

- [ ] **Step 4: Verify imports are clean**

Run: `python -c "from oil_painting_rag.ingestion.pdf_metadata_reader import extract_pdf_metadata; print('OK')"`
Expected: `OK`

Run: `python -c "from oil_painting_rag.ingestion.intake_runner import process_file; print('OK')"`
Expected: `OK`
