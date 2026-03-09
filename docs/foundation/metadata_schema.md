# Metadata Schema v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-FND-002
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Source-level and chunk-level metadata field definitions, field types, required status, groupings, ID conventions, and operational notes
**Applies to:** Ingestion, chunking, indexing, retrieval, review, conflict resolution, citation assembly, and answer generation in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This document defines the canonical metadata schema for the Oil Painting Research Assistant.

It specifies:

* what metadata fields exist at the source level and the chunk level
* what each field means
* what type each field accepts
* whether each field is required or optional
* how fields are grouped by function
* what ID conventions apply
* how metadata is intended to be used operationally

This is a **conceptual schema foundation document**, not a JSON schema file.
It is the authoritative human-readable reference from which JSON schemas, Pydantic models, and code are derived.

---

# 2. Core Principle

Every retrievable unit in this system — whether a source or a chunk — must carry enough metadata to support:

* source-aware retrieval and reranking
* provenance tracking from source to answer
* review-state gating before retrieval
* citation construction
* conflict detection
* scope preservation (case-specific, product-specific, historical)

Metadata is not decorative. It is structural.

A chunk without complete metadata is not ready for indexing.
A source without complete metadata is not ready for chunking.

---

# 3. Objectives

1. Define a fixed, canonical set of fields for source-level and chunk-level records in v1
2. Ensure every field has a clear, unambiguous meaning
3. Ensure fields align with the source hierarchy, controlled vocabulary, and chunking rules
4. Ensure fields are compatible with ChromaDB metadata filtering
5. Provide the authoritative baseline from which JSON schemas and Pydantic models are generated

---

# 4. Definitions

**Source record:** One metadata record per ingested document or data source. Describes the document as a whole.

**Chunk record:** One metadata record per retrievable chunk. Describes a unit of text extracted from a source.

**Required field:** Must be populated before the record can be considered complete. Missing required fields block advancement in the review workflow.

**Optional field:** May be populated when data is available. Absence does not block workflow, but absence should be noted.

**Enum field:** Accepts only values from the controlled vocabulary (see `docs/foundation/controlled_vocabulary.md`). No free-text substitutions permitted.

**List field:** Accepts one or more values. May be an empty list but should be populated when applicable.

**Provenance tracking:** How a metadata field value was determined — extracted automatically, inferred by rule, suggested by a model, or entered manually. Provenance is tracked per-field in a separate record. See `docs/policies/metadata_provenance_rules.md`.

---

# 5. Schema Structure

| Layer | Record type | Granularity |
|-------|-------------|-------------|
| Source-level | `SourceRecord` | One per ingested document |
| Chunk-level | `ChunkRecord` | One per retrievable chunk |

These layers are linked by `source_id`. Every chunk carries the `source_id` of its parent source.

---

# 6. Source-Level Metadata Fields

## 6.1 Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_id` | string | yes | Unique internal source ID. Format: `SRC-{FAMILY_CODE}-{NNN}`. Stable — never changed after assignment. |
| `title` | string | yes | Full title of the source document |
| `short_title` | string | yes | Short, scan-friendly reference label used in citations |
| `source_family` | enum | yes | Broad source class. See controlled vocabulary §3.1. |
| `source_type` | enum | yes | More specific source type within family. See controlled vocabulary §3.2. |
| `institution_or_publisher` | string | yes | Organization or publisher responsible for the source |
| `author` | string or null | yes | Author name(s) if known; otherwise the organization name |
| `publication_year` | string or int or null | yes | Year of publication, or `"unknown"` |
| `edition_or_version` | string or null | no | Edition, version number, or snapshot label if applicable |

## 6.2 Access and Capture Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_url` | string or null | yes | Original URL if applicable; null if not a web source |
| `access_type` | enum | yes | How the source was accessed. See controlled vocabulary §3.7. |
| `raw_file_name` | string | yes | Filename of the saved raw file |
| `raw_file_path` | string | yes | Path to the raw file within `data/raw/` |
| `capture_date` | string | yes | ISO 8601 date the source was captured (e.g. `"2025-03-09"`) |
| `capture_method` | enum | yes | Method used to capture the source. See controlled vocabulary §3.8. |

## 6.3 Trust and Scoring Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trust_tier` | int or null | yes | Trust tier 1–5. Null until assigned by reviewer. See `docs/foundation/source_hierarchy.md`. |
| `authority_score` | int or null | yes | 0–5 score: source authority and rigor |
| `extractability_score` | int or null | yes | 0–5 score: how well content can be extracted and chunked |
| `coverage_value_score` | int or null | yes | 0–5 score: breadth and depth of domain coverage |
| `density_score` | int or null | yes | 0–5 score: information density |
| `priority_score` | int or null | yes | Derived composite score from the above four; used for ingestion prioritization |

All scores are null until assigned during review.

## 6.4 Domain and Content Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | enum | yes | Primary domain of the source. See controlled vocabulary §3.3. |
| `subdomain` | string or null | yes | More specific area within the domain. Free text. |
| `materials_mentioned` | list[string] | yes | Canonical material names mentioned in the source |
| `pigment_codes` | list[string] | yes | Pigment codes present (e.g. `PW1`, `PB29`). Empty list if none. |
| `binder_types` | list[string] | yes | Canonical binder/medium terms present. See controlled vocabulary §3.12. |
| `historical_period` | enum or string | yes | Historical period scope. See controlled vocabulary §3.15. |
| `artist_or_school` | list[string] | yes | Artists or schools referenced. See controlled vocabulary §3.16. Empty list if not applicable. |
| `question_types_supported` | list[enum] | yes | Question classes this source helps answer. See controlled vocabulary §3.4. |

## 6.5 Processing Status Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `raw_captured` | bool | yes | Whether the raw file has been saved to `data/raw/` |
| `normalized_text_created` | bool | yes | Whether a clean normalized text version exists in `data/clean/` |
| `tables_extracted` | enum | yes | Table extraction status. See controlled vocabulary §3.9. |
| `metadata_attached` | bool | yes | Whether the source metadata record file exists |
| `qa_reviewed` | bool | yes | Whether a human QA review has been performed |
| `chunked` | bool | yes | Whether the source has been chunked |
| `indexed` | bool | yes | Whether the source's chunks have been indexed into the retrieval stores |
| `ready_for_use` | bool | yes | Whether the source is approved for live retrieval |

## 6.6 Evidence Characterization Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_study_vs_general` | enum | yes | Whether the source is primarily a case study or general reference. See controlled vocabulary §3.6. |
| `claim_types_present` | list[enum] | yes | Types of claims present in the source. See controlled vocabulary §3.5. |
| `confidence_level` | enum | yes | Reviewer confidence in metadata completeness and accuracy. See controlled vocabulary §3.10. |

## 6.7 Annotation Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `limitations_notes` | string | yes | Known limitations, scope boundaries, or weaknesses |
| `license_or_usage_notes` | string | yes | Usage constraints: internal summary only, full quotation permitted, etc. |
| `citation_format` | string | yes | Preferred short citation text for use in answers |
| `summary` | string | yes | 2–4 sentence functional summary: what the source covers and when to use it |
| `retrieval_notes` | string | yes | Guidance for when and how to use this source in retrieval |
| `internal_notes` | string or null | no | Project-specific operational notes not intended for citation |

---

# 7. Chunk-Level Metadata Fields

## 7.1 Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chunk_id` | string | yes | Unique chunk ID. Format: `CHK-{source_id}-{NNN}`. Used as the ChromaDB document ID. Never regenerated after initial assignment. |
| `source_id` | string | yes | Parent source ID. Must match an existing source register record. |
| `chunk_index` | int | yes | Sequential position of this chunk within its source (0-based) |
| `chunk_title` | string | yes | Short semantic label describing the content of this chunk |
| `section_path` | string | yes | Dot-separated section hierarchy path (e.g. `3.2.pigment_handling`) |
| `page_range` | string or null | no | Page range if applicable (e.g. `"12-13"`) |

## 7.2 Content Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | Full text content of this chunk as indexed |
| `token_estimate` | int | yes | Approximate token count |
| `chunk_type` | enum | yes | Structural type. See controlled vocabulary §3.11. |

## 7.3 Domain and Content Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | enum | yes | Primary domain. See controlled vocabulary §3.3. |
| `subdomain` | string or null | yes | Specific area within the domain. May differ from source subdomain. |
| `materials_mentioned` | list[string] | yes | Canonical material names in this chunk |
| `pigment_codes` | list[string] | yes | Pigment codes in this chunk. Empty list if none. |
| `binder_types` | list[string] | yes | Canonical binder/medium terms in this chunk |
| `historical_period` | enum or string | yes | Historical period scope of this chunk's content |
| `artist_or_school` | list[string] | yes | Artists or schools referenced in this chunk |
| `question_types_supported` | list[enum] | yes | Question classes this chunk helps answer |

## 7.4 Evidence Characterization Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim_types_present` | list[enum] | yes | Evidence types present. See controlled vocabulary §3.5. |
| `case_specificity` | enum | yes | Whether this chunk is case-specific, broadly applicable, mixed, or unknown. See controlled vocabulary §3.6. |
| `citability` | enum | yes | How this chunk may be cited. See controlled vocabulary §3.13. |

## 7.5 Retrieval and Approval Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `approval_state` | enum | yes | Operational retrieval gate. Determines which contexts this chunk may be served. See controlled vocabulary §3.14. |
| `retrieval_weight_hint` | int or null | no | Optional manual boost value (0–5) to adjust retrieval prominence |

## 7.6 Quality and Review Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `quality_flags` | list[string] | yes | Quality issues identified during chunking or review. See §10 for canonical flag values. |
| `review_status` | enum | yes | Current metadata review state. See controlled vocabulary §3.17. |

---

# 8. ID Conventions

## 8.1 Source IDs

Format: `SRC-{FAMILY_CODE}-{NNN}`

| Source Family | Family Code | Example |
|--------------|-------------|---------|
| `museum_conservation` | `MUS` | `SRC-MUS-001` |
| `pigment_reference` | `PIG` | `SRC-PIG-001` |
| `manufacturer` | `MFR` | `SRC-MFR-001` |
| `color_theory` | `COL` | `SRC-COL-001` |
| `historical_practice` | `HIS` | `SRC-HIS-001` |
| `scientific_paper` | `SCI` | `SRC-SCI-001` |

Source IDs are assigned at intake and never changed.

## 8.2 Chunk IDs

Format: `CHK-{source_id}-{NNN}` — three-digit zero-padded sequence number.

Examples:
* `CHK-SRC-MUS-001-001`
* `CHK-SRC-PIG-003-007`

Chunk IDs serve as the ChromaDB document ID. They are assigned once, are stable, and are never regenerated.

## 8.3 Metadata File Names

| Record type | Pattern | Example |
|-------------|---------|---------|
| Source metadata | `{source_id}.json` | `SRC-MUS-001.json` |
| Chunk metadata | `{chunk_id}.json` | `CHK-SRC-MUS-001-001.json` |

## 8.4 Benchmark IDs

Format: `BMK-{CATEGORY_CODE}-{NNN}`

| Category | Code | Example |
|----------|------|---------|
| pigments | `PIG` | `BMK-PIG-001` |
| binders/media | `BND` | `BMK-BND-001` |
| conservation | `CON` | `BMK-CON-001` |
| historical practice | `HIS` | `BMK-HIS-001` |
| color theory | `COL` | `BMK-COL-001` |
| product comparison | `PRD` | `BMK-PRD-001` |
| terminology | `TRM` | `BMK-TRM-001` |

---

# 9. ChromaDB Encoding Notes

ChromaDB metadata accepts only `str`, `int`, `float`, or `bool`.

| Situation | Rule |
|-----------|------|
| List fields | Encode as pipe-delimited string: `"lead_white\|zinc_white"`. Full list preserved in metadata store. |
| Null/None values | Must not be stored in ChromaDB. Use `"unspecified"` for optional enum fields, or omit the field. |
| Date fields | Encode as ISO 8601 string: `"2025-03-09"` |
| Bool fields | Store as-is |

**Retrieval-critical fields that must always be present in ChromaDB metadata:**
`source_id`, `approval_state`, `domain`, `chunk_type`, `source_family`, `citability`, `case_specificity`, `trust_tier`

Full chunk records including all list fields and annotation fields are stored in `storage/metadata_store.py`. ChromaDB stores only the retrieval-critical subset.

---

# 10. Canonical Quality Flag Values

| Flag | Meaning |
|------|---------|
| `ocr_suspect` | OCR quality may have introduced errors |
| `table_messy` | Table extraction was incomplete or poorly structured |
| `citation_unclear` | Source attribution for claims in this chunk is ambiguous |
| `product_specific` | Contains product-specific claims that must not be generalized |
| `case_specific` | From a case study — must not be universalized |
| `historical_scope_unclear` | Historical period or context is ambiguous |
| `needs_manual_review` | Requires human review before approval |
| `low_density` | Low information density; may be transitional or border content |
| `duplicate_suspect` | Appears similar to another chunk; deduplication review needed |

---

# 11. Operational Notes

## 11.1 Metadata completeness gates retrieval

A chunk may not advance to `approval_state: retrieval_allowed` or `live_allowed` unless all required chunk-level fields are populated.

A source may not advance to `indexed: true` unless all required source-level fields are populated.

## 11.2 Trust tier propagates to retrieval

The source-level `trust_tier` is copied into chunk-level retrieval context at indexing time to support tier-aware reranking without requiring a separate source lookup per query.

## 11.3 Review status and approval state are distinct

`review_status` — whether a human has reviewed the chunk's metadata.
`approval_state` — whether the chunk is operationally permitted to be retrieved.

A chunk may have `review_status: approved` and `approval_state: testing_only` if it has passed metadata review but not yet completed the full approval workflow for live retrieval.

## 11.4 Provenance tracking

All metadata values should carry provenance. Provenance is tracked per-field in a separate record stored in the metadata store. See `docs/policies/metadata_provenance_rules.md`.

---

# 12. QA Questions

1. Does the record have a stable, unique ID that will not change?
2. Are all required fields populated with valid enum values or appropriate content?
3. Is `domain` accurately set — not defaulted from source family without verification?
4. Is `case_specificity` correctly set — not defaulted to general when the content is case-specific?
5. Are `materials_mentioned` and `pigment_codes` populated from actual content, not left as empty defaults?
6. Is `trust_tier` consistent with `source_family` and `source_type`?
7. Are `quality_flags` honestly populated — not left empty when problems exist?
8. Is `approval_state` appropriate for the chunk's current review state?
9. Is `citation_format` complete enough to construct a user-facing citation?
10. Are `limitations_notes` and `retrieval_notes` specific enough to guide operational use?

---

# 13. Recommended Companion Documents

1. `docs/foundation/source_hierarchy.md` — trust tier system
2. `docs/foundation/controlled_vocabulary.md` — all enum values referenced in this schema
3. `docs/foundation/chunking_rules.md` — how chunks are created and what metadata they require
4. `docs/policies/metadata_provenance_rules.md` — per-field provenance tracking
5. `docs/policies/review_workflow.md` — review stages and approval state transitions
6. `schemas/source_register_schema.json` — JSON schema implementation of source-level fields
7. `schemas/chunk_schema.json` — JSON schema implementation of chunk-level fields

---

# 14. Adoption Rule

This document is the canonical metadata schema reference for v1 of the Oil Painting Research Assistant.

All ingestion logic, chunking logic, ChromaDB indexing, retrieval filtering, review workflows, and citation assembly must use field names and types consistent with this schema.

Any addition or change to the schema requires updating this document, `docs/foundation/controlled_vocabulary.md`, the affected JSON schema files, and the Pydantic models before implementation proceeds.

---
