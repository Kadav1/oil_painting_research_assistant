# Oil Painting Research Assistant

**Provenance-Aware RAG System for Oil Painting Research**

A production-grade, domain-specific Retrieval-Augmented Generation (RAG) system built to answer research questions about oil painting — spanning pigment chemistry, historical studio practices, conservation science, manufacturer product data, and color theory. The system enforces source trust hierarchies, tracks full metadata provenance, detects and discloses source conflicts, and grounds every answer in cited, retrievable evidence.

---

## Project at a Glance

| Metric | Value |
|--------|-------|
| Language | Python 3.11+ |
| Source files | 56 modules across 10 packages |
| Source lines | ~9,200 (excl. tests) |
| Test lines | ~1,240 |
| Test count | 91 passing |
| Schemas | 12 JSON schemas |
| Vocabulary files | 4 controlled vocabulary JSONs |
| Foundation docs | 7 specification documents |
| Policy docs | 8 governance policies |
| Data models | 20+ Pydantic v2 models |
| CLI commands | 11 |
| API endpoints | 6 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Vector database | ChromaDB (persistent, 3-collection approval-state architecture) |
| Lexical index | BM25 via rank-bm25 (serialized to disk) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (offline-capable) |
| Data models | Pydantic v2 with strict validation, JSON schema grounding |
| LLM backend | OpenAI-compatible API via LM Studio — Qwen 3.5 9B, IBM Granite 3.2 8B (swappable; gpt-4o fallback) |
| LLM inference server | LM Studio (local, OpenAI-compatible endpoint) |
| CLI | Typer + Rich console |
| API | FastAPI + Uvicorn |
| PDF processing | pypdf for metadata extraction |
| Data wrangling | pandas (source register, audit logs) |
| Build system | Hatchling (PEP 517) |
| Testing | pytest |

---

## Architecture

The system implements a strict 5-stage pipeline with governance enforced at every boundary:

```
Ingest ──▶ Chunk ──▶ Index ──▶ Retrieve ──▶ Generate
```

### Stage 1: Ingestion

Files are dropped into typed inbox subdirectories (`pdf/`, `html/`, `markdown/`, `text/`, `other/`). The intake pipeline handles classification, metadata assignment, registration, and archival.

**Key components:**

- **IntakeClassifier** — Keyword-based metadata inference engine. Scans filename + content preview against patterns defined in `intake_patterns.json`. Infers three fields:
  - `source_family` — museum_conservation, scientific_paper, manufacturer, art_historical_text, color_reference, pigment_reference (with confidence: high/medium/low based on keyword hit count)
  - `domain` — pigment, binder, conservation, historical_practice, color_theory, product, technique (tie-breaking to "mixed")
  - `capture_method` — derived from inbox subdirectory (pdf_download, html_scrape, manual_entry, etc.)

- **PDF Metadata Reader** — Extracts `/Title`, `/Author`, `/Creator` from PDF info dictionaries via pypdf. Silent failure on corrupted or non-PDF files — returns `None` for missing fields.

- **Auto-Mode Processing** (`--auto` flag) — Zero-prompt file intake for non-interactive environments. Resolution chain:
  1. PDF metadata title → filename-derived title (strip extension, hyphens/underscores to spaces, title-case)
  2. PDF creator → `"unknown"` fallback for institution
  3. First source_type from family mapping → `"web_article"` fallback
  4. Fixed defaults: `access_type = "open_access"`, `publication_year = None`

- **Source ID Generation** — Auto-increments within family: `SRC-{FAMILY_CODE}-{NNN}` (e.g., `SRC-MUS-001`, `SRC-PIG-012`, `SRC-UNK-001`). Family codes loaded from controlled vocabulary with synthetic `UNK` for unclassifiable sources.

- **SourceCapture** — Registration orchestrator. Validates source_id format, builds a full `SourceRecord` (40+ fields), persists to register store, saves raw file to filesystem store, infers default trust tier from source family.

- **SourceRegistry** — Query facade over the register store. Supports filtering by family, trust tier, review state, domain. Provides DataFrame export for bulk analysis.

- **Rollback on failure** — If registration fails after file move, the file is moved back to its original location and the empty destination directory is cleaned up.

### Stage 2: Chunking

Two complementary chunkers split normalized text into retrievable units:

- **ProseChunker** — Splits by Markdown heading boundaries, then creates sliding sentence windows within each section. Respects token budget (max 400, min 40 tokens per chunk, 1 sentence overlap). Detects chunk type (prose, glossary, mixed). Builds hierarchical `section_path` from heading structure (e.g., `"3.2.pigment_handling"`).

- **TableChunker** — Detects Markdown table blocks via regex pattern matching (`|...|` rows with separator detection). Each table becomes one table-type `ChunkRecord` preserving full structure. Parses column headers for descriptive chunk titles. Flags messy tables (inconsistent column counts) with quality flags.

- **Chunk Validation** — Post-chunking validator checks for empty text, missing source IDs, invalid token estimates. Returns filtered valid list + issue report.

Every `ChunkRecord` inherits 15+ metadata fields from its parent `SourceRecord`: domain, subdomain, materials_mentioned, pigment_codes, binder_types, historical_period, artist_or_school, question_types_supported, claim_types_present, trust_tier, source_family, source_type, citation_format, and more.

### Stage 3: Indexing

Dual-index architecture ensures both semantic and keyword retrieval:

- **ChromaDB Vector Index** — 3 approval-state collections (`chunks_live`, `chunks_retrieval`, `chunks_draft`) gate which chunks are retrievable based on review state. Metadata stored as pipe-encoded strings for list fields. Embeddings via `all-MiniLM-L6-v2` with offline-first loading strategy.

- **BM25 Lexical Index** — Full-text keyword index built with rank-bm25. Supports incremental add/remove. Persisted as pickle files to disk. Indexes all non-rejected chunks regardless of approval state.

- **IndexManager** — Unified interface over both indexes. Handles upsert (validates + indexes into both), delete (by chunk or by source), rebuild (wipe + reload from disk), and status reporting.

### Stage 4: Retrieval

The mandatory hybrid retrieval pipeline runs 9 steps to produce a governance-compliant context package:

1. **Query Classification** — Deterministic keyword matching infers answer modes (Studio, Conservation, Art History, Color Analysis, Product Comparison), domains, and question types.

2. **Filter Construction** — Builds ChromaDB `where`-clause from approval state gate + inferred domain. Only narrows by domain when classification is specific enough.

3. **Vector Search** — ChromaDB cosine similarity search (20 candidates default).

4. **Lexical Search** — BM25 keyword search (20 candidates default).

5. **Reciprocal Rank Fusion (RRF)** — Merges vector + lexical candidates with fusion constant K=60. Every candidate tagged with its source(s) ("vector", "lexical", or both).

6. **Metadata Completion** — Loads full `ChunkRecord` for each merged candidate from filesystem store.

7. **Multi-Factor Reranking** — Scores each candidate across 11 weighted factors:

   | Factor | Weight | Description |
   |--------|--------|-------------|
   | Semantic relevance | 0.35 | Inverted cosine distance from vector search |
   | Lexical relevance | 0.20 | BM25 score from keyword search |
   | Trust tier | 0.15 | Source hierarchy (tier 1 = most trusted) |
   | Review state | 0.10 | Approved > reviewed > draft > pending |
   | Domain fit | 0.08 | Chunk domain matches query domain |
   | Question type fit | 0.05 | Chunk supports inferred question types |
   | Case specificity | 0.03 | Penalizes case-specific for general queries |
   | Quality flags | 0.02 | Penalties for OCR suspect, citation unclear, etc. |
   | Citability | 0.01 | Directly citable > paraphrase only > internal use |
   | Retrieval weight hint | 0.01 | Manual 0-5 boost per chunk |
   | Duplicate status | implicit | -0.50 for confirmed duplicates or superseded |

8. **Diversity & Deduplication Filtering** — Greedy selection subject to: max 3 chunks per source, duplicate cluster suppression (canonical member preferred), token budget enforcement (3000 tokens default), final approval state gate check.

9. **Context Assembly** — Builds `ContextPackage` containing selected chunks, excluded candidates (with reasons), duplicate suppression notes, conflict notes for disclosure, citation strings, filter audit trail, token budget accounting, and retrieval warnings.

### Stage 5: Generation

- **Mode Router** — Selects answer mode from classification with priority ordering: Conservation > Art History > Product Comparison > Color Analysis > Studio. Appends mode-specific emphasis notes to system prompt.

- **Prompt Builder** — Constructs system prompt from canonical `system_prompt_v1.md` + mode addendum. User prompt includes the query, formatted chunk contexts with trust tier annotations, and active conflict disclosures.

- **Answerer** — Calls LLM backend (OpenAI-compatible or EchoBackend for testing). Parses response into structured `AnswerResult` with: answer text, answer mode, citations, conflict disclosures, and uncertainty notes.

- **Swappable LLM Backends:**
  - `OpenAIBackend` — Production (temperature 0.2, configurable base_url). Targets LM Studio serving local models: Qwen 3.5 9B and IBM Granite 3.2 8B. Falls back to OpenAI gpt-4o when API key is set.
  - `EchoBackend` — Testing (returns user prompt verbatim, no API key needed)

---

## Governance & Policy Layer

The system enforces 8 formal governance policies:

| Policy | Scope |
|--------|-------|
| **Source Acquisition** | Rules for what sources are ingested, trust tier assignment criteria, access type classification |
| **Metadata Provenance** | Per-field provenance tracking (who set it, how, confidence level, override history) |
| **Deduplication** | Duplicate cluster management, canonical member selection, suppression in retrieval |
| **Conflict Resolution** | When sources disagree, records the conflict, tracks resolution status, mandates disclosure in answers |
| **Review Workflow** | Approval state machine: draft → pending → under_review → reviewed → approved/rejected. Gates retrieval access. |
| **Retrieval Policy** | Mandatory hybrid search, RRF fusion, multi-factor reranking, diversity enforcement, token budget |
| **Answer Labeling** | Structured labels on answers: mode, quality flags, confidence levels |
| **File Naming** | Standardized naming: `SRC-FAM-NNN_sanitized_title.ext` with collision suffixes |

---

## Data Models

20+ Pydantic v2 models with `extra = "forbid"` validation. Key models:

- **SourceRecord** (40+ fields) — Complete source document metadata: identity, classification, access, storage, trust scoring (5 sub-scores), 10 pipeline status flags, scope/quality, deduplication state, governance notes
- **ChunkRecord** (30+ fields) — Retrievable text unit: content, classification (inherited from source), scope/quality, review state, deduplication, propagated source metadata
- **ContextPackage** — Assembled retrieval output: selected chunks, excluded candidates with reasons, conflict notes, duplicate suppression notes, token accounting, trace data
- **RetrievalTrace** — Full audit trail of the 9-step retrieval pipeline: all candidates at each stage with scores
- **FieldProvenance** — Per-field provenance: entity, field, value, method, confidence, override history
- **ConflictRecord** — Source disagreement tracking: topic, involved entities, resolution status, disclosure requirement
- **BenchmarkRunResult** — Evaluation result: automated scoring + human dimension scores (1-5 scale, 8 failure categories)

---

## Controlled Vocabulary & Schemas

**4 vocabulary files** enforce consistency across the entire system:

- `controlled_vocabulary.json` — Canonical values for: source_family (6 + family_codes), source_type (15 types), domain (7), access_type (4), question_type (8), approval_state (5), review_status (7), duplicate_status (4), answer_mode (5)
- `material_alias_map.json` — Maps informal material names to canonical forms (e.g., "flake white" → "lead_white")
- `product_alias_map.json` — Maps product names to canonical forms (e.g., "Winsor & Newton" → "winsor_newton")
- `material_ontology_v1.json` — Hierarchical material classification: pigment families, binder types, mediums, substrates

**12 JSON schemas** validate all data types: source register, chunks, context packages, retrieval traces, field provenance, duplicate clusters, conflict records, review records, approval states, benchmark templates, answer labels, restriction flags.

---

## Evaluation & Benchmarking

- **BenchmarkRunner** — Executes gold set queries through the full pipeline. For each query: retrieves, generates, auto-scores, logs failures. Supports `--max N` for partial runs.

- **Scorer** — Automated pre-scoring with 8 failure categories:
  - `FABRICATED_CITATION` — Citation not grounded in retrieved chunks
  - `UNCERTAINTY_COLLAPSED` — Failed to preserve uncertainty from sources
  - `SCOPE_MISMATCH` — Answer scope doesn't match query specificity
  - `PRODUCT_UNIVERSALIZED` — Product-specific claim generalized
  - `CASE_GENERALIZED` — Case study finding stated as universal
  - `CONFLICT_UNDISCLOSED` — Active conflict not disclosed in answer
  - `HISTORICAL_ANACHRONISM` — Anachronistic claim
  - `MUST_NOT_SAY_VIOLATION` — Answer contains explicitly prohibited content

- **FailureLogger** — Persists failures to `retrieval_failure_log.csv` for post-hoc analysis.

- **Human Scoring Dimensions** — 8 dimensions scored 1-5 after automated pre-screening: accuracy, completeness, source grounding, conflict handling, uncertainty preservation, practical value, readability, citation quality.

---

## CLI Interface

11 commands via Typer + Rich:

```
oil-rag ask "What pigments did Vermeer use?"    # Full RAG pipeline query
oil-rag intake --auto                            # Auto-ingest inbox files
oil-rag intake --file paper.pdf --auto           # Ingest single file
oil-rag chunk                                    # Chunk all ingested sources
oil-rag chunk SRC-MUS-001                        # Chunk specific source
oil-rag index                                    # Index all chunks
oil-rag index --rebuild                          # Rebuild indexes from files
oil-rag status                                   # Index health + source count
oil-rag review                                   # Sources pending review
oil-rag sources --domain pigment --tier 1        # Filter registered sources
oil-rag conflicts                                # Active source conflicts
oil-rag benchmark --max 10                       # Run evaluation subset
oil-rag vocab                                    # Controlled vocabulary summary
```

---

## REST API

6 endpoints via FastAPI (default: `127.0.0.1:8765`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Full RAG query with structured response |
| GET | `/status` | ChromaDB counts, BM25 size, source count |
| GET | `/sources` | List/filter registered sources |
| GET | `/conflicts` | List active conflict records |
| POST | `/benchmark/run` | Execute benchmark gold set |
| GET | `/benchmark/{filename}` | Retrieve benchmark results |

---

## Storage Architecture

All storage is local-first with no external database dependencies:

```
data/
├── inbox/{pdf,html,markdown,text,other}/   Drop zone for new sources
├── raw/{source_id}/                        Archived originals
├── clean/{source_id}/                      Normalized markdown + metadata JSON
├── chunks/
│   ├── text/                               Chunk text files (.txt)
│   ├── tables/                             Extracted table JSONs
│   └── metadata/                           Chunk metadata JSONs
├── indexes/
│   ├── chroma/                             Persistent ChromaDB (3 collections)
│   ├── lexical/                            BM25 pickles (index + corpus)
│   └── cache/                              Embedding cache
├── register/                               Source register JSONs + audit CSVs
├── logs/                                   Retrieval failure logs
└── benchmark_runs/                         Timestamped benchmark results
```

**FilesystemStore** provides unified read/write access: raw files, clean text, chunk text + metadata, source metadata sidecars, table data, generic JSON helpers. **RegisterStore** manages source register persistence (one JSON per source + pandas DataFrame export). **MetadataStore** handles provenance records, conflict records, and review audit trail.

---

## Testing

91 tests across 6 test modules:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_chunking` | 9 | Prose chunking, table detection, chunk validation |
| `test_intake` | 26 | Classifier inference, sanitization, source ID generation, auto-mode, filename derivation, UNK family code |
| `test_models` | 10 | Pydantic model creation, ChromaDB round-trip, scoring logic |
| `test_pdf_metadata` | 5 | PDF extraction, missing/corrupt/non-PDF handling |
| `test_retrieval` | 23 | Query classification, reranking, diversity filtering, citation assembly, scoring, mode routing, prompt building |
| `test_utils` | 18 | Hash generation, text processing, pipe encoding, citation formatting, enum validation |

Auto-mode tests use mocked `cfg.RAW_DIR`, `shutil`, and `extract_pdf_metadata` to avoid filesystem side effects.

---

## Key Design Decisions

1. **Mandatory hybrid retrieval** — Vector-only search is architecturally prohibited. Every query runs through both semantic and lexical indexes, merged via RRF. This prevents the silent failure mode where embedding similarity misses keyword-critical domain terms.

2. **Approval-state gated collections** — Three ChromaDB collections gate access by review state. Draft chunks are only searchable in testing. Production retrieval only sees approved content. This prevents unreviewed or low-quality content from reaching users.

3. **Multi-factor reranking over raw similarity** — Raw cosine similarity is only 35% of the final score. Trust tier, review state, domain fit, and 7 other factors ensure that a tier-1 museum conservation bulletin outranks a tier-5 blog post even if the blog post has a slightly higher embedding similarity.

4. **Conflict disclosure as a first-class concern** — When retrieved chunks come from sources that disagree (tracked via `ConflictRecord`), the system mandates disclosure in the generated answer. The scorer flags `CONFLICT_UNDISCLOSED` as an automatic failure.

5. **Provenance tracking at field granularity** — Every metadata field can carry its own provenance record: who set it, by what method, at what confidence, whether it was overridden and from what original value.

6. **Local-first, offline-capable** — ChromaDB persistent storage, pickled BM25, offline-first embedding model loading. The system runs fully offline after initial model download. No cloud dependency for retrieval.

7. **Policy-driven governance** — Business rules live in 8 formal policy documents, not scattered across code. Policies are cross-referenced by the codebase (e.g., retrieval_policy_v1.md defines the reranking weights used in `reranker.py`).

---

## Project Structure

```
oil_painting_research_assistant/
├── src/oil_painting_rag/          # 56 Python modules, ~9,200 lines
│   ├── models/                    #   5 Pydantic v2 model modules
│   ├── ingestion/                 #   7 modules (loader, capture, registry, classifier, runner, PDF reader)
│   ├── chunking/                  #   4 modules (prose chunker, table chunker, validators)
│   ├── indexing/                  #   4 modules (index manager, ChromaDB, BM25, embeddings)
│   ├── retrieval/                 #   6 modules (hybrid retriever, classifier, reranker, diversity, filters, citations)
│   ├── generation/                #   4 modules (answerer, mode router, prompt builder, backends)
│   ├── storage/                   #   3 modules (filesystem, register, metadata stores)
│   ├── evaluation/                #   3 modules (benchmark runner, scorer, failure logger)
│   ├── policies/                  #   4 modules (source, provenance, retrieval, conflict policies)
│   ├── utils/                     #   4 modules (citation, text, hash, enum utilities)
│   ├── cli.py                     #   11-command Typer CLI
│   ├── api.py                     #   6-endpoint FastAPI server
│   ├── config.py                  #   Centralized configuration
│   └── logging_utils.py           #   Structured logging setup
├── tests/                         #   6 test modules, 91 tests, ~1,240 lines
├── schemas/                       #   12 JSON schemas
├── vocab/                         #   4 controlled vocabulary files
├── benchmarks/                    #   Gold set for evaluation
├── docs/
│   ├── foundation/                #   7 specification documents
│   └── policies/                  #   8 governance policies
├── scripts/                       #   Scaffold + intake scripts
└── pyproject.toml                 #   Hatchling build config
```
