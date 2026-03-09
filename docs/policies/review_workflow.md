# Review Workflow v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-005
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Human review workflow for sources, metadata, chunks, duplicates, conflicts, and release readiness
**Applies to:** All source ingestion, metadata approval, chunk approval, duplicate resolution, conflict resolution, and corpus activation in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This document defines the human review workflow for the Oil Painting Research Assistant.

Its purpose is to ensure that the corpus does not move from:

* captured
* normalized
* inferred
* model-suggested

into:

* trusted
* indexed
* retrievable
* answer-generating

without a clear review path.

This workflow exists to prevent:

* unreviewed metadata becoming operational truth
* duplicate or superseded sources entering active retrieval unnoticed
* case-specific evidence being treated as general
* model-suggested summaries being mistaken for reviewed source descriptions
* unresolved conflicts silently affecting answers
* partial ingestion being confused with approved corpus content

---

# 2. Core Principle

A source is not trustworthy because it has been processed.

A source becomes operationally trustworthy only after it has passed the appropriate review gates.

The workflow must always make it possible to answer:

1. What stage is this artifact in?
2. Who reviewed it?
3. What was confirmed, corrected, deferred, or rejected?
4. Is it safe for retrieval?
5. Is it safe for live answer generation?

---

# 3. Workflow Objectives

This review workflow is designed to achieve six things:

## 3.1 Preserve corpus trust

Only reviewed material should shape live answers unless a specific experimental mode allows otherwise.

## 3.2 Separate draft from approved

A processed artifact is not necessarily an approved artifact.

## 3.3 Make decisions auditable

Every important review outcome should leave a trail.

## 3.4 Support staged progress

The system should support partial completion without pretending completion.

## 3.5 Reduce silent error propagation

Incorrect classifications, bad extraction, stale product pages, and poor chunking should be caught before they affect retrieval.

## 3.6 Support future maintenance

Updates, corrections, and supersession should fit into the same workflow instead of bypassing it.

---

# 4. Review Scope

This workflow applies to six artifact classes:

1. **Source candidates**
2. **Source metadata records**
3. **Normalized source text**
4. **Chunks**
5. **Duplicate decisions**
6. **Conflict decisions**

It also governs **release readiness** for:

* indexing
* retrieval eligibility
* live-answer eligibility

---

# 5. Roles

One person may hold multiple roles, but the roles should remain conceptually separate.

## 5.1 Intake Operator

Responsible for:

* discovery
* registration
* capture
* normalization
* first-pass metadata drafting

## 5.2 Reviewer

Responsible for:

* factual and structural review
* metadata confirmation/correction
* duplicate review
* conflict review
* readiness decisions

## 5.3 Maintainer

Responsible for:

* policy consistency
* release gating
* change management
* versioning
* escalation and final approval standards

## 5.4 Optional Specialist Reviewer

Used when needed for high-stakes areas such as:

* conservation interpretation
* product/version disputes
* historically sensitive classification

---

# 6. Workflow Stages

The canonical workflow stages are:

1. `candidate`
2. `registered`
3. `captured`
4. `normalized`
5. `metadata_drafted`
6. `review_pending`
7. `reviewed_confirmed`
8. `reviewed_corrected`
9. `approved_for_chunking`
10. `chunked`
11. `chunk_review_pending`
12. `approved_for_indexing`
13. `indexed`
14. `approved_for_retrieval`
15. `approved_for_live_use`
16. `deferred`
17. `rejected`
18. `superseded`

These stages apply primarily at the source level, but chunks and related decisions should use compatible state labels.

---

# 7. Status Meanings

## `candidate`

Potential source identified, not yet formally admitted.

## `registered`

Source has a register entry and identity scaffold.

## `captured`

Raw source preserved.

## `normalized`

Clean text created and major extraction complete.

## `metadata_drafted`

Metadata exists, but is not yet trusted.

## `review_pending`

Awaiting human review.

## `reviewed_confirmed`

Reviewed and accepted without material correction.

## `reviewed_corrected`

Reviewed and corrected.

## `approved_for_chunking`

Safe to turn into chunks.

## `chunked`

Chunk artifacts exist.

## `chunk_review_pending`

Chunks need review before indexing.

## `approved_for_indexing`

Safe to index.

## `indexed`

Present in index, but not necessarily live.

## `approved_for_retrieval`

Allowed in retrieval for testing or limited use.

## `approved_for_live_use`

Allowed to influence normal answers.

## `deferred`

Not rejected, but blocked pending further work.

## `rejected`

Not suitable for active corpus use.

## `superseded`

Retained for history/audit but not active by default.

---

# 8. Review Gates

The workflow has five major gates.

## Gate 1 — Admission Review

Checks whether a source should enter the corpus at all.

## Gate 2 — Metadata Review

Checks whether source metadata is sufficiently correct and trustworthy.

## Gate 3 — Chunk Review

Checks whether chunking preserved meaning and did not create harmful duplication or fragmentation.

## Gate 4 — Indexing Review

Checks whether the source/chunks are fit to enter retrieval infrastructure.

## Gate 5 — Live Use Review

Checks whether the material is safe for normal answer generation.

A source may pass one gate without passing later gates.

---

# 9. Gate 1 — Admission Review

## Purpose

Decide whether the source should proceed beyond candidate/registration.

## Reviewer checks

* scope relevance
* publisher clarity
* source family/source type plausibility
* legal/storage concerns
* obvious duplication
* obvious low-value or low-rigor problems
* provisional corpus value

## Possible outcomes

* approve for capture
* defer
* reject

## Minimum outputs

* decision
* reviewer
* decision date
* reason
* next action if deferred

---

# 10. Gate 2 — Metadata Review

## Purpose

Decide whether source metadata is good enough to support chunking and later retrieval.

## Reviewer checks

* title
* author/institution
* publication year or unknown handling
* source family
* source type
* domain/subdomain
* materials mentioned
* pigment codes if present
* binder/media terms if present
* case-study vs general status
* trust tier
* summary
* limitations notes
* provenance state
* review status for critical fields

## Possible outcomes

* confirm
* correct
* defer
* reject metadata as unreliable

## Minimum outputs

* per-field confirmation or correction
* provenance updates
* review note
* source metadata review state

---

# 11. Gate 3 — Chunk Review

## Purpose

Decide whether the chunks represent the source accurately and usefully.

## Reviewer checks

* semantic coherence
* chunk boundary quality
* missing or broken sections
* table handling
* duplicated chunk content
* chunk titles
* section paths
* domain/question-type tagging
* case-specificity where relevant
* quality flags
* citation support

## Possible outcomes

* approve chunks
* approve with warnings
* request rechunking
* reject chunk set
* defer for manual cleanup

## Minimum outputs

* chunk review decision
* notes on chunking quality
* duplicate/overlap observations
* chunk readiness state

---

# 12. Gate 4 — Indexing Review

## Purpose

Decide whether the reviewed chunks should be added to search/retrieval infrastructure.

## Reviewer checks

* source is not rejected
* metadata is sufficiently reviewed
* chunk set is approved
* duplicate handling has been performed
* unresolved conflicts do not make the source unsafe for indexing
* citation metadata exists at acceptable level
* retrieval risk is acceptable

## Possible outcomes

* approve for indexing
* index for experimental/testing only
* defer indexing
* reject indexing

## Minimum outputs

* indexing decision
* index scope
* restrictions if any

---

# 13. Gate 5 — Live Use Review

## Purpose

Decide whether indexed material is safe for normal answer generation.

## Reviewer checks

* trust tier appropriate for live use
* metadata sufficiently reviewed
* unresolved conflicts appropriately scoped
* source is not heavily stale for its source family
* duplicate suppression in place
* citation readiness acceptable
* no major known failure risks for this source/chunk group

## Possible outcomes

* approve for live use
* approve for limited mode only
* approve for internal testing only
* defer
* block from live use

## Minimum outputs

* live-use decision
* allowed modes or restrictions
* release note

---

# 14. Artifact-Level Review Requirements

Different artifact classes require different review depth.

## 14.1 Source candidate

Needs:

* relevance
* identity
* admission suitability

## 14.2 Source metadata

Needs:

* critical-field review
* provenance review
* trust-tier review
* case/general review

## 14.3 Normalized text

Needs:

* extraction sanity
* missing-section check
* boilerplate corruption check
* table integrity check

## 14.4 Chunk set

Needs:

* semantic boundary review
* duplication review
* citation-readiness check
* question-fit check

## 14.5 Duplicate decision

Needs:

* canonical selection
* cluster decision
* suppression/deletion choice
* rationale

## 14.6 Conflict decision

Needs:

* conflict classification
* scope analysis
* prefer one / keep both / scope split decision
* answer-disclosure determination

---

# 15. Critical Fields That Must Be Reviewed Before Live Use

These fields should not remain unreviewed if the source is approved for live use:

* `title`
* `institution_or_publisher`
* `source_family`
* `source_type`
* `domain`
* `trust_tier`
* `case_study_vs_general`
* `summary`
* `limitations_notes`
* `citation_format`
* `ready_for_use`

For applicable sources, also review:

* `pigment_codes`
* `binder_types`
* `historical_period`

---

# 16. Review Actions

Allowed review actions:

* `confirm`
* `correct`
* `defer`
* `reject`
* `approve_with_warnings`
* `send_back_for_revision`
* `supersede`
* `restore`

## Meaning

### `confirm`

Field/artifact is acceptable as-is.

### `correct`

Field/artifact is acceptable after modification.

### `defer`

Not rejected, but not ready.

### `reject`

Not suitable for current use.

### `approve_with_warnings`

Usable, but with explicit limitations.

### `send_back_for_revision`

Needs processing changes before re-review.

### `supersede`

Older artifact remains in history but loses primary status.

### `restore`

Previously suppressed/rejected item is reinstated.

---

# 17. Review Record Requirements

Every review event should record:

* `review_id`
* `entity_type`
* `entity_id`
* `review_stage`
* `reviewer`
* `review_date`
* `action`
* `status_before`
* `status_after`
* `summary_of_findings`
* `field_changes`
* `warnings`
* `next_action`
* `notes`

This must apply to:

* source review
* metadata review
* chunk review
* duplicate review
* conflict review

---

# 18. Approval Levels

To support more granular release control, use these approval levels:

* `not_approved`
* `internal_draft_only`
* `testing_only`
* `retrieval_allowed`
* `live_allowed`

## Meaning

### `internal_draft_only`

Visible to maintainers only.

### `testing_only`

May be used in retrieval tests or benchmark runs.

### `retrieval_allowed`

Can enter retrieval, but not necessarily normal user-facing synthesis.

### `live_allowed`

Can influence normal answer generation.

---

# 19. Warnings and Restrictions

Approval does not have to be binary.

A source/chunk may be approved with restrictions such as:

* product-comparison only
* not for historical questions
* not for live use until duplicate review complete
* retrieval only, not citation-preferred
* use only if higher-tier evidence absent
* case-specific evidence only

Restrictions should be stored explicitly, not left in free text only.

---

# 20. Deferment Rules

Use `deferred` when the artifact is potentially valuable but blocked by one or more of:

* unresolved metadata ambiguity
* unresolved duplicate status
* unresolved conflict status
* poor extraction quality
* missing critical fields
* incomplete provenance
* unclear citation support
* need for manual cleanup
* pending specialist review

Deferred artifacts must include:

* defer reason
* required next action
* responsible role
* re-review condition

---

# 21. Rejection Rules

Reject when:

* source is out of scope
* identity cannot be established
* extraction is unusably corrupt
* legal/storage constraints block practical use
* source is too weak to justify inclusion
* metadata remains too unreliable after review
* chunking is beyond practical salvage
* source introduces more confusion than value

Rejected items should remain logged with:

* rejection reason
* reviewer
* date
* whether re-submission is allowed

Do not silently delete rejected artifacts from audit history.

---

# 22. Revision Loop

A review failure should feed a revision loop, not only a terminal stop.

## Revision cycle

1. artifact reviewed
2. issue identified
3. revision requested
4. artifact updated
5. provenance/history updated
6. artifact re-enters review queue

### Rule

Revised artifacts must not overwrite the fact that a prior version failed review.

---

# 23. Escalation Rules

Escalate review when:

* trust tier is unclear
* conflict is materially important
* historical interpretation is disputed
* product/version differences affect practical recommendations
* multiple reviewers disagree
* benchmark failures suggest hidden metadata or retrieval problems

Escalation should produce:

* escalation note
* responsible specialist/reviewer
* decision deadline or condition
* final resolution record

---

# 24. Review by Artifact State Transition

Recommended state transitions:

## Source

`candidate → registered → captured → normalized → metadata_drafted → review_pending → reviewed_confirmed/reviewed_corrected → approved_for_chunking`

## Chunk set

`approved_for_chunking → chunked → chunk_review_pending → approved_for_indexing`

## Retrieval readiness

`approved_for_indexing → indexed → approved_for_retrieval`

## Live readiness

`approved_for_retrieval → approved_for_live_use`

Alternative paths:

* any stage → deferred
* any stage → rejected
* approved artifact → superseded

---

# 25. Minimum QA Questions Per Review

## Admission Review

1. Is this source in scope?
2. Is it identifiable?
3. Does it add meaningful value?
4. Is it too weak or too redundant?

## Metadata Review

1. Are critical fields believable?
2. What was extracted vs inferred vs suggested?
3. Is case/general status correct?
4. Is trust tier reasonable?

## Chunk Review

1. Do chunks preserve meaning?
2. Are chunk boundaries sensible?
3. Are there harmful overlaps or duplicates?
4. Are chunk tags useful and believable?

## Live Use Review

1. Is this safe for normal answers?
2. Are unresolved problems clearly bounded?
3. Would I trust this to shape a response without manual babysitting?

---

# 26. Review Logs

Maintain at least these logs:

1. `source_review_log.csv`
2. `metadata_review_log.csv`
3. `chunk_review_log.csv`
4. `duplicate_review_log.csv`
5. `conflict_review_log.csv`
6. `release_approval_log.csv`

These logs make the workflow inspectable and auditable.

---

# 27. Recommended Structured Outputs

This workflow should be supported by:

1. `review_record_schema.json`
2. `approval_state_schema.json`
3. `restriction_flags.json`
4. `recheck_queue.json`
5. `review_dashboard.csv` or equivalent

---

# 28. Non-Negotiable Rules

## 28.1 No live use without review

Nothing becomes normal-answer eligible without human review.

## 28.2 No reviewed status without actual reviewer action

Automation cannot self-award reviewed status.

## 28.3 No silent promotion

An artifact must not jump from draft to live use without passing defined gates.

## 28.4 No silent correction

Material review changes must be recorded.

## 28.5 No unresolved critical ambiguity in live mode

If critical ambiguity remains, the artifact must stay restricted, deferred, or blocked.

## 28.6 No mixing approved and draft states invisibly

Retrieval and answer systems must be able to distinguish approval states.

---

# 29. Operational Checklist

## Source Review

* [ ] Admission checked
* [ ] Identity checked
* [ ] Scope checked
* [ ] Initial status assigned

## Metadata Review

* [ ] Critical fields reviewed
* [ ] Provenance reviewed
* [ ] Trust tier reviewed
* [ ] Summary/limitations reviewed

## Chunk Review

* [ ] Chunk boundaries reviewed
* [ ] Duplication reviewed
* [ ] Table handling reviewed
* [ ] Chunk metadata reviewed

## Release Review

* [ ] Indexed state appropriate
* [ ] Retrieval safety checked
* [ ] Live-use restrictions checked
* [ ] Final approval logged

---

# 30. Recommended Companion Documents

This workflow works together with:

1. `source_acquisition_policy.md`
2. `metadata_provenance_rules.md`
3. `deduplication_policy.md`
4. `conflict_resolution_policy.md`
5. `retrieval_policy_v1.md`
6. `benchmark_gold_set_v1.json`

---
