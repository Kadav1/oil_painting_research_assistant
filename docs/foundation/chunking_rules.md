# Chunking Rules v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-FND-004
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Rules governing how source documents are divided into retrievable chunks, including chunk size targets, boundary rules, table handling, metadata requirements, quality standards, and review expectations
**Applies to:** All chunking operations in the Oil Painting Research Assistant — automated and manual — and all code that produces or validates chunks

---

# 1. Purpose

This document defines how source documents are divided into retrievable chunks for the Oil Painting Research Assistant.

It establishes:

* the semantic principle that governs all chunking decisions
* target size ranges for different content types
* rules for where chunk boundaries should be placed
* rules for handling tables and structured data
* the minimum metadata each chunk must carry
* citation and context preservation requirements
* rules for preventing unnecessary duplication
* quality flags and review expectations

This is a conceptual and operational rules document, not a code specification.
Code implementing the chunker must comply with these rules.

---

# 2. Core Principle

**Chunk by semantic unit, not by arbitrary character or token count.**

A chunk should contain one coherent, retrievable idea.

The goal is not to produce uniformly sized blocks of text.
The goal is to produce units that can each stand alone as the answer to a specific kind of question, attributed to a specific source, with a specific epistemic status.

A well-formed chunk:
* contains one coherent technical, historical, or practical claim or set of closely related claims
* can be cited independently
* carries enough metadata to support retrieval filtering, reranking, and citation assembly
* does not require the reader to have the surrounding chunks to understand its meaning

A poorly formed chunk:
* cuts across unrelated topics
* contains half an argument that requires the next chunk to make sense
* merges multiple products, materials, or time periods without distinction
* is so short it lacks context, or so long it dilutes retrieval precision

---

# 3. Objectives

1. Ensure every chunk is independently retrievable and citable
2. Preserve the epistemic scope of source content (case-specific, product-specific, historical)
3. Maintain sufficient context for safe citation and paraphrase
4. Prevent duplication while allowing structurally distinct versions of the same content
5. Ensure every chunk carries complete metadata before indexing
6. Support ChromaDB vector indexing and BM25 lexical indexing equally well

---

# 4. Target Chunk Sizes

These are targets, not hard limits. Semantic coherence takes priority over size compliance.

| Content type | Target token range | Notes |
|-------------|-------------------|-------|
| Default prose | 500–900 tokens | General technical, conservation, or historical paragraphs |
| Dense technical prose | 350–700 tokens | Chemistry, material science, highly detailed descriptions |
| Product pages | one product per chunk | Merge short product entries only when they are directly comparable |
| Glossary entries | 100–350 tokens | One definition per chunk; group only when entries are tightly related |
| Tables | 200–600 tokens | Separate chunk; include caption and any interpretive note |
| Figure notes | 50–200 tokens | Caption and immediate context |

A chunk that exceeds 1,200 tokens should be reviewed for a natural split point.
A chunk under 80 tokens is likely too short to retrieve meaningfully and should be merged with an adjacent chunk or flagged for review.

---

# 5. Chunk Boundary Rules

## 5.1 Start a new chunk when

* A heading changes (H1, H2, H3 in the source)
* The material under discussion changes
* The product under discussion changes
* The question type addressed by the content changes
* The document transitions from explanatory prose to a table
* The historical context shifts significantly (e.g. from 15th-century Flemish to 17th-century Dutch)
* Case-study evidence ends and broader interpretation begins
* The conservation claim shifts to a studio recommendation
* A new pigment is introduced after the previous pigment entry concluded

## 5.2 Do not split when

* The paragraph sequence forms one continuous argument
* A technical point depends on the following paragraph to complete its meaning
* A table requires its adjacent caption or interpretive note to be understood
* The split would leave a chunk under 80 tokens
* The split would cut a direct quotation or a cited claim from its attribution

## 5.3 Ambiguous boundaries

When a boundary is ambiguous — where the content could reasonably go either way — prefer the split that preserves the most self-contained unit of meaning. Document the decision in `quality_flags` using `needs_manual_review` if the boundary is uncertain.

---

# 6. Table Handling Rules

Tables in oil painting source material commonly contain:
* pigment property comparisons
* product line data (opacity, pigment codes, vehicle, lightfastness)
* historical period timelines
* conservation risk matrices
* material compatibility charts

## 6.1 Significant tables

A table is significant if it can be used to answer a direct question independently.

For significant tables:
* Create a separate chunk for the table
* Retain the row/column structure in the chunk text, rendered as plain text if necessary
* Include the table caption or heading in the chunk
* Include any immediately adjacent interpretive note (1–2 sentences) in the same chunk
* Set `chunk_type: table`
* Link to the source and section via `section_path`

## 6.2 Extractability issues

If table extraction produces poorly formatted output:
* Flag the chunk with `table_messy`
* Do not treat the table chunk as reliable until a reviewer confirms it
* Do not auto-approve a chunk with `table_messy` set

## 6.3 Structural variants

When a table chunk and a prose summary of the same data both exist:
* Keep both — they are structurally distinct and serve different retrieval needs
* Ensure both link to the same source and section
* They are not duplicates; they are format variants

---

# 7. Chunk Metadata Minimum

A chunk is not ready for indexing until all of the following fields are populated:

| Field | Reason required |
|-------|----------------|
| `chunk_id` | ChromaDB document ID — must be present before indexing |
| `source_id` | Links chunk to parent source for retrieval and citation |
| `chunk_title` | Semantic label used in citation display and retrieval context |
| `section_path` | Supports hierarchical filtering and section-aware retrieval |
| `text` | The content to be indexed |
| `token_estimate` | Size validation and retrieval context budgeting |
| `chunk_type` | Required for type-aware filtering |
| `domain` | Required for domain-scoped retrieval |
| `question_types_supported` | Required for query-mode alignment |
| `claim_types_present` | Required for evidence-type filtering |
| `case_specificity` | Required to prevent inappropriate generalization |
| `citability` | Required to gate citation behavior |
| `approval_state` | Required for retrieval gating — must not default |
| `review_status` | Required for workflow tracking |

A chunk without these fields set must have `approval_state: not_approved` and must not be indexed.

---

# 8. Citation and Context Preservation Rule

Each chunk must preserve enough context for safe paraphrase and citation.

A properly formed chunk must make it possible to answer the following questions without looking at adjacent chunks:

* What is the claim?
* What source does it come from?
* Is this claim case-specific or broadly applicable?
* Is this claim product-specific or general?
* Is this historical, technical, or instructional in nature?
* What is the section or topic this claim belongs to?

If a chunk does not provide enough context to answer these questions, it requires either merger with adjacent content or an expansion of its metadata.

---

# 9. Duplication Prevention Rule

Duplicate chunks inflate the corpus, distort retrieval, and reduce citation reliability.

## 9.1 Exact duplicates

Chunks with identical text from the same source must not both be indexed. Retain the one with better metadata and discard or reject the other.

## 9.2 Structurally distinct versions

The following are **not** duplicates and may coexist:
* One prose version and one table version of the same data
* One full-detail chunk and one glossary abstraction of the same term
* One product-level chunk and one material-level summary when both are independently useful

## 9.3 Near-duplicates across sources

When two chunks from different sources contain highly similar content:
* Do not discard either automatically
* Flag both with `duplicate_suspect`
* Route to the deduplication review workflow (see `docs/policies/deduplication_policy.md`)
* Let the reviewer decide which to retain, mark as canonical, or keep as format variant

---

# 10. Chunk Quality Flags

Apply quality flags honestly. An unflagged chunk is assumed to have been reviewed and cleared.

| Flag | When to apply |
|------|--------------|
| `ocr_suspect` | OCR artefacts visible in the text; accuracy uncertain |
| `table_messy` | Table extraction produced poor structure or garbled content |
| `citation_unclear` | The attribution for claims in the chunk is ambiguous |
| `product_specific` | Chunk contains brand/product-specific claims that must not be generalized |
| `case_specific` | Chunk is from a case study; content must not be universalized |
| `historical_scope_unclear` | The historical period or context of the content is ambiguous |
| `needs_manual_review` | Chunk requires human inspection before approval |
| `low_density` | Chunk has low information content; may be transitional or border content |
| `duplicate_suspect` | Chunk appears similar to another chunk in the corpus |

Multiple flags may apply simultaneously. Flags are stored as a list of strings.

---

# 11. Review Expectations

## 11.1 Auto-populated chunks

Chunks produced by automated chunking should begin with `review_status: draft` and `approval_state: not_approved`.

They must not be indexed until:
* a reviewer has confirmed the metadata fields are accurate
* quality flags have been addressed or acknowledged
* `review_status` has been advanced to `reviewed` or `approved`
* `approval_state` has been set appropriately

## 11.2 Manual chunking

Chunks produced by manual inspection should still go through the review workflow. Manual creation does not bypass approval.

## 11.3 Metadata completeness check

Before approving a chunk, a reviewer must confirm:

1. `domain` reflects the actual content of the chunk, not just the source
2. `case_specificity` is set correctly — not defaulted to `broadly_applicable`
3. `materials_mentioned` and `pigment_codes` are populated from actual chunk content
4. `quality_flags` are either empty (clean) or populated with accurate flags
5. `chunk_title` is a meaningful semantic label, not a generic heading copy

---

# 12. Special Cases

## 12.1 Product data sheets

Product pages and TDS documents typically contain:
* one product per page or section
* multiple fields: pigment codes, vehicle, lightfastness, opacity, tinting strength, notes

Rule: create one chunk per product unless multiple products are so closely related that splitting would destroy meaning. If a comparison table exists, create a separate table chunk.

## 12.2 Glossary sources

Glossary documents should be chunked one definition at a time, or grouped in sets of 2–4 closely related terms where grouping adds context.

Set `chunk_type: glossary` for all glossary chunks.

## 12.3 Long conservation reports

Conservation case studies and technical bulletins may be long. Chunk by section heading. Each section addressing a different material, treatment, or finding should be a separate chunk.

Set `case_specificity: case_specific` unless the section explicitly generalizes beyond the case.

## 12.4 Chapters with tables and prose

When a source chapter contains both tables and interpretive prose:
* Create one table chunk per significant table
* Create one or more prose chunks for the surrounding text
* Link both to the same `section_path`
* They are not duplicates — they are structurally distinct and complement each other in retrieval

---

# 13. QA Questions

Before approving a batch of chunks from a source, a reviewer should be able to answer yes to all of the following:

1. Does each chunk contain a single coherent idea or closely related set of ideas?
2. Is every chunk independently citable — can its claim be attributed without needing adjacent chunks?
3. Are chunk boundaries aligned with heading changes, material changes, or topic shifts?
4. Is no chunk below 80 tokens or above 1,200 tokens without a documented reason?
5. Are all tables in significant tabular sources represented as separate table chunks?
6. Are `case_specificity`, `domain`, and `question_types_supported` set from actual chunk content?
7. Are quality flags honestly populated — not left empty when issues exist?
8. Are duplicates identified and routed to the deduplication workflow?
9. Does every chunk have all required metadata fields populated?
10. Is no chunk in the indexing queue with `approval_state: not_approved`?

---

# 14. Recommended Companion Documents

1. `docs/foundation/metadata_schema.md` — defines all chunk-level metadata fields
2. `docs/foundation/controlled_vocabulary.md` — defines all enum values used in chunk metadata
3. `docs/policies/deduplication_policy.md` — governs how duplicate chunks are identified and resolved
4. `docs/policies/review_workflow.md` — defines the review stages and approval transitions for chunks
5. `docs/policies/metadata_provenance_rules.md` — governs how chunk metadata field values are tracked

---

# 15. Adoption Rule

This document defines the canonical chunking rules for v1 of the Oil Painting Research Assistant.

All automated chunking code, manual chunking workflows, and chunk validation logic must comply with the rules defined here.

Any change to these rules requires a version increment to this document and a review of existing chunks that may not comply with the updated rules.

---
