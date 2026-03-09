# Senior Python Engineer Skill — Design

**Date:** 2026-03-09
**Scope:** Oil Painting Research Assistant project
**Skill name:** `oil-rag-senior-python`

## Purpose

A three-phase workflow skill that governs Claude's Python work in this project from first thought to finished code. Covers coding discipline, architecture judgment, RAG system design, and code review.

## Trigger

Invoke before writing any Python code, when designing a new module, or when reviewing existing code.

---

## Phase 1 — Pre-Implementation

Before writing any Python, Claude must answer:
- What is this module's single responsibility?
- Which existing layer does this belong to?
- What are the dependencies — is this adding coupling?
- What are the failure modes and edge cases?

---

## Phase 2 — Coding Standards

### Python
- Type hints on all public functions and methods
- Pydantic v2 models for all data structures (not raw dicts)
- Pathlib for all file paths (no `os.path`)
- Structured logging via `logging_utils.py` (no `print`)
- No bare `except:` — always catch specific exceptions
- No hardcoded paths, magic strings, or magic numbers — wire through `config.py`
- Short, focused functions — if it needs a comment to explain what, split it

### RAG / Retrieval
- Full hybrid pipeline mandatory: `classify → filter → vector search → lexical search → merge → rerank → diversity → citation assembly`
- ChromaDB: always `PersistentClient`, always `chunk_id` as document ID, persist under `data/indexes/chroma/`
- Review state gates every result: only `retrieval_allowed` or `live_allowed` chunks served
- Provenance flows through end-to-end: never flatten into a trust score
- All field names and enum values match `schemas/` and `vocab/controlled_vocabulary.json` exactly

---

## Phase 3 — Self-Review Checklist

| Category | Checks |
|----------|--------|
| Correctness | Edge cases handled? Error paths covered? Returns what it promises? |
| Security | File path traversal? Input validation at boundaries? |
| Quality | Duplication? Naming self-explanatory? Complexity reasonable? |
| Architecture | Right layer? Right module? Coupling appropriate? |
| Testability | Unit-testable without mocking 5 things? |
| RAG pipeline | All stages present? No vector-only shortcuts? |
| Data quality | Chunks metadata-complete? Required fields populated? |
| Provenance | Tracked end-to-end? Not collapsed into a flat field? |
| Citations | Grounded in actual retrieved chunks? Nothing fabricated? |
| Approval gating | Review state enforced before serving results? |
