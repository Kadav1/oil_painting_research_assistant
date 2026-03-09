# File Naming Policy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-008
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Naming conventions for all file types in the Oil Painting Research Assistant — source IDs, chunk IDs, benchmark IDs, raw files, clean files, metadata files, schema files, log files, script files, and documentation files
**Applies to:** All code, ingestion logic, review workflows, storage backends, schema validators, and documentation authors working in the Oil Painting Research Assistant repository

---

# 1. Purpose

This document defines the canonical file and ID naming conventions for the Oil Painting Research Assistant.

It specifies:

* the ID format for sources, chunks, and benchmarks
* the naming convention for raw, clean, metadata, schema, and log files
* the directory layout each file type must reside in
* the rules for generating new IDs and filenames consistently
* the stability guarantees for IDs once assigned
* the prohibited naming patterns

This is the operational naming standard. All ingestion code, review tools, CLI scripts, and documentation must follow it.

---

# 2. Core Principle

**Every file and record in this system must be identifiable, locatable, and stable.**

A name is not just a label. A name is an address. Once assigned, IDs and filenames that serve as persistent identifiers (source IDs, chunk IDs, benchmark IDs) must not change. Downstream systems — ChromaDB indexes, metadata stores, log entries, benchmark records — all reference these IDs. Changing them breaks provenance chains.

Human-readable names (documentation files, script files, policy files) follow a consistent pattern to support navigation and `grep`-based discovery.

---

# 3. Objectives

1. Eliminate ambiguity in how records and files are named across all system layers
2. Ensure IDs are stable once assigned — no regeneration, no renaming after indexing
3. Ensure filenames are predictable enough to construct programmatically without a lookup
4. Ensure naming conventions are consistent with ChromaDB document ID requirements
5. Provide clear rules for assigning new IDs when new sources, chunks, or benchmarks are registered

---

# 4. ID Naming Conventions

## 4.1 Source IDs

**Format:** `SRC-{FAMILY_CODE}-{NNN}`

Where:
- `{FAMILY_CODE}` is the uppercase three-letter code for the source family
- `{NNN}` is a zero-padded three-digit sequence number, starting at `001`

| Source Family | Family Code | Example |
|--------------|-------------|---------|
| `museum_conservation` | `MUS` | `SRC-MUS-001` |
| `pigment_reference` | `PIG` | `SRC-PIG-001` |
| `manufacturer` | `MFR` | `SRC-MFR-001` |
| `color_theory` | `COL` | `SRC-COL-001` |
| `historical_practice` | `HIS` | `SRC-HIS-001` |
| `scientific_paper` | `SCI` | `SRC-SCI-001` |

Rules:
- Source IDs are assigned at intake registration and never changed after assignment
- Sequence numbers are assigned per family and never reused, even if a source is removed
- If a source family is not in the table above, it must be added to `docs/foundation/controlled_vocabulary.md` §3.1 before a source ID in that family can be issued

## 4.2 Chunk IDs

**Format:** `CHK-{source_id}-{NNN}`

Where:
- `{source_id}` is the full source ID of the parent source (e.g. `SRC-MUS-001`)
- `{NNN}` is a zero-padded three-digit sequence number within that source, starting at `001`

Examples:
- `CHK-SRC-MUS-001-001` (first chunk of source SRC-MUS-001)
- `CHK-SRC-PIG-003-007` (seventh chunk of source SRC-PIG-003)

Rules:
- Chunk IDs serve as the ChromaDB document ID. They must conform to ChromaDB document ID constraints (string, unique within collection)
- Chunk IDs are assigned when a chunk is first created during chunking. They are never changed after assignment
- Sequence numbers are assigned per source and never reused
- Chunks that are rejected, superseded, or removed retain their ID in the metadata store with `approval_state: not_approved` or `review_status: rejected`. They are not reassigned to new content

## 4.3 Benchmark IDs

**Format:** `BMK-{CATEGORY_CODE}-{NNN}`

Where:
- `{CATEGORY_CODE}` is the uppercase three-letter benchmark category code
- `{NNN}` is a zero-padded three-digit sequence number, starting at `001`

| Category | Code | Example |
|----------|------|---------|
| Pigments | `PIG` | `BMK-PIG-001` |
| Binders and Media | `BND` | `BMK-BND-001` |
| Conservation | `CON` | `BMK-CON-001` |
| Historical Practice | `HIS` | `BMK-HIS-001` |
| Color Theory | `COL` | `BMK-COL-001` |
| Product Comparison | `PRD` | `BMK-PRD-001` |
| Terminology | `TRM` | `BMK-TRM-001` |

Rules:
- Benchmark IDs are assigned when a benchmark record is first authored. They are never changed
- Sequence numbers are assigned per category and never reused
- Benchmark IDs are stored in `benchmarks/benchmark_gold_set_v1.json` and validated against `schemas/benchmark_template.json`

---

# 5. Data File Naming Conventions

## 5.1 Raw Files

**Directory:** `data/raw/`
**Format:** `{source_id}_{descriptive_slug}.{ext}`

Where:
- `{source_id}` is the full source ID (e.g. `SRC-MUS-001`)
- `{descriptive_slug}` is a short, lowercase, hyphen-separated label describing the file (e.g. `ngs-zinc-white-bulletin`)
- `{ext}` is the file extension matching the raw format (`pdf`, `html`, `txt`, `docx`, etc.)

Examples:
- `SRC-MUS-001_ngs-zinc-white-bulletin.pdf`
- `SRC-MFR-002_winsor-newton-oil-tds.html`
- `SRC-PIG-001_hilaire-mayer-pigments.pdf`

Rules:
- Raw filenames are set at intake and not changed
- The `source_id` prefix must match the source register entry for that file
- The descriptive slug is for human navigation only — it is not parsed programmatically
- Spaces are not permitted in filenames. Use hyphens

## 5.2 Clean/Normalized Files

**Directory:** `data/clean/`
**Format:** `{source_id}.txt`

Where:
- `{source_id}` is the full source ID

Examples:
- `SRC-MUS-001.txt`
- `SRC-PIG-003.txt`

Rules:
- One clean file per source
- The clean file contains the normalized, extraction-ready text of the source
- Filename is always `{source_id}.txt` — no slug, no suffix variants
- Tables extracted to separate files use `{source_id}_tables.txt` as a suffix variant

## 5.3 Source Metadata Files

**Directory:** `data/metadata/sources/`
**Format:** `{source_id}.json`

Examples:
- `SRC-MUS-001.json`
- `SRC-COL-002.json`

Rules:
- One metadata file per source
- Filename must match the `source_id` field inside the file
- File must conform to `schemas/source_register_schema.json`

## 5.4 Chunk Metadata Files

**Directory:** `data/metadata/chunks/`
**Format:** `{chunk_id}.json`

Examples:
- `CHK-SRC-MUS-001-001.json`
- `CHK-SRC-PIG-003-007.json`

Rules:
- One metadata file per chunk
- Filename must match the `chunk_id` field inside the file
- File must conform to `schemas/chunk_schema.json`
- Chunk metadata files are not required for chunks that live only in ChromaDB — they are required when using the metadata store for full-field storage

---

# 6. Schema File Naming Conventions

**Directory:** `schemas/`
**Format:** `{descriptive_name}_schema.json` for schemas; `{descriptive_name}_vocab.json` for vocabulary files

| File | Purpose |
|------|---------|
| `source_register_schema.json` | JSON Schema for source-level metadata records |
| `chunk_schema.json` | JSON Schema for chunk-level metadata records |
| `benchmark_template.json` | JSON Schema for benchmark records |
| `controlled_vocabulary.json` | Canonical enum values for all shared vocabulary |
| `provenance_record_schema.json` | JSON Schema for metadata provenance records |
| `conflict_record_schema.json` | JSON Schema for conflict log entries |
| `retrieval_failure_schema.json` | JSON Schema for retrieval failure log entries |
| `answer_label_vocab.json` | Canonical answer label values and definitions |

Rules:
- Schema filenames are fixed — they must match the filenames referenced in code imports and documentation
- No version suffixes in schema filenames in v1. Version is tracked inside the schema file as a `$schema` or `version` field
- Schema files must not be renamed without updating all references in `src/`, `scripts/`, and documentation

---

# 7. Log File Naming Conventions

**Directory:** `data/logs/`
**Format:** `{log_type}_log.{ext}` for ongoing logs; `{log_type}_log_{YYYY-MM-DD}.{ext}` for dated snapshots

| File | Purpose |
|------|---------|
| `retrieval_failure_log.csv` | Ongoing log of retrieval failures during evaluation |
| `conflict_log.csv` | Ongoing log of detected source conflicts |
| `deduplication_log.csv` | Ongoing log of deduplication decisions |
| `ingestion_log.csv` | Ongoing log of source intake events |
| `benchmark_results_log.csv` | Cumulative benchmark run results |

Rules:
- Ongoing log files use a flat name without date suffix — they are appended to, not replaced
- Dated snapshots are written when a full log is archived: e.g. `retrieval_failure_log_2025-03-09.csv`
- Log files must conform to the schema in `schemas/retrieval_failure_schema.json` and related schemas

---

# 8. Documentation File Naming Conventions

## 8.1 Foundation Docs

**Directory:** `docs/foundation/`
**Format:** `{descriptive_name}.md` (lowercase, underscore-separated)

| File | Purpose |
|------|---------|
| `FOUNDATION_PACK_v1.md` | Umbrella master document (uppercase by convention — this is a named master artifact) |
| `source_hierarchy.md` | Source trust tiers and role matrix |
| `metadata_schema.md` | Source and chunk metadata field definitions |
| `controlled_vocabulary.md` | Canonical enum values (human-readable reference) |
| `chunking_rules.md` | Semantic chunking principles and boundary rules |
| `benchmark_template.md` | Benchmark structure and scoring dimensions |
| `system_prompt_v1.md` | The v1 system prompt and behavioral rules |

## 8.2 Policy Docs

**Directory:** `docs/policies/`
**Format:** `{descriptive_name}.md` (lowercase, underscore-separated)

| File | Purpose |
|------|---------|
| `source_acquisition_policy.md` | Source intake rules and admission criteria |
| `metadata_provenance_rules.md` | Provenance types and tracking method |
| `deduplication_policy.md` | Duplicate detection and resolution rules |
| `conflict_resolution_policy.md` | Conflict types, resolution order, disclosure |
| `review_workflow.md` | Workflow stages, review gates, approval levels |
| `retrieval_policy_v1.md` | Hybrid retrieval pipeline rules |
| `answer_labeling_standard.md` | Answer label selection and application rules |
| `file_naming_policy.md` | This document |

Rules:
- Documentation files use lowercase with underscores — no camelCase, no hyphens
- Version suffixes (`_v1`) are used only for files that will have multiple versioned releases (e.g. `system_prompt_v1.md`, `retrieval_policy_v1.md`). Other docs are versioned via internal version fields, not filename
- Documentation files are never renamed after they are referenced in companion document lists

## 8.3 Plan and Design Docs

**Directory:** `docs/plans/`
**Format:** `{YYYY-MM-DD}-{descriptive-slug}-design.md`

Examples:
- `2026-03-09-senior-python-engineer-skill-design.md`
- `2026-03-09-chromadb-specialist-skill-design.md`

Rules:
- Date prefix is the date the design was authored
- Slug is lowercase, hyphen-separated
- Design docs are not renamed after creation — they serve as historical records

---

# 9. Source Code File Naming Conventions

**Directory:** `src/`
**Format:** `{module_name}.py` (lowercase, underscore-separated)

| Module | Purpose |
|--------|---------|
| `config.py` | All paths, constants, ChromaDB collection names |
| `models.py` | Pydantic models for SourceRecord, ChunkRecord, ProvenanceRecord |
| `storage/metadata_store.py` | Full-field metadata store (read/write) |
| `storage/chroma_store.py` | ChromaDB indexing and query interface |
| `ingestion/chunker.py` | Chunking logic |
| `ingestion/normalizer.py` | Text normalization |
| `retrieval/retriever.py` | Hybrid retrieval pipeline |
| `retrieval/reranker.py` | Reranking and diversity logic |
| `generation/generator.py` | Answer generation with citation assembly |
| `evaluation/benchmark_runner.py` | Benchmark execution and scoring |
| `evaluation/scorer.py` | Dimension-level scoring logic |
| `cli.py` | Command-line interface entry point |
| `api.py` | FastAPI application entry point |
| `logging_utils.py` | Structured logging setup |

Rules:
- Module names are lowercase with underscores — no camelCase, no hyphens
- Module names must match the import path used in other files
- If a module is renamed, all imports and references in `CLAUDE.md`, documentation, and other source files must be updated together

---

# 10. Script File Naming Conventions

**Directory:** `scripts/`
**Format:** `{verb}_{noun}.py` (lowercase, underscore-separated)

Examples:
- `scaffold.py` — creates project directory structure
- `ingest_source.py` — ingests a new source
- `rebuild_index.py` — rebuilds ChromaDB index
- `run_benchmarks.py` — runs the benchmark evaluation suite
- `export_metadata.py` — exports metadata store to JSON

Rules:
- Script names use verb-noun format where possible
- Scripts are not importable modules — they are executable entry points
- Script names must not shadow module names in `src/`

---

# 11. Prohibited Naming Patterns

The following patterns must not be used anywhere in the system:

| Pattern | Why prohibited |
|---------|---------------|
| `untitled_*.json` | Unnamed files cannot be programmatically associated with a source or chunk |
| `temp_*.json`, `tmp_*.json` | Temporary files must not enter the data directory structure |
| `chunk_1.json`, `chunk_2.json` | Non-prefixed sequence numbers are not globally unique |
| `source_data.json` | Generic names without source ID prefix are not locatable |
| Spaces in filenames | Spaces break shell commands, glob patterns, and path construction |
| Mixed case in data filenames | `SRC-MUS-001.json` and `src-mus-001.json` must not coexist |
| Reused sequence numbers | Once a sequence number is assigned (even if the record is later rejected), it must not be reused |

---

# 12. ID Assignment Procedure

When registering a new source, chunk, or benchmark, follow this procedure:

1. **Determine the family or category** — look up the appropriate code from §4
2. **Find the highest current sequence number** for that family in the source register, chunk metadata, or benchmark gold set
3. **Increment by one** — assign the next number in sequence
4. **Construct the ID** using the format in §4
5. **Record the ID in the register** (source register, chunk metadata file, or benchmark file) immediately — do not hold it in memory
6. **Do not reuse** — if the registration fails, the ID is consumed; discard it and use the next number next time

The source register at `data/source_register.json` is the authoritative list of all assigned source IDs. Chunk IDs are authoritative in `data/metadata/chunks/`. Benchmark IDs are authoritative in `benchmarks/benchmark_gold_set_v1.json`.

---

# 13. QA Questions

Before approving any new file or ID assignment:

1. Does the ID or filename follow the exact format defined in §4 or §5–§10?
2. Is the sequence number new — not reused from a previously assigned or rejected record?
3. Does the filename match the ID field inside the file?
4. Is the file in the correct directory for its type?
5. Are spaces absent from all filenames?
6. For source metadata files: does the `source_id` in the file match the filename?
7. For chunk metadata files: does the `chunk_id` in the file match the filename?
8. For schema files: does the filename match the reference used in all code that imports it?
9. Are all documentation files lowercase with underscores?
10. Is the file free of prohibited naming patterns from §11?

---

# 14. Recommended Companion Documents

1. `docs/foundation/metadata_schema.md` §8 — ID convention definitions that this policy operationalizes
2. `docs/foundation/controlled_vocabulary.md` §3.1 — source family codes referenced in §4.1
3. `docs/foundation/controlled_vocabulary.md` §3.21 — benchmark category codes referenced in §4.3
4. `docs/policies/review_workflow.md` — governs when IDs are assigned relative to review stages
5. `schemas/source_register_schema.json` — JSON Schema that validates source metadata files named per this policy
6. `schemas/chunk_schema.json` — JSON Schema that validates chunk metadata files named per this policy

---

# 15. Adoption Rule

This document is the canonical file naming policy for v1 of the Oil Painting Research Assistant.

All ingestion code, review tools, CLI scripts, schema validators, and documentation authors must follow the naming conventions defined here.

Any deviation from the ID formats in §4 constitutes a data integrity error and must be corrected before the affected records are indexed or approved.

Any change to naming conventions requires a version increment to this document, an audit of existing files for compliance, and updates to all code that constructs or validates filenames.

---
