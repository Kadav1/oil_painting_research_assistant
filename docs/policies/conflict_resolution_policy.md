# Conflict Resolution Policy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-004
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Source conflict handling, evidentiary disagreement, and answer-resolution rules
**Applies to:** All retrieval, synthesis, citation, evaluation, and answer-generation behavior in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This policy defines how the Oil Painting Research Assistant must detect, represent, and resolve conflicts between sources, metadata, versions, and evidence types.

Its purpose is to prevent the system from:

* flattening disagreement into fake certainty
* averaging incompatible claims into misleading summaries
* treating product-specific data as if it overrides broader technical evidence
* treating case studies as if they cancel general references
* hiding uncertainty when evidence is mixed
* giving overconfident answers where the corpus is genuinely divided or scoped

This policy applies to:

1. **source-to-source conflicts**
2. **version conflicts**
3. **product-vs-general conflicts**
4. **case-study-vs-general conflicts**
5. **historical-vs-modern conflicts**
6. **metadata classification conflicts**
7. **retrieval-time and answer-time conflict framing**

---

# 2. Core Principle

When sources disagree, the assistant must not force a single smooth answer unless the evidence actually supports one.

The goal is not to eliminate conflict.
The goal is to make conflict:

* visible
* scoped
* ranked
* explained
* useful

A truthful assistant should often say:

* these sources are talking about different things
* these sources differ by scope or version
* these sources are both partly right in different contexts
* this question does not have one flat answer
* the strongest evidence points one way, but there are caveats

---

# 3. Policy Objectives

This policy is designed to achieve seven things:

## 3.1 Preserve epistemic honesty

Do not hide disagreement.

## 3.2 Preserve source distinctions

Do not let one source type erase another source type’s role.

## 3.3 Protect contextual meaning

Resolve conflicts based on scope, not only rank.

## 3.4 Improve answer quality

Make answers more precise, less falsely absolute.

## 3.5 Improve retrieval decisions

Help the system select evidence that matches the question’s actual frame.

## 3.6 Improve evaluation

Allow benchmarks to detect whether the system handled disagreement properly.

## 3.7 Improve governance

Make conflict handling consistent and auditable.

---

# 4. What Counts as a Conflict

A conflict exists when two or more records, sources, chunks, or metadata values are materially incompatible in a way that could change:

* the answer
* the ranking
* the interpretation
* the citation choice
* the user’s action

Conflict does **not** require total contradiction. It includes:

* direct contradiction
* scope mismatch
* terminology mismatch
* temporal version mismatch
* evidentiary-level mismatch
* strong emphasis mismatch

---

# 5. Types of Conflict

Allowed conflict categories:

* `direct_factual_conflict`
* `scope_conflict`
* `version_conflict`
* `product_vs_general_conflict`
* `case_vs_general_conflict`
* `historical_vs_modern_conflict`
* `classification_conflict`
* `terminology_conflict`
* `interpretive_conflict`
* `confidence_conflict`
* `citation_conflict`

---

## 5.1 Definitions

### `direct_factual_conflict`

Two sources make materially incompatible factual claims.

Example:
One source says a product uses one pigment code, another says it uses another.

---

### `scope_conflict`

Sources appear to disagree, but are actually speaking at different levels.

Example:
A conservation case study on one painting vs a general pigment handbook.

---

### `version_conflict`

Different versions of a source or product page contain different data.

Example:
Older product page vs newer product page with revised formulation or wording.

---

### `product_vs_general_conflict`

A brand-specific claim appears to conflict with broader material science or technical guidance.

Example:
Manufacturer markets a paint as stable or safe in practice, while conservation literature describes risks in broader contexts.

---

### `case_vs_general_conflict`

A specific historical/technical case study conflicts with or complicates a general reference.

Example:
A specific analyzed painting used walnut in a context where broad teaching says linseed was typical.

---

### `historical_vs_modern_conflict`

A historical claim conflicts with modern practice or product assumptions.

Example:
Modern paint naming implies a historical continuity that the historical record does not support.

---

### `classification_conflict`

Metadata disagreement.

Example:
One workflow labels a source as `technical_bulletin`, another as `educational_reference`.

---

### `terminology_conflict`

Different sources use different names for related or partially overlapping materials.

Example:
Flake white, Cremnitz, lead white, and product-line marketing labels.

---

### `interpretive_conflict`

Sources agree on facts but disagree on interpretation.

Example:
Different teaching texts explain the same historical practice in different ways.

---

### `confidence_conflict`

Two metadata records or source framings differ in confidence or certainty level.

---

### `citation_conflict`

Multiple possible citation targets exist, and it is unclear which one should be treated as primary.

---

# 6. Conflict Priority Principle

Not all conflicts are equal.

The system should prioritize conflicts that affect:

1. factual correctness
2. user safety or material consequence
3. source ranking
4. historical plausibility
5. retrieval interpretation
6. citation accuracy

A disagreement about wording is less important than a disagreement about pigment identity, brittleness risk, or historical availability.

---

# 7. General Resolution Order

When a conflict is detected, resolve it in this order:

1. identify the conflict type
2. determine whether it is real or only apparent
3. determine scope and context
4. determine source types involved
5. determine trust tier and review state
6. determine freshness relevance
7. decide whether:

   * one source should dominate
   * both should remain visible
   * the answer should present a split view
8. label the conflict explicitly in synthesis

---

# 8. Governing Resolution Principle

The assistant must prefer:

* **scoped truth** over flat truth
* **source-aware synthesis** over average blending
* **explicit uncertainty** over false consensus
* **ranked explanation** over silent suppression

---

# 9. Resolution Hierarchy

Use this resolution order unless a narrower policy overrides it.

## 9.1 Human-reviewed values beat unreviewed values

If one side of the conflict comes from reviewed metadata and the other from unreviewed inference, prefer the reviewed side for operational decisions.

## 9.2 Higher-trust evidence beats lower-trust evidence for general claims

For general material, historical, or conservation claims:

* Tier 1 beats Tier 2–5
* Tier 2 beats Tier 3–5
* Tier 3 beats Tier 4–5 for product-specific facts

## 9.3 Product-specific evidence beats general evidence for product-specific questions

If the user asks about a specific brand/product:

* manufacturer product data usually outranks broad general guidance on that product’s exact formulation
* but broader technical caveats must still be surfaced if materially relevant

## 9.4 Case-specific evidence does not cancel general evidence

A case study may refine or complicate a general claim, but should not automatically replace it universally.

## 9.5 Newer versions beat older versions when freshness matters

Applies mainly to:

* product pages
* technical sheets
* SDS/TDS
* versioned web pages

## 9.6 Older authoritative sources may still dominate in historical questions

Freshness is not inherently better for historical truth.

---

# 10. Conflict Resolution by Question Type

## 10.1 Chemistry questions

Prefer:

* conservation science
* structured technical references
* scientific papers
* reviewed manufacturer data for exact products

Do not let casual instructional simplifications override chemistry.

---

## 10.2 Product comparison questions

Prefer:

* product pages
* technical sheets
* SDS/TDS
* structured manufacturer data

But if there is a broader technical caveat, surface it as a caveat rather than ignoring it.

---

## 10.3 Historical plausibility questions

Prefer:

* museum conservation
* technical bulletins
* historical documentation
* scholarly pigment references

Do not let modern product naming or teaching shorthand rewrite historical availability.

---

## 10.4 Conservation risk questions

Prefer:

* conservation literature
* technical bulletins
* scientific papers
* then product data where relevant

Do not let product marketing flatten conservation nuance.

---

## 10.5 Color theory questions

Prefer:

* structured color references
* serious technical teaching sources
* pigment/material evidence when practical

Do not over-abstract away from pigment behavior if the question is painterly.

---

## 10.6 Technique questions

Prefer:

* documented historical practice for historical questions
* practical/product data for modern workflow questions
* keep interpretive teaching clearly labeled

---

# 11. Common Conflict Patterns and How to Resolve Them

## 11.1 Manufacturer claim vs conservation warning

Example pattern:
A brand presents a paint as workable and stable in ordinary use, while conservation literature warns of brittleness or long-term concerns.

### Resolution

* do not declare one side “wrong” automatically
* separate:

  * product-specific practical guidance
  * broader conservation risk
* explain that both may be true at different levels

### Preferred answer shape

* direct answer
* “for this product, the brand says…”
* “more broadly, conservation literature raises…”
* practical takeaway with scoped caution

---

## 11.2 Case study vs handbook generalization

Example pattern:
One painting analysis shows atypical use of a binder or pigment.

### Resolution

* preserve both
* label the case study as case-specific
* keep the handbook claim as broader reference unless stronger evidence says otherwise

### Prohibited move

Do not rewrite a general historical pattern into an absolute exception based on one analyzed case.

---

## 11.3 Older vs newer product page

Example pattern:
Pigment code or wording differs between captures.

### Resolution

* determine whether the page identity is the same
* prefer the newer reviewed version for current product questions
* retain older version for historical comparison if useful

---

## 11.4 Historical term vs modern term

Example pattern:
Historical material names do not map neatly to modern product names.

### Resolution

* preserve original historical terminology
* normalize carefully using alias map
* avoid claiming equivalence where the mapping is imperfect

---

## 11.5 Teaching advice vs technical evidence

Example pattern:
Atelier guidance says “never use X,” while technical evidence is more nuanced.

### Resolution

* treat teaching advice as instructional
* privilege technical evidence for factual claims
* preserve atelier advice as a workflow recommendation, not universal law

---

# 12. Metadata Conflicts

Conflicts can exist in metadata even when source text is fine.

Examples:

* two different `source_type` labels
* different `historical_period` assignments
* different `case_study_vs_general` values
* different `trust_tier` assignments

## Resolution order

1. manual override
2. reviewed value
3. extracted value
4. imported trusted value
5. rule-inferred value
6. model-suggested value

If unresolved, keep status as conflicted and avoid using it as a hard retrieval filter.

---

# 13. Conflict Flags

Each conflict should support fields like:

* `conflict_id`
* `conflict_type`
* `entity_type`
* `entity_ids`
* `conflict_summary`
* `resolution_status`
* `preferred_value_or_source`
* `resolution_reason`
* `reviewed_by`
* `reviewed_at`
* `requires_answer_disclosure`

Allowed `resolution_status`:

* `open`
* `review_pending`
* `resolved_prefer_one`
* `resolved_keep_both`
* `resolved_scope_split`
* `rejected_as_not_real`

---

# 14. Answer-Time Disclosure Rule

Some conflicts must be disclosed in the answer, not merely resolved internally.

The assistant should surface conflict when:

* the disagreement materially affects the answer
* the difference changes practical advice
* the disagreement reflects genuine expert uncertainty
* the answer would otherwise overstate certainty
* the user asks a question where nuance matters

The assistant may resolve internally without explicit disclosure when:

* the conflict is only about formatting
* the conflict is between reviewed and clearly wrong unreviewed metadata
* the conflict is version noise with no substantive effect
* one source is clearly outdated and irrelevant for the user’s framing

---

# 15. Disclosure Labels

When conflict is exposed in answers, preferred internal labels are:

* **Well established**
* **Historically documented**
* **Product-specific**
* **Case-specific**
* **Likely but context-dependent**
* **Mixed evidence**
* **Uncertain**

These labels help prevent false certainty.

---

# 16. Rules for “Prefer One” Resolution

A conflict may be resolved by preferring one side when:

* one source is clearly higher tier and equally on-point
* one value is human-reviewed and the other is not
* one version is clearly superseded
* one source is authoritative and the other is derivative
* one conflict is only apparent and scope clarifies it

### Requirement

The reason must be recorded.

---

# 17. Rules for “Keep Both” Resolution

A conflict should remain visible when:

* both sources are authoritative in their own scope
* one is product-specific and one is broader
* one is historical and one is modern
* one is case-specific and one is general
* both represent meaningful interpretive disagreement

### Requirement

The answer must avoid collapsing them into fake consensus.

---

# 18. Rules for “Scope Split” Resolution

This is often the best resolution.

Use `resolved_scope_split` when:

* the sources are both valid but differently scoped
* the disagreement is actually contextual
* the correct answer is “it depends on what you mean”

Examples:

* current product vs long-term conservation risk
* one artist’s documented practice vs workshop general trend
* formal color theory vs pigment-specific studio behavior

---

# 19. Retrieval-Time Conflict Handling

Conflict handling begins before answer generation.

If retrieved evidence contains unresolved conflict:

* retain both sides if both are materially relevant
* avoid flooding context with one side only
* include metadata describing conflict type or case specificity
* prefer reviewed chunks
* ensure diversity across source types

Do not let the retriever silently erase one side if both are necessary for truthful synthesis.

---

# 20. Reranking and Conflict

Reranking should not be designed to eliminate meaningful disagreement.

Instead, reranking should:

* reduce low-quality contradictions
* preserve high-quality conflicting evidence when relevant
* prioritize better-scoped evidence
* reduce duplicate contradiction from same cluster
* keep one high-value chunk from each necessary side when appropriate

---

# 21. Citation Rules in Conflicted Answers

If both sides are surfaced, both sides should be citable.

Rules:

* cite the actual source of each claim
* do not cite only one side while paraphrasing the other
* do not imply corroboration where there is disagreement
* if one side is product-specific, citation should make that clear
* if one side is case-specific, citation choice should preserve that scope

---

# 22. Conflict Review Workflow

## Step 1 — Detection

Conflict detected by:

* metadata comparison
* version comparison
* retrieval inspection
* benchmark failure
* reviewer observation

## Step 2 — Classification

Assign conflict type.

## Step 3 — Context check

Determine:

* question frame
* source types
* trust tiers
* version/freshness relevance
* scope

## Step 4 — Decision

Choose:

* prefer one
* keep both
* scope split
* reject as not a real conflict

## Step 5 — Record

Log:

* decision
* reason
* reviewer
* date
* whether answer disclosure is required

---

# 23. Non-Negotiable Rules

## 23.1 No fake consensus

The system must not smooth real disagreement into one neat sentence unless the evidence supports that.

## 23.2 No product flattening

Brand/product data must not overwrite broader material science outside its scope.

## 23.3 No case-study universalization

Specific observed cases remain specific unless broader evidence supports generalization.

## 23.4 No review-free hard resolution

Important conflicts should not be operationally resolved only by weak inference.

## 23.5 No one-source domination by convenience

Ease of capture must not decide truth.

## 23.6 No hiding material uncertainty

If the difference matters, the user should not be given false certainty.

---

# 24. QA Questions for Conflict Review

Before resolving a conflict, the reviewer should be able to answer:

1. Is this a real conflict or only a scope mismatch?
2. Which source types are involved?
3. Does freshness matter here?
4. Is one side product-specific, case-specific, or historically scoped?
5. Is one side clearly stronger for this exact question?
6. Should the answer prefer one side, keep both, or split by scope?
7. Does the user need to see the disagreement explicitly?

If these cannot be answered, the conflict should remain open.

---

# 25. Operational Checklist

## Detection

* [ ] Conflict identified
* [ ] Entities logged
* [ ] Conflict type assigned

## Assessment

* [ ] Scope checked
* [ ] Source tiers checked
* [ ] Review states checked
* [ ] Version relevance checked
* [ ] Freshness relevance checked

## Resolution

* [ ] Prefer one / keep both / scope split selected
* [ ] Reason recorded
* [ ] Disclosure need decided
* [ ] Citation implications checked

## Finalization

* [ ] Conflict record stored
* [ ] Retrieval logic updated if needed
* [ ] Evaluation notes updated if needed

---

# 26. Recommended Outputs

This policy should be supported by:

1. `conflict_record_schema.json`
2. `conflict_review_log.csv`
3. `open_conflicts_report.json`
4. `answer_labeling_standard.md`

These make conflict handling operational and inspectable.

---
