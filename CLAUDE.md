# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A domain-specific RAG (Retrieval-Augmented Generation) system for oil painting research, covering pigment chemistry, historical practices, conservation, and manufacturer data. Built with local-first ChromaDB vector storage and hybrid retrieval.

## Commands

```bash
# Install (editable)
pip install -e .
# or: pip install hatch && hatch shell

# Environment setup
cp .env.example .env  # then populate any required values

# Run CLI
python -m oil_painting_rag.cli  # stub — no-op until cli.py is implemented

# Run API server
python -m oil_painting_rag.api  # stub — no-op until api.py is implemented

# Run tests (no tests exist yet — add to tests/ as modules are implemented)
pytest tests/ -v

# Run benchmarks
python -m oil_painting_rag.evaluation.benchmark_runner
```

## Architecture

The system follows a layered pipeline: **Ingest → Chunk → Index → Retrieve → Generate**

```
src/oil_painting_rag/
├── models/          # Pydantic v2 data models (source, chunk, provenance, retrieval, benchmark)
├── ingestion/       # Source loading, registration, capture
├── chunking/        # Text and table chunking with validation
├── indexing/        # ChromaDB vector index + BM25 lexical index + embeddings
├── retrieval/       # Hybrid retriever (vector+lexical fusion), reranker, filters, citation assembler
├── generation/      # Answer generation, prompt builder, query mode router
├── storage/         # Metadata store, filesystem store, source register
├── evaluation/      # Benchmark runner, scorer, failure logger
├── policies/        # Governance: source, provenance, retrieval, conflict resolution
├── utils/           # Citation, text, hash, enum helpers
├── api.py           # REST API entry point
├── cli.py           # CLI entry point
└── config.py        # Configuration/settings
```

**Key design principles:**
- **Provenance-aware:** All metadata tracks lineage from source to answer
- **Source hierarchy:** Sources are tiered by trust level (see `docs/foundation/source_hierarchy.md`)
- **Review-state aware:** Chunks and sources have approval states tracked in `data/register/`
- **Hybrid retrieval:** Semantic (ChromaDB) + lexical (BM25) search fused in `retrieval/hybrid_retriever.py`
- **Policy-driven:** Business rules enforced via `policies/` modules, not ad-hoc

## Data Layout

```
data/
├── raw/             # Ingested source documents by domain (pigments/, historical/, etc.)
├── clean/           # Normalized markdown + metadata + tables
├── chunks/          # Split chunks: text/, tables/, metadata/
├── indexes/         # Persisted ChromaDB (chroma/) and BM25 (lexical/) indexes + cache/
├── register/        # Audit CSVs: acquisition_log, chunk_review_log, conflict_review_log
└── logs/            # retrieval_failure_log.csv
```

## Domain Vocabulary & Schemas

- `vocab/` — controlled vocabulary JSON, material/product alias maps, material ontology
- `schemas/` — JSON schemas for all core data types (source register, chunks, provenance, conflicts, etc.)
- `docs/foundation/` — authoritative specs for chunking rules, metadata schema, source hierarchy, system prompt
- `docs/policies/` — governance policies for acquisition, deduplication, conflict resolution, review workflow

## Python Engineering Standards

Before writing, extending, or reviewing any Python in this project, invoke the `oil-rag-senior-python` skill. It covers pre-implementation architecture thinking, coding standards (type hints, Pydantic v2, Pathlib, logging, config), RAG pipeline integrity (mandatory hybrid retrieval, ChromaDB rules, provenance tracking), and a self-review checklist.

For any ChromaDB-specific work (collections, upsert, queries, metadata design, filter syntax, debugging, index maintenance), also invoke `oil-rag-chromadb`. Target version: 0.6.x.

Before writing or reviewing any documentation — foundation docs, policy docs, README, docstrings, or API docs — invoke `oil-rag-technical-writer`. It enforces formal doc structure, developer doc standards, cross-policy governance integrity, and research-systems architecture correctness.

## Build Workflow & Skills

The project is built in 4 strict sequential phases using Claude Code skills. Invoke the relevant skill before starting any phase.

| Phase | Skill | What it produces |
|-------|-------|-----------------|
| Overview / orientation | `oil-rag-build-workflow` | Phase sequence, gate checks, iron rules |
| 2.1 — Foundation Docs | `oil-rag-foundation-docs` | 7 docs in `docs/foundation/` |
| 2.2 — Policy Docs | `oil-rag-policy-docs` | 8 docs in `docs/policies/` |
| 3 — Schemas | `oil-rag-schemas` | 12 schemas + 4 vocab + 2 benchmark files |
| 4 — Code | `oil-rag-code` | Full Python codebase in `src/oil_painting_rag/` |

**Phase 1 (folder scaffold) is complete** — `scripts/scaffold.py` has already been run.

`prompts/` contains the full specification prompts (298–748 lines each) that the skills reference. Skills tell you which prompt files to read and in what order.

## Current State

Most Python modules are scaffolded stubs. Schema JSON files contain empty `{"type": "object", "properties": {}}` placeholders. Documentation files are marked as "Canonical draft placeholders."

**Implement incrementally:** models → ingestion → indexing → retrieval → generation

**When implementing `config.py`:** wire ChromaDB persistence path (`data/indexes/chroma/`) and embeddings model here — all other modules should import from config rather than hardcoding paths.
