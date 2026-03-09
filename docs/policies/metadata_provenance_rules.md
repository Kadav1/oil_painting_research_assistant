# Metadata Provenance Rules v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-002
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Provenance, confidence, and review-state rules for metadata fields
**Applies to:** All source-level and chunk-level metadata in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This document defines how metadata fields must record:

* **where a value came from**
* **how it was obtained**
* **how certain it is**
* **whether it has been reviewed**
* **whether it overrides an earlier value**

Its purpose is to prevent the corpus from silently mixing:

* extracted facts
* inferred guesses
* human judgments
* corrected values
* stale values

Without provenance rules, the system may look structured while still being epistemically unstable.

---

# 2. Core Principle

A metadata value is not trustworthy merely because it exists.

Every important field must be treated as one of these:

* directly extracted
* inferred by rule
* suggested by model
* manually entered
* manually reviewed
* manually overridden

The system must always be able to answer:

1. **What is the value?**
2. **Where did it come from?**
3. **How was it produced?**
4. **Who last confirmed it?**
5. **How confident are we in it?**

---

# 3. Why This Policy Exists

These rules are meant to stop five common failures:

## 3.1 Extraction false certainty

A parser pulls a year or title incorrectly, and the system treats it as fact.

## 3.2 Inference flattening

A classifier guesses `source_type = technical_bulletin`, and that guess later becomes indistinguishable from a human-reviewed classification.

## 3.3 Silent overrides

A field gets corrected manually, but the system loses the original extracted value.

## 3.4 Mixed-trust metadata

A pigment code extracted from a product page gets stored in the same trust state as a guessed subdomain or a model-written summary.

## 3.5 Debugging blindness

When retrieval goes wrong, nobody can tell whether the problem came from:

* bad extraction
* bad inference
* bad review
* stale data
* conflicting manual edits

---

# 4. Scope

These rules apply to:

* source-level metadata
* chunk-level metadata
* register rows
* metadata sidecar JSON
* QA-derived metadata
* manual corrections
* automated classifiers
* optional LLM-generated draft fields

These rules do **not** replace:

* source acquisition policy
* deduplication policy
* review workflow
* retrieval policy

They only govern **metadata provenance and metadata trust state**.

---

# 5. Provenance Model

Every tracked metadata field should carry provenance information, either:

* explicitly per field
* or via a companion provenance structure

## 5.1 Minimum provenance dimensions

Each important metadata field must be associated with:

* `value`
* `provenance_type`
* `provenance_method`
* `confidence`
* `review_status`
* `last_updated_at`
* `last_updated_by`
* `override_status`

---

# 6. Provenance Types

Allowed values for `provenance_type`:

* `extracted`
* `rule_inferred`
* `model_suggested`
* `manual_entered`
* `manual_reviewed`
* `manual_overridden`
* `imported`
* `derived`

## 6.1 Definitions

### `extracted`

Value taken directly from the source or source structure.

Examples:

* title parsed from HTML `<title>`
* pigment code read directly from product page text
* year parsed from a PDF front page

### `rule_inferred`

Value assigned by deterministic logic or heuristic rules.

Examples:

* `source_family = manufacturer` because URL domain matches known brand list
* `source_type = product_page` because page contains repeated structured product fields

### `model_suggested`

Value proposed by an LLM or probabilistic model.

Examples:

* draft summary
* suggested subdomain
* suggested limitations note
* suggested question types

### `manual_entered`

Value typed by a human where no automated value existed.

Examples:

* manually entering missing author
* manually supplying citation format

### `manual_reviewed`

An existing value was checked and confirmed by a human without changing it.

### `manual_overridden`

A previous value existed but was replaced by a human.

Examples:

* parser extracted wrong publication year
* reviewer corrected `source_type`
* reviewer replaced guessed `trust_tier`

### `imported`

Value brought in from an external structured dataset or earlier approved registry.

### `derived`

Value computed from other fields, not extracted directly.

Examples:

* `priority_score`
* `ready_for_use`
* derived age category for freshness handling

---

# 7. Provenance Methods

Allowed values for `provenance_method`:

* `regex`
* `html_parse`
* `pdf_parse`
* `table_parse`
* `keyword_rule`
* `domain_mapping`
* `filename_rule`
* `llm_draft`
* `human_entry`
* `human_review`
* `human_override`
* `import_script`
* `computed_formula`

These describe **how** the value was produced, while `provenance_type` describes **what class of origin** it belongs to.

---

# 8. Confidence Levels

Each field should also carry a confidence value.

Allowed values:

* `high`
* `medium`
* `low`
* `unknown`

## 8.1 Meaning

### `high`

Value is explicit in source or verified by human review.

### `medium`

Value is plausible and well-supported by structure or strong heuristic, but not yet human-confirmed.

### `low`

Value is tentative, ambiguous, or weakly inferred.

### `unknown`

Confidence has not yet been assessed.

---

# 9. Review Status

Every important field should also carry review state.

Allowed values:

* `unreviewed`
* `reviewed_confirmed`
* `reviewed_corrected`
* `review_pending`
* `rejected`

## 9.1 Meaning

### `unreviewed`

System-generated or imported, not checked by a human.

### `reviewed_confirmed`

Human reviewed and kept the value.

### `reviewed_corrected`

Human reviewed and changed the value.

### `review_pending`

Known to need human attention.

### `rejected`

Field value should not be used.

---

# 10. Override Status

Allowed values:

* `original`
* `superseded`
* `current_override`

## 10.1 Rule

The system must preserve prior values when a field is overridden, at least in audit history.

Do not silently replace values with no trace.

---

# 11. Field Classes

Not all metadata fields are equally sensitive. Provenance strictness should vary by field class.

## 11.1 Class A — Critical factual identity

These require the strongest provenance tracking.

Examples:

* `title`
* `author`
* `publication_year`
* `institution_or_publisher`
* `source_url`
* `source_type`
* `source_family`
* `pigment_codes`
* `binder_types`

### Rule

These fields must never be silently model-invented.

---

## 11.2 Class B — Classification / routing

Examples:

* `domain`
* `subdomain`
* `question_types_supported`
* `historical_period`
* `artist_or_school`
* `case_study_vs_general`

### Rule

These may be inferred or suggested, but must remain clearly marked until reviewed.

---

## 11.3 Class C — Judgment / governance

Examples:

* `trust_tier`
* `authority_score`
* `coverage_value_score`
* `density_score`
* `limitations_notes`
* `retrieval_notes`
* `ready_for_use`

### Rule

These should usually be human-reviewed before becoming operationally trusted.

---

## 11.4 Class D — Derived state

Examples:

* `priority_score`
* `chunked`
* `indexed`
* `ready_for_use` if computed from workflow states

### Rule

These may be derived automatically, but the derivation logic must be documented.

---

## 11.5 Class E — Narrative support fields

Examples:

* `summary`
* `retrieval_notes`
* `limitations_notes`
* `citation_format`

### Rule

These may be model-drafted, but must be marked as such until reviewed.

---

# 12. Required Provenance Rules by Field

## 12.1 Must be direct or manual

These fields should only be:

* extracted
* imported from trusted structured source
* manually entered
* manually reviewed/overridden

Not acceptable as model-only final values:

* `title`
* `publication_year`
* `author`
* `institution_or_publisher`
* `source_url`
* `pigment_codes`
* `binder_types`

---

## 12.2 May be rule-inferred

These can be populated by deterministic logic:

* `source_family`
* `source_type`
* `domain`
* `subdomain`
* `question_types_supported`
* `historical_period`
* `artist_or_school`

But they must remain reviewable and traceable.

---

## 12.3 May be model-suggested

These may be drafted by an LLM:

* `summary`
* `retrieval_notes`
* `limitations_notes`
* suggested `domain`
* suggested `subdomain`
* suggested `question_types_supported`

These must never overwrite reviewed factual fields.

---

## 12.4 Must be human-governed

These should not become trusted operational values without human review:

* `trust_tier`
* `authority_score`
* `coverage_value_score`
* `case_study_vs_general`
* `ready_for_use`

---

# 13. Per-Field Provenance Structure

Each important field should support a structure like this:

```json id="q6trg5"
{
  "field_name": "source_type",
  "value": "product_page",
  "provenance_type": "rule_inferred",
  "provenance_method": "domain_mapping",
  "confidence": "medium",
  "review_status": "unreviewed",
  "last_updated_at": "2026-03-08",
  "last_updated_by": "system",
  "override_status": "original",
  "notes": "Assigned because URL domain matched known manufacturer and page structure contained product metadata blocks."
}
```

---

# 14. Minimum Provenance Requirements

At minimum, the following fields must carry explicit provenance:

* `title`
* `author`
* `publication_year`
* `source_family`
* `source_type`
* `institution_or_publisher`
* `domain`
* `pigment_codes`
* `binder_types`
* `trust_tier`
* `case_study_vs_general`
* `summary`
* `ready_for_use`

These are the fields most likely to distort retrieval if provenance is unclear.

---

# 15. Rules for Automated Extraction

## 15.1 Extraction must preserve raw evidence

If the system extracts:

* a pigment code
* a year
* a title
* a publisher

it should preserve the raw snippet or source location when possible.

Examples:

* page number
* HTML selector
* regex match excerpt
* source line excerpt

This makes later QA easier.

---

## 15.2 Exact fields beat guessed fields

If the product page explicitly says `PW4`, that extracted field outranks a model suggestion or alias guess.

## 15.3 Missing is better than invented

If the field cannot be found reliably, leave it null or mark it low-confidence.

Do not fill gaps with confident-looking noise.

---

# 16. Rules for Rule-Based Inference

Rule-based inference is allowed for classification fields, but must follow these rules:

## 16.1 Rules must be documented

The logic that maps:

* URL domain
* heading keywords
* filename patterns
* vocabulary matches

to field values must be transparent and versioned.

## 16.2 Inferred values stay provisional

A rule-inferred field is not considered fully trusted until human review if it affects retrieval or governance.

## 16.3 No inference masquerading as extraction

If `source_type = product_page` was guessed from page structure, it must not be marked `extracted`.

---

# 17. Rules for LLM-Suggested Fields

LLM assistance is optional, but if used, it must be constrained.

## 17.1 Allowed use cases

LLMs may suggest:

* summaries
* limitations notes
* retrieval notes
* question type support
* possible domain/subdomain

## 17.2 Disallowed use cases without review

LLMs must not be treated as authoritative for:

* pigment codes
* publication years
* author names
* exact product identity
* trust tier
* case-study determination
* historical fact claims

## 17.3 Mark clearly

Any model-generated field must carry:

* `provenance_type = model_suggested`
* `review_status = unreviewed` until checked

---

# 18. Rules for Human Review

Human review may do one of three things:

## 18.1 Confirm

Keep the value, update:

* `provenance_type` remains original type
* `review_status = reviewed_confirmed`

## 18.2 Correct

Replace the value, update:

* `provenance_type = manual_overridden`
* `review_status = reviewed_corrected`

## 18.3 Reject

Invalidate the value:

* `review_status = rejected`

If corrected, the old value should remain in history.

---

# 19. Manual Override Rules

Manual overrides are allowed when:

* extraction is wrong
* classifier is wrong
* model suggestion is misleading
* human evidence is stronger
* source context clarifies ambiguity

## 19.1 Requirements

A manual override must record:

* old value
* new value
* who changed it
* when
* why

## 19.2 No silent correction

Every material correction must leave an audit trail.

---

# 20. Fallback Rule

If a field has multiple candidate values, prefer in this order:

1. `manual_overridden`
2. `manual_reviewed`
3. `manual_entered`
4. `extracted`
5. `imported`
6. `rule_inferred`
7. `model_suggested`
8. `derived`

This order applies unless a policy explicitly states otherwise.

---

# 21. Field Freshness Rules

Some metadata becomes stale faster than others.

## 21.1 Time-sensitive fields

These should be re-checked periodically:

* `edition_or_version`
* manufacturer-derived `publication_year` or snapshot date
* current product formulations
* product availability-related fields if later added

## 21.2 Mostly stable fields

These are usually stable after review:

* technical bulletin title
* author
* historical period labels
* pigment code in a fixed historical reference, if explicit

---

# 22. Provenance at Chunk Level

Chunk-level metadata must also carry provenance, especially for:

* `chunk_title`
* `chunk_type`
* `question_types_supported`
* `materials_mentioned`
* `case_specificity`
* `quality_flags`

## Rule

If a chunk was split automatically and then renamed or reclassified by a human, that change must also be trackable.

---

# 23. Register-Level Simplification Rule

The flat CSV register may not support full per-field provenance directly.

That is acceptable if:

* the flat register stores current operational values
* the sidecar JSON stores detailed provenance

### Rule

CSV is for operational visibility.
JSON is for full epistemic accountability.

---

# 24. Required Sidecar Structure

Every source metadata JSON should include:

* `current_values`
* `field_provenance`
* `field_history`
* `review_events`

## Suggested structure

```json id="779u4k"
{
  "source_id": "SRC-MFR-004",
  "current_values": {
    "title": "Zinc White",
    "source_type": "product_page",
    "pigment_codes": ["PW4"]
  },
  "field_provenance": {
    "title": {
      "provenance_type": "extracted",
      "provenance_method": "html_parse",
      "confidence": "high",
      "review_status": "reviewed_confirmed",
      "last_updated_at": "2026-03-08",
      "last_updated_by": "reviewer"
    },
    "source_type": {
      "provenance_type": "rule_inferred",
      "provenance_method": "domain_mapping",
      "confidence": "medium",
      "review_status": "reviewed_confirmed",
      "last_updated_at": "2026-03-08",
      "last_updated_by": "reviewer"
    },
    "pigment_codes": {
      "provenance_type": "extracted",
      "provenance_method": "regex",
      "confidence": "high",
      "review_status": "reviewed_confirmed",
      "last_updated_at": "2026-03-08",
      "last_updated_by": "reviewer"
    }
  },
  "field_history": [],
  "review_events": []
}
```

---

# 25. Review Event Model

Each review event should log:

* `event_id`
* `source_id` or `chunk_id`
* `reviewer`
* `date`
* `field_name`
* `old_value`
* `new_value`
* `action_type`
* `reason`
* `notes`

Allowed `action_type`:

* `confirm`
* `correct`
* `reject`
* `override`
* `restore`

---

# 26. Non-Negotiable Rules

## 26.1 No provenance-free critical fields

Critical fields must never exist without provenance.

## 26.2 No model-only factual truth

LLM-suggested factual fields are never final by default.

## 26.3 No silent overwrites

Corrections must preserve history.

## 26.4 No inference masquerading as extraction

The system must accurately represent how a field was obtained.

## 26.5 No reviewed badge without reviewer action

A field is not reviewed unless a human actually reviewed it.

---

# 27. Operational Use Rules

A metadata field may be used operationally in retrieval only according to its trust state.

## 27.1 Safe for direct retrieval filters

Usually acceptable if:

* extracted and high confidence
* or manually reviewed

Examples:

* pigment codes
* source family
* source type
* product brand

## 27.2 Safe for soft ranking only

Use cautiously if:

* rule-inferred
* medium confidence
* not reviewed

Examples:

* domain
* subdomain
* question type support

## 27.3 Not safe as hard truth until reviewed

Examples:

* trust tier
* case-study status
* historical period guess
* LLM-written summary

---

# 28. QA Questions for Provenance Review

Before approving a metadata record, the reviewer should be able to answer:

1. Which fields are directly extracted?
2. Which fields are inferred?
3. Which fields were suggested by a model?
4. Which fields have been manually corrected?
5. Which critical fields still lack human review?
6. Which fields are safe for retrieval filtering now?
7. Which fields should remain advisory only?

If these cannot be answered, provenance is not yet sufficient.

---

# 29. Recommended Companion Files

This policy should be followed by:

1. `field_provenance_schema.json`
2. `review_workflow.md`
3. `deduplication_policy.md`
4. `conflict_resolution_policy.md`

These make provenance rules operational.

---

# 30. Adoption Rule

This document should be treated as the canonical provenance standard for v1 of the Oil Painting Research Assistant.

No new ingestion pipeline, metadata script, or review process should be considered complete unless it preserves provenance according to this policy.
