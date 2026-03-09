# ChromaDB Specialist Skill — Design

**Date:** 2026-03-09
**Scope:** Oil Painting Research Assistant project
**Skill name:** `oil-rag-chromadb`
**Target version:** ChromaDB 0.6.x

## Purpose

Combined reference + discipline skill for all ChromaDB work in this project. Covers API patterns, metadata schema design, filter syntax, and debugging/maintenance. Complements `oil-rag-senior-python` which enforces high-level rules; this skill goes deep on ChromaDB specifics.

---

## Section 1 — API Reference
Correct patterns: PersistentClient setup, collection management, upsert, query, delete, inspect.

## Section 2 — Metadata Schema Design
Encoding strategies for ChromaDB's flat metadata model (str/int/float/bool only — no lists, no nesting). Field selection, list encoding, approval state encoding, field name alignment with schemas/.

## Section 3 — Filter Syntax Reference
Where clause operators, correct nesting of $and/$or, approval-state filter pattern, domain/source-tier patterns.

## Section 4 — Debugging & Maintenance
Diagnosing empty results, inspecting collection state, rebuilding indexes, detecting schema drift.

## Discipline Layer
Red flags and mandatory checks woven throughout: approval state filter always present, chunk_id always as document ID, metadata keys always match schemas/, lists always encoded, separate collections for live vs draft.
