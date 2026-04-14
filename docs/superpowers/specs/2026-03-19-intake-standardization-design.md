# Intake Standardization Design

## Problem

Source files dropped into `data/inbox/` have no automated path to registration. Users must manually construct `source_id`, fill all metadata fields, rename files, and call `SourceCapture.register_source()`. This is error-prone and slow.

The existing `ingest` and `scan-inbox` CLI commands are broken — they reference fields that don't exist on `SourceRecord` (`source_title`, `approval_state`, `review_status`, `file_format`), call `registry.register()` which doesn't exist on `SourceRegistry`, and use hash-based IDs (`SRC-{sha256[:8]}`) instead of the canonical `SRC-{FAMILY_CODE}-{NNN}` format. This new `intake` command replaces both.

## Solution

A content-scanning intake tool that auto-infers classification metadata, prompts the user for what it cannot determine, renames files to a standardized convention, moves them to `data/raw/`, and registers them in the source register.

## Components

### `scripts/intake.py`

Standalone entry point. Accepts two modes:

- **Batch mode** (no args): scans all `data/inbox/` subdirectories for files, processes each sequentially.
- **Single file mode** (`--file path/to/file.pdf`): processes one file directly, does not need to be in inbox.

Also invocable from the CLI via a new `intake` subcommand in `cli.py` that delegates to the same logic.

### `src/oil_painting_rag/ingestion/intake_classifier.py`

New module. Responsibilities:

- Read file content (text-based formats) or fall back to filename-only analysis (PDFs, binaries).
- Match content and filename against keyword patterns from `intake_patterns.json`.
- Infer `source_family` and `domain` with a confidence level (high/medium/low).
- `source_type` is always prompted — too many valid values (22) for reliable keyword inference. The prompt shows values filtered to the inferred `source_family` as a numbered pick list.
- Auto-assign next `source_id` by reading existing IDs from `SourceRegistry.list_ids()` (the facade over `RegisterStore`), filtering by family code, and incrementing.
- Infer `capture_method` from the inbox subdirectory the file was found in.
- Read `family_codes` from `controlled_vocabulary.json` at runtime — do not hardcode the mapping.

### `src/oil_painting_rag/ingestion/intake_patterns.json`

Keyword/pattern configuration. Structure:

```json
{
  "source_family_patterns": {
    "museum_conservation": {
      "keywords": ["national gallery", "tate", "rijksmuseum", "technical bulletin", "conservation report", "examination report"],
      "weight": 1.0
    },
    "pigment_reference": {
      "keywords": ["kremer", "pigment", "colour index", "color of art", "artists pigments"],
      "weight": 1.0
    },
    "manufacturer": {
      "keywords": ["gamblin", "williamsburg", "old holland", "winsor", "schmincke", "tds", "sds", "product catalog"],
      "weight": 1.0
    },
    "historical_practice": {
      "keywords": ["treatise", "de mayerne", "cennini", "vasari", "atelier", "recipe"],
      "weight": 1.0
    },
    "color_theory": {
      "keywords": ["color theory", "colour theory", "color mixing", "munsell", "color wheel"],
      "weight": 1.0
    },
    "scientific_paper": {
      "keywords": ["doi", "abstract", "peer-reviewed", "journal", "spectroscopy", "chromatography"],
      "weight": 1.0
    }
  },
  "domain_patterns": {
    "pigment": ["pigment", "lead white", "ultramarine", "vermilion", "ochre", "cadmium", "cobalt", "titanium white"],
    "binder": ["linseed", "walnut oil", "poppy oil", "medium", "binder", "drying oil", "varnish"],
    "conservation": ["conservation", "restoration", "degradation", "cleaning", "retouching", "x-ray", "cross-section"],
    "historical_practice": ["treatise", "historical", "recipe", "guild", "apprentice", "palette"],
    "color_theory": ["color theory", "color mixing", "optical", "complementary", "value", "chroma"],
    "product": ["product", "catalog", "tds", "sds", "safety data", "technical data"],
    "technique": ["technique", "impasto", "glazing", "scumbling", "alla prima", "underpainting"]
  },
  "capture_method_map": {
    "pdf": "pdf_download",
    "html": "html_scrape",
    "markdown": "manual_transcription",
    "text": "manual_transcription",
    "other": "manual_entry"
  }
}
```

Extensible by adding keywords to the lists. The `capture_method_map` covers inbox subdirectories only; other valid capture methods (`ocr_scan`, `api_export`, `copy_paste`) are available via manual override at the prompt.

## Data Flow

```
data/inbox/{pdf,html,markdown,text,other}/
                    │
                    ▼
          scripts/intake.py (or CLI: intake subcommand)
                    │
                    ▼
          intake_classifier.py
          ├─ Read content (text) or filename (PDF — no text extraction, filename only)
          ├─ Match against intake_patterns.json
          ├─ Infer: source_family, domain
          ├─ Infer: capture_method from inbox subdirectory
          └─ Auto-assign: source_id (next available per family via SourceRegistry)
                    │
                    ▼
          Interactive prompt (per file):
          ├─ Display inferred values with confidence
          ├─ [Enter] to accept all inferred values
          ├─ Type field name to override specific values
          ├─ Prompt for: title, short_title, source_type, institution_or_publisher, access_type
          ├─ Optional: author, publication_year, source_url
          ├─ skip / quit commands for batch control
                    │
                    ▼
          File operations:
          1. Create destination dir: data/raw/{source_id}/
          2. shutil.move() file from inbox → data/raw/{source_id}/{renamed_file}
          3. SourceCapture.register_source() with raw_file_name = renamed filename
          4. SourceCapture.save_raw_file() is NOT called (file already moved by shutil)
             Instead, set raw_captured flag directly via register update
                    │
                    ▼
          Summary (single file or batch table)
```

### File move strategy

`SourceCapture.save_raw_file()` reads file content as `bytes`, which is wasteful for large PDFs. Instead, the intake tool:

1. Uses `shutil.move()` to relocate the file from inbox to `data/raw/{source_id}/`.
2. Calls `SourceCapture.register_source()` with `raw_file_name` set to the renamed filename.
3. Updates the source record's `raw_captured` flag to `True` via `SourceRegistry.update_field()`.

This avoids reading large files into memory just to write them back.

### PDF text extraction

PDF content scanning is out of scope for this spec. PDFs use filename-only inference. This is a known limitation — inference quality for PDFs depends entirely on descriptive filenames. A future enhancement could add optional `pdfplumber` or `pymupdf` extraction.

## Inference Details

### Source family inference

- Scan filename + first 2000 characters of content (text formats only) against `source_family_patterns` keyword lists.
- Count keyword hits per family. Family with the most hits wins.
- Confidence: high (3+ hits), medium (1-2 hits), low (0 hits, falls back to "unknown" — user must pick from numbered list).
- The 2000-character limit is a trade-off: fast scanning vs. missing content in files with long boilerplate headers.

### Domain inference

- Same keyword scan against `domain_patterns`.
- If multiple domains match equally, use `mixed`.

### Source type

- Always prompted. Not inferred — too many values (22) with subtle distinctions for keyword matching.
- Prompt displays values filtered by inferred `source_family` when a reasonable mapping exists (e.g., `museum_conservation` → `technical_bulletin`, `conservation_report`, `examination_report`, `treatment_record`).

### Source ID auto-assignment

- Read all existing source IDs from `SourceRegistry.list_ids()`.
- Look up family code from `controlled_vocabulary.json` `source_family.family_codes` (e.g., `museum_conservation` → `MUS`).
- Filter to IDs matching `SRC-{FAMILY_CODE}-\d+` pattern.
- Extract numeric suffix, take `max + 1`, zero-pad to 3 digits.
- Example: existing `SRC-MUS-001`, `SRC-MUS-002` → next is `SRC-MUS-003`.
- If no existing IDs for that family, start at `001`.

### Capture method inference

- Determined by which inbox subdirectory the file resides in.
- Map defined in `intake_patterns.json` under `capture_method_map`.
- For single-file mode (file not in inbox), defaults to `manual_entry` — user can override.

## Interactive Prompt UX

```
─── Intake: NGA_Tech_Bulletin_35_Lead_White.pdf ───
  Inferred:
    source_family : museum_conservation  (confidence: high)
    domain        : pigment              (confidence: medium)
    capture_method: pdf_download
    source_id     : SRC-MUS-001

  [Enter] to accept all, or type field name to override.
  > _

  Source type:
    1. technical_bulletin
    2. conservation_report
    3. examination_report
    4. treatment_record
  Pick [1-4]: _

  Title: _
  Short title: _
  Institution/publisher: _
  Access type [open_access/institutional_library/purchased/...]: _
```

For overrides, show the valid vocab values from `controlled_vocabulary.json` as a numbered list for the user to pick from.

## File Naming Convention

Final filename: `{source_id}_{sanitized_short_title}.{ext}`

The `source_id` prefix is prepended as-is (with hyphens preserved). Only the `short_title` portion is sanitized.

Sanitization rules for `short_title`:
- Lowercase
- Spaces and hyphens to underscores
- Strip all characters except `[a-z0-9_]`
- Collapse consecutive underscores
- Truncate to 60 characters (before extension)

Example: `SRC-MUS-001_nga_tech_bulletin_35_lead_white.pdf`

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Empty inbox | Print "No files found in inbox" and exit 0 |
| Unrecognized format (other/) | `capture_method: manual_entry`, all fields prompted, no content inference |
| Filename sanitization collision | Append `_2`, `_3` suffix |
| Interrupted batch | Already-moved files are registered; remaining stay in inbox. Re-run picks up |
| Source ID collision | Cannot happen — auto-increment from register max |
| `SourceRecord` extra fields | Not possible — `extra = "forbid"`. Only pass fields defined on the model. Do not pass arbitrary kwargs through `register_source()`. |

Note: Duplicate content hash detection was considered but deferred — `SourceRecord` has no `content_hash` field, and computing hashes across all raw files at scan time is slow. This can be added later by extending the model.

## Scope Boundary

The intake tool stops at registration. It does NOT:
- Normalize text to `data/clean/`
- Chunk or index
- Modify existing source records

These are separate downstream pipeline steps.

## CLI Changes

The new `intake` subcommand **replaces** the existing broken `ingest` and `scan-inbox` commands in `cli.py`. Those commands:
- Reference non-existent `SourceRecord` fields (`source_title`, `approval_state`, `review_status`, `file_format`)
- Call `registry.register()` which doesn't exist on `SourceRegistry`
- Use hash-based IDs (`SRC-{sha256[:8]}`) instead of canonical format

Both will be removed and replaced with a single `intake` command that delegates to the shared logic in `intake_classifier.py`.

Additionally, the `review` and `sources` CLI commands are also broken — they reference `s.source_title` (should be `s.short_title`) and `s.approval_state` (does not exist on `SourceRecord`). These will be fixed as part of the CLI modification:
- `s.source_title` → `s.short_title`
- `s.approval_state` → removed (filter/display by `ready_for_use` or `qa_reviewed` instead)

## Error Recovery

If `SourceCapture.register_source()` fails after `shutil.move()` has already relocated the file, the intake tool moves the file back to its original inbox location and logs the error. This prevents orphaned files in `data/raw/` with no corresponding registration.

The intake tool calls `register_source()` with only named parameters — never passes arbitrary kwargs, since `SourceRecord` has `extra = "forbid"`.

## Files Created/Modified

| File | Action |
|------|--------|
| `scripts/intake.py` | New — standalone entry point |
| `src/oil_painting_rag/ingestion/intake_classifier.py` | New — inference engine |
| `src/oil_painting_rag/ingestion/intake_patterns.json` | New — keyword config |
| `src/oil_painting_rag/cli.py` | Modified — remove broken `ingest`/`scan-inbox`, add `intake` subcommand |
| `src/oil_painting_rag/ingestion/__init__.py` | Modified — export new module |
