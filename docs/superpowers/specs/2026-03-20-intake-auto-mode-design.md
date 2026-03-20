# Intake Auto Mode Design

**Date:** 2026-03-20
**Status:** Approved
**Extends:** [2026-03-19-intake-standardization-design.md](2026-03-19-intake-standardization-design.md)

## Problem

The current intake script requires 9 interactive prompts per file. This blocks non-TTY execution (e.g., from Claude Code's Bash tool) and makes batch processing tedious when files are well-named and classifiable.

## Solution

Add an `--auto` flag and confidence-based auto-processing to the intake pipeline. When the classifier is confident, skip all prompts. Use PDF metadata extraction and filename-derived fallbacks to fill fields that can't be inferred from content keywords.

## Components

### 1. New Module: `pdf_metadata_reader.py`

**Location:** `src/oil_painting_rag/ingestion/pdf_metadata_reader.py`

Single public function:

```python
def extract_pdf_metadata(filepath: Path) -> dict[str, str | None]
```

- Uses `pypdf` to read the PDF document info dictionary
- Returns dict with keys: `title`, `author`, `creator`
- Values come from PDF `/Title`, `/Author`, `/Creator` metadata fields
- Returns `{"title": None, "author": None, "creator": None}` if:
  - File is not a PDF (check extension)
  - PDF has no metadata
  - Any read error occurs (corrupted PDF, permission error, etc.)
- No exceptions leak out — all failures return the empty-result dict
- Dependency: `pypdf` (add to project dependencies in `pyproject.toml`)

### 2. Modified `process_file()` in `intake_runner.py`

New parameter: `auto: bool = False`

#### Auto-processing decision logic

```
if auto == True:
    → ALWAYS auto-process (--auto flag forces it)
    → Use SRC-UNK-xxx for unknown families

elif auto == False (default, no flag):
    if family confidence in (high, medium) AND domain confidence in (high, medium):
        → Auto-process this file
    else:
        → Fall back to existing interactive prompt flow
```

#### Auto-mode field resolution chain

When auto-processing, resolve all required `SourceRecord` fields without prompts:

| Field | Resolution order | Fallback |
|-------|-----------------|----------|
| `source_family` | Classifier inference | `"unknown"` |
| `domain` | Classifier inference | `"mixed"` |
| `source_id` | `next_source_id(family_code, existing_ids)` | `next_source_id("UNK", existing_ids)` if family unknown |
| `capture_method` | `infer_capture_method(inbox_subfolder)` | Always resolves |
| `title` | PDF metadata `/Title` | Filename stem with underscores→spaces, title-cased |
| `short_title` | PDF metadata `/Title` passed through `sanitize_short_title()` | Filename stem passed through `sanitize_short_title()` |
| `institution_or_publisher` | PDF metadata `/Creator` | `"unknown"` |
| `author` | PDF metadata `/Author` | `None` |
| `source_type` | First value from `source_type_by_family[family]` | `"web_article"` (most generic canonical value) |
| `access_type` | `"open_access"` | — |
| `publication_year` | `None` | — |
| `source_url` | `None` | — |

#### Title derivation from filename

When PDF metadata has no `/Title` or the file is not a PDF:

1. Take the filename stem (e.g., `sennelier-NuancierHXF-EN` from `sennelier-NuancierHXF-EN.pdf`)
2. Replace hyphens and underscores with spaces
3. Title-case the result → `"Sennelier Nuancierhxf En"`
4. Use this as `title`
5. For `short_title`, use the sanitized version (via existing `sanitize_short_title()`)

#### Auto-mode output (detailed, per file)

```
[AUTO] SRC-MFR-001
  title      : Sennelier NuancierHXF EN
  family     : manufacturer (high)
  domain     : product (high)
  source_type: product_catalog
  source     : sennelier-NuancierHXF-EN.pdf → data/raw/SRC-MFR-001/
```

#### Interactive fallback

When auto-processing is not triggered (low/unknown confidence without `--auto`), the existing interactive prompt flow runs exactly as today. No changes to the interactive path.

### 3. Modified `scripts/intake.py`

Add `--auto` flag to argparse:

```python
parser.add_argument("--auto", action="store_true", help="Auto-process without prompts")
```

Pass `auto=args.auto` to `process_file()` calls.

### 4. Modified `cli.py`

Add `--auto` option to the `intake` command:

```python
auto: bool = typer.Option(False, "--auto", help="Auto-process without prompts")
```

Pass `auto=auto` to `process_file()` calls.

### 5. Dependency: `pypdf`

Add `pypdf` to `pyproject.toml` dependencies. This is a lightweight, pure-Python PDF library with no native dependencies.

## Unknown Family Handling

When `source_family` inference returns `"unknown"`:

- **With `--auto` flag:** Use `"UNK"` as the family code. Generate `SRC-UNK-001`, `SRC-UNK-002`, etc. Register the file — user fixes the family later via review.
- **Without `--auto` (default mode):** Unknown family means low confidence, which triggers interactive fallback. The user picks the family manually (existing behavior).

This requires adding `"unknown": "UNK"` to the `family_codes` mapping if not already present. Check `controlled_vocabulary.json` — if `unknown` is not in `source_family.family_codes`, add it at runtime in `IntakeClassifier.__init__()` as a synthetic entry (don't modify the vocab file).

## Scope

- Stops at registration only (same as existing intake)
- No changes to chunking, indexing, or retrieval
- No changes to `SourceRecord` model
- Existing interactive mode preserved without regression
- Existing tests must continue to pass
