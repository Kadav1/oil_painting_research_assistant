# Deduplication Policy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-003
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Source-level and chunk-level deduplication rules
**Applies to:** All ingested, normalized, chunked, and indexed content in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This policy defines how duplicate and near-duplicate content must be detected, labeled, resolved, and tracked in the Oil Painting Research Assistant corpus.

Its purpose is to prevent:

* the same source being stored multiple times without awareness
* revised versions being mistaken for unique evidence
* product pages being captured repeatedly and overweighting retrieval
* one claim appearing multiple times in the index and creating false confidence
* the final assistant answer being distorted by redundant chunks

This policy applies at two levels:

1. **source-level deduplication**
2. **chunk-level deduplication**

It also covers:

* revised and superseded sources
* mirrored content
* structurally duplicated product data
* repeated boilerplate
* retrieval-time redundancy control

---

# 2. Core Principle

Duplicate content is not neutral.

A duplicate source does not strengthen evidence simply because it appears multiple times in the corpus.

The corpus must distinguish between:

* truly unique evidence
* the same evidence in another format
* a revised version of the same source
* a mirrored copy
* a near-duplicate paraphrase
* repeated product boilerplate
* meaningful overlap that should remain separate

The system must never allow duplication to masquerade as corroboration.

---

# 3. Policy Objectives

This policy exists to achieve six things:

## 3.1 Preserve epistemic integrity

Prevent one source from being counted multiple times as if it were multiple independent pieces of evidence.

## 3.2 Improve retrieval quality

Reduce repetitive top-k results and same-source flooding.

## 3.3 Support update handling

Distinguish revised/superseding versions from redundant copies.

## 3.4 Reduce storage clutter

Avoid unnecessary duplication of raw, clean, and chunked artifacts.

## 3.5 Improve citation clarity

Ensure that the assistant cites the best version of a source instead of arbitrary duplicates.

## 3.6 Maintain auditability

Keep a trace of duplicate decisions instead of silently deleting evidence.

---

# 4. Deduplication Levels

The policy distinguishes four levels of duplication.

## 4.1 Exact duplicate

The content is functionally identical.

Examples:

* same PDF downloaded twice
* same HTML captured twice
* same normalized text generated twice
* same chunk text appearing with only trivial whitespace differences

## 4.2 Format duplicate

The same source exists in different formats.

Examples:

* official page saved as HTML and PDF
* webpage and print view with same content
* PDF report and plain-text extraction of the same report

## 4.3 Version duplicate

The source is the same document or product page, but a newer or older version exists.

Examples:

* revised technical sheet
* updated product page snapshot
* second edition of a reference entry
* product page captured on multiple dates

## 4.4 Near duplicate

The content is substantially overlapping but not identical.

Examples:

* repeated product copy on color pages in the same brand line
* two chunks that say the same thing with minor wording changes
* educational page rephrased into a product help page
* a duplicated chunk created by bad chunking boundaries

---

# 5. What Counts as a Duplicate

A source or chunk should be treated as duplicate or near-duplicate if it adds no meaningful new value in one or more of these dimensions:

* factual content
* evidentiary independence
* structure
* metadata quality
* version freshness
* interpretive scope

A source is **not** necessarily a duplicate just because it overlaps.
Overlap is acceptable when the source adds one of these:

* stronger authority
* clearer structure
* more reliable metadata
* better citation data
* different source type
* meaningful new scope
* a distinct version with relevant changes

---

# 6. Deduplication Entity Types

This policy applies to:

## 6.1 Raw source files

Examples:

* PDFs
* HTML captures
* text exports
* local snapshots

## 6.2 Normalized sources

Examples:

* cleaned markdown
* structured text
* extracted tables

## 6.3 Source records

Examples:

* source register entries
* metadata sidecars
* re-imported records

## 6.4 Chunks

Examples:

* semantic text chunks
* table chunks
* glossary chunks
* mixed chunks

## 6.5 Retrieval result sets

Examples:

* top-k results containing multiple redundant chunks
* repeated same-source content in context assembly

---

# 7. Source-Level Duplicate Categories

Allowed duplicate classification values:

* `unique`
* `exact_duplicate`
* `format_duplicate`
* `version_duplicate`
* `near_duplicate`
* `superseded_version`
* `superseding_version`
* `possible_duplicate`
* `duplicate_cluster_member`

## 7.1 Definitions

### `unique`

No meaningful duplicate currently known.

### `exact_duplicate`

Same source content captured more than once.

### `format_duplicate`

Same source content in another representation.

### `version_duplicate`

Same source family/document identity but another version exists.

### `near_duplicate`

Strong overlap, but not fully identical.

### `superseded_version`

Older version retained for audit/history but not preferred for retrieval.

### `superseding_version`

Preferred newer version of the same source.

### `possible_duplicate`

Needs human review.

### `duplicate_cluster_member`

Part of a group of related duplicates or near-duplicates.

---

# 8. Chunk-Level Duplicate Categories

Allowed chunk duplicate classification values:

* `unique`
* `exact_duplicate`
* `near_duplicate`
* `same_source_overlap`
* `cross_source_overlap`
* `boilerplate_duplicate`
* `table_duplicate`
* `possible_duplicate`

## 8.1 Definitions

### `same_source_overlap`

Two chunks from the same source materially overlap because of bad or loose chunking.

### `cross_source_overlap`

Two chunks from different sources overlap heavily in content.

### `boilerplate_duplicate`

Repeated vendor copy, product line copy, or page-template text that is not unique evidence.

### `table_duplicate`

Repeated structured data in both table and prose-rendered form.

---

# 9. Duplicate Detection Signals

The system should detect duplicates using multiple signals, not one signal only.

## 9.1 Strong signals

* identical URL
* identical source title + publisher + year
* file hash match
* normalized text hash match
* identical chunk text hash
* identical product name + brand + page snapshot + same body text

## 9.2 Moderate signals

* very high text similarity
* same source family + same title + similar body
* same product page with minor formatting change
* same chunk meaning with small token variation
* same table rendered in different forms

## 9.3 Weak signals

* same pigment name appears
* same general topic
* overlapping keywords only

Weak signals are not enough alone for duplicate classification.

---

# 10. Recommended Detection Methods

Use layered detection.

## 10.1 Source-level detection

Recommended checks:

* raw file hash
* normalized text hash
* canonical URL match
* title normalization + publisher match
* version/snapshot date comparison
* fuzzy similarity of clean text

## 10.2 Chunk-level detection

Recommended checks:

* normalized chunk hash
* fuzzy text similarity
* semantic embedding similarity
* same section path + same source
* repeated structured table rows
* repeated product descriptions across pages

## 10.3 Retrieval-time detection

Recommended checks:

* same `source_id` overrepresented
* same duplicate cluster overrepresented
* high pairwise similarity among retrieved chunks
* repeated citations to effectively same content

---

# 11. Canonical Source Selection Rule

When duplicates are detected, the system must determine a **canonical source**.

The canonical source is the one preferred for:

* retrieval
* citation
* chunking
* indexing
* benchmark use

The canonical source should be selected using this priority order:

1. reviewed and approved source
2. higher trust tier
3. better metadata completeness
4. better citation quality
5. better extraction quality
6. fresher version when freshness matters
7. cleaner normalized text
8. richer structure (e.g. table + prose integrity)

## Rule

The canonical source is not always the newest source.
For stable historical references, the best-structured or best-cited source may remain preferred.

---

# 12. Freshness and Supersession Rules

Freshness matters mostly for:

* manufacturer product pages
* technical sheets
* SDS/TDS
* web-maintained product documentation

It matters less for:

* historical technical bulletins
* archival papers
* fixed reference texts

## 12.1 When to supersede

Mark an older source as `superseded_version` when:

* a clearly newer version exists
* the newer version is same-source identity
* the newer version is more complete or more current
* the older version is not needed as default retrieval target

## 12.2 When to retain older versions

Retain older versions if:

* formulation history matters
* version comparison matters
* product change itself is historically relevant
* the older source contains content omitted later
* audit trail requires retention

Retained older versions should not be active by default unless the query requires historical comparison.

---

# 13. Mirror and Rehost Rules

A mirrored or reposted source should not usually be treated as independent evidence.

Examples:

* same PDF mirrored elsewhere
* reposted brand SDS on third-party site
* copied article in a PDF repository

## Rule

Prefer the most authoritative origin:

1. original publisher
2. official mirror
3. archived official capture
4. third-party repost only if necessary

Third-party copies may remain as fallback artifacts but should not become primary citation sources if official origin is available.

---

# 14. Product Page Duplication Rules

Manufacturer content is especially prone to duplication.

Common patterns:

* same line description on every product page
* repeated permanence paragraphs
* repeated drying notes
* identical product descriptions across shades
* archived snapshots with unchanged copy

## Rule

Repeated product boilerplate should be detected and labeled as `boilerplate_duplicate`.

It may remain in storage, but should receive reduced retrieval weight.

## Rule

A product page is not a duplicate just because the line-level boilerplate repeats.
What matters is whether product-specific fields differ, such as:

* pigment code
* opacity
* vehicle
* drying notes
* lightfastness
* product name
* formulation date/version

---

# 15. Chunking-Introduced Duplication

Bad chunking can create duplicates.

Examples:

* overlapping sliding windows with too much overlap
* table content duplicated in prose chunks
* paragraph repeated across adjacent chunks
* section intro repeated in multiple chunks

## Rule

Chunk overlap must be controlled.

If overlap is used, it should be:

* minimal
* intentional
* documented

Large accidental overlaps should be cleaned before indexing.

---

# 16. Table Duplication Rules

Tables are allowed to exist in more than one form if each form has a distinct retrieval function.

Acceptable pair:

* structured table JSON
* text-rendered table chunk

Not acceptable:

* three nearly identical table renderings indexed equally

## Rule

Where a table exists in multiple forms:

* choose one primary retrieval form
* mark others as secondary or linked
* reduce duplicate weight in retrieval

---

# 17. Duplicate Clusters

Related duplicates should be grouped into a cluster.

Each duplicate cluster should have:

* `cluster_id`
* list of member source_ids or chunk_ids
* canonical member
* duplicate type
* decision note
* reviewer
* decision date

This allows the system to:

* preserve audit history
* suppress redundant retrieval
* compare versions when needed

---

# 18. Required Duplicate Metadata Fields

At source level, support fields such as:

* `duplicate_status`
* `duplicate_cluster_id`
* `canonical_source_id`
* `duplicate_reason`
* `superseded_by`
* `supersedes`
* `dedupe_review_status`
* `dedupe_reviewed_by`
* `dedupe_reviewed_at`

At chunk level, support:

* `duplicate_status`
* `duplicate_cluster_id`
* `canonical_chunk_id`
* `duplicate_reason`
* `dedupe_weight_modifier`

---

# 19. Review Workflow for Duplicate Decisions

Automated detection may suggest duplicates, but human review should resolve important cases.

## 19.1 Auto-detect stage

System assigns:

* `possible_duplicate`
* similarity metrics
* candidate canonical partner

## 19.2 Human review stage

Reviewer decides:

* keep as unique
* mark as exact duplicate
* mark as near duplicate
* mark as superseded/superseding
* merge cluster
* preserve both with explicit note

## 19.3 Resolution stage

System updates:

* cluster membership
* canonical source/chunk
* retrieval weight
* index inclusion state

---

# 20. When Both Sources Should Remain

Do not deduplicate away a source merely because it overlaps.

Keep both when they represent genuinely different value, such as:

* different source type with same subject
  Example: manufacturer product page + conservation paper on same pigment

* different evidentiary role
  Example: case study + general pigment reference

* different temporal state
  Example: older and newer product versions where change matters

* different operational use
  Example: structured table vs explanatory prose

Overlap alone is not enough for removal.

---

# 21. Removal vs Suppression

The policy distinguishes:

## 21.1 Removal

Delete or archive duplicate from active working set.

Use only for:

* exact redundant artifacts
* corrupt duplicate files
* accidental repeated imports

## 21.2 Suppression

Keep the duplicate for audit/history but reduce or disable its role in retrieval.

Use for:

* superseded versions
* mirrored copies
* boilerplate duplicates
* near-duplicate chunks

## Rule

Prefer suppression over deletion unless the duplicate is clearly useless.

---

# 22. Retrieval-Time Redundancy Control

Even after storage deduplication, retrieval must still avoid redundancy.

## 22.1 Retrieval diversity rule

The context builder must not allow:

* too many chunks from same source
* too many chunks from same duplicate cluster
* too many near-identical product chunks
* same evidence repeated in slightly different chunk forms

## 22.2 Recommended caps

Suggested defaults:

* no more than 2 chunks from same source unless query strongly requires it
* no more than 1 canonical member per duplicate cluster in primary context
* boilerplate duplicates heavily downweighted

## 22.3 Exceptions

Allow exceptions if:

* question asks for version comparison
* question asks for product-vs-product comparison
* question requires multiple sections from same source
* question explicitly asks for evidence breadth inside one case study

---

# 23. Citation Rules for Duplicates

When citing duplicated material:

* cite the canonical source
* prefer original publisher version
* prefer reviewed and better-cited version
* avoid citing both duplicate and canonical unless version comparison is the point

If comparing versions:

* cite both explicitly as different versions
* do not imply they are independent corroboration

---

# 24. Duplicate Decision Rules by Source Family

## 24.1 Museum conservation

Usually keep distinct papers unless they are actually the same publication in multiple formats.

Do not mark two different papers as duplicates merely because they cover the same artwork or pigment.

## 24.2 Pigment reference

Often overlapping but not duplicate unless same entry mirrored or re-exported.

## 24.3 Manufacturer

High duplicate risk.
Watch for:

* repeated boilerplate
* archived snapshots
* multiple captures of same page
* same product across regions with trivial wording changes

## 24.4 Color theory

Lower duplicate risk, but web captures and print/PDF variants may duplicate.

## 24.5 Historical practice

Be careful: overlap in teaching language does not make texts duplicates if they differ in sourcing or interpretation.

## 24.6 Scientific paper

Mirror copies are duplicates; separate papers on same subject are not duplicates.

---

# 25. Non-Negotiable Rules

## 25.1 No duplicate inflation

Repeated content must not count as multiple independent evidence sources.

## 25.2 No silent deletion

Every duplicate decision must leave a trace.

## 25.3 No forced collapsing across source types

A product page and a conservation paper are not duplicates simply because they discuss the same material.

## 25.4 No canonical source without reason

Canonical selection must be explainable.

## 25.5 No retrieval flooding

Duplicate clusters must not dominate context assembly.

## 25.6 No freshness confusion

Newer is not always better, except where freshness materially matters.

---

# 26. Minimum QA Questions for Duplicate Review

Before resolving a duplicate case, the reviewer should be able to answer:

1. Are these truly the same source, or just about the same topic?
2. Is this an exact duplicate, a format duplicate, a version duplicate, or only a near duplicate?
3. Which one should be canonical, and why?
4. Does freshness matter here?
5. Does each source have distinct evidentiary value?
6. Will keeping both distort retrieval?
7. Is this a case for deletion, suppression, or retention with clustering?

If these cannot be answered, the duplicate decision is not mature enough.

---

# 27. Operational Checklist

## Discovery

* [ ] Possible duplicate detected
* [ ] Duplicate signals recorded
* [ ] Candidate comparison object identified

## Assessment

* [ ] Exact vs near duplicate checked
* [ ] Source type difference checked
* [ ] Version/freshness relevance checked
* [ ] Canonical candidate identified

## Review

* [ ] Human reviewed important case
* [ ] Duplicate status assigned
* [ ] Cluster created if needed
* [ ] Canonical source/chunk marked

## Resolution

* [ ] Retrieval weight updated
* [ ] Index inclusion updated
* [ ] Citation preference updated
* [ ] Audit note stored

---

# 28. Recommended Outputs

This policy should be supported by:

1. `duplicate_cluster_schema.json`
2. `dedupe_review_log.csv`
3. `chunk_similarity_report.json`
4. `source_similarity_report.json`

These make duplicate handling operational and reviewable.
