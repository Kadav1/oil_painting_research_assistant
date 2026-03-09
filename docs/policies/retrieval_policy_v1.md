# Retrieval Policy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-006
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Retrieval, candidate selection, reranking, diversity, and context assembly rules
**Applies to:** All search, retrieval, reranking, context building, and answer-support behavior in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This policy defines how the Oil Painting Research Assistant must retrieve evidence from the corpus.

Its purpose is to ensure that retrieval is:

* relevant
* source-aware
* provenance-aware
* review-aware
* diversity-controlled
* conflict-capable
* citation-ready

This policy exists to prevent:

* vector-only retrieval drift
* low-trust sources outranking strong sources without reason
* product pages dominating unrelated questions
* case studies being surfaced as universal rules
* duplicate clusters flooding the answer context
* unreviewed inferred metadata being treated as hard filters
* retrieval outputs that are accurate in pieces but misleading in combination

---

# 2. Core Principle

Retrieval is not just “find similar text.”

Retrieval is the process of assembling the **right evidence for the right question**, with the right balance of:

* source tier
* scope
* question type
* review state
* diversity
* freshness
* citation readiness

The best retrieval result is not the most semantically similar chunk in isolation.
It is the set of chunks that gives the generation layer the best chance of producing a truthful, scoped, useful answer.

---

# 3. Policy Objectives

This policy is designed to achieve eight things:

## 3.1 Increase answer truthfulness

Return evidence that matches the question’s actual domain and scope.

## 3.2 Respect source hierarchy

High-value sources should generally carry more weight where appropriate.

## 3.3 Protect context quality

Avoid redundant, low-signal, or poorly scoped retrieval sets.

## 3.4 Preserve scope

Historical, product, conservation, and teaching evidence should not be blurred together without control.

## 3.5 Support nuanced answers

Allow retrieval to carry both general and contextual evidence where needed.

## 3.6 Improve citation quality

Return chunks that can be tied back to clear source identity and scope.

## 3.7 Support evaluation

Make retrieval inspectable and benchmarkable.

## 3.8 Support safe iteration

Allow experimental retrieval without silently affecting normal live behavior.

---

# 4. Retrieval Scope

This policy governs:

1. query classification
2. mode inference
3. metadata filtering
4. candidate retrieval
5. reranking
6. diversity control
7. duplicate suppression
8. conflict-aware evidence selection
9. context assembly
10. retrieval inspection and logging

It applies to:

* CLI search
* answer generation
* evaluation runs
* retrieval inspection tools
* internal testing modes

---

# 5. Core Retrieval Pipeline

The canonical retrieval pipeline is:

1. **query intake**
2. **query classification**
3. **mode inference**
4. **candidate domain selection**
5. **metadata filtering**
6. **lexical retrieval**
7. **vector retrieval**
8. **candidate merge**
9. **reranking**
10. **diversity enforcement**
11. **duplicate suppression**
12. **conflict-aware adjustment**
13. **context assembly**
14. **citation packaging**
15. **retrieval log generation**

This order should be treated as the default retrieval flow unless a narrower implementation mode requires variation.

---

# 6. Query Classification

Every query should be classified before full retrieval.

At minimum, classify for:

* `chemistry`
* `handling`
* `historical_plausibility`
* `conservation_risk`
* `product_comparison`
* `color_analysis`
* `terminology`

A query may belong to more than one class.

## 6.1 Multi-label rule

Use multi-label classification when the question clearly spans domains.

Example:
“Why does zinc white raise concerns in oil painting, and how does that compare to modern tube paints?”

This should likely activate:

* chemistry
* conservation_risk
* product_comparison

## 6.2 Uncertainty rule

If classification is uncertain, keep candidate domains broader rather than forcing a narrow false label.

---

# 7. Mode Inference

The retrieval layer should infer a likely answer mode.

Allowed modes:

* `Studio`
* `Conservation`
* `Art History`
* `Color Analysis`
* `Product Comparison`

Mode inference helps shape weighting and context balance.

## 7.1 Examples

### Studio

“What should I use instead of zinc white for faster drying?”

### Conservation

“Why is this paint film cracking?”

### Art History

“Would a 15th-century painter have used titanium white?”

### Color Analysis

“Why do my shadows go muddy?”

### Product Comparison

“Compare two modern terre verte paints.”

## 7.2 Multi-mode rule

A query may activate more than one mode. Retrieval should then preserve evidence diversity across those modes.

---

# 8. Metadata Filtering Rules

Retrieval must support metadata filtering before and after candidate retrieval.

## 8.1 Supported filters

At minimum, support:

* `source_family`
* `source_type`
* `domain`
* `subdomain`
* `question_types_supported`
* `historical_period`
* `artist_or_school`
* `materials_mentioned`
* `pigment_codes`
* `binder_types`
* `review_status`
* `case_specificity`
* `trust_tier`
* `duplicate_status`
* `approval_level`
* `citability`

## 8.2 Hard vs soft filters

### Hard filters

Use only for fields that are:

* reviewed
* structurally reliable
* operationally critical

Examples:

* approval level
* rejected status
* duplicate suppression
* indexed state
* source family in explicit user-filtered search

### Soft filters

Use as weighting inputs when fields may be inferred or not fully reviewed.

Examples:

* domain
* subdomain
* question types
* historical period guess
* artist_or_school guess

## 8.3 Rule

Do not use weakly inferred metadata as a hard exclusion unless explicitly configured.

---

# 9. Corpus Eligibility Rules

Not every indexed chunk should be eligible for normal retrieval.

## 9.1 Default live-eligible chunks

Only retrieve by default from chunks/sources that are:

* `indexed = true`
* `approved_for_retrieval = true`
* not `rejected`
* not `superseded` unless relevant
* not blocked by restriction flags

## 9.2 Testing mode

In testing or benchmark inspection mode, broader retrieval may be allowed, including:

* draft artifacts
* lower-trust material
* deferred sources
* alternate versions

This must be explicit.

---

# 10. Hybrid Retrieval Rule

The system must use **hybrid retrieval**, not vector-only retrieval.

Required components:

* lexical search
* vector search
* metadata-aware ranking
* reranking

## 10.1 Why

Lexical search is strong for:

* pigment codes
* exact product names
* historical names
* short technical phrases
* terminology questions

Vector search is strong for:

* semantically phrased questions
* paraphrased technical explanations
* broader concept matching

## 10.2 Rule

Neither lexical nor vector search may be the sole default retrieval mode for live use.

---

# 11. Lexical Retrieval Policy

Lexical retrieval should prioritize:

* exact pigment codes
* material names
* brand/product names
* named techniques
* exact historical terms
* failure-mode terms
* formal color theory terms

## 11.1 Best lexical use cases

* “PW4”
* “terre verte”
* “sinking in”
* “stand oil”
* “Van Dyck”
* “Munsell chroma”

## 11.2 Limitations

Lexical retrieval alone may miss semantically relevant paraphrases and explanatory chunks.

---

# 12. Vector Retrieval Policy

Vector retrieval should prioritize:

* semantically related explanations
* broader handling or chemistry discussion
* indirect but relevant cause/effect relationships
* interpretive discussion linked to the question

## 12.1 Best vector use cases

* “Why does this white make the film feel fragile?”
* “Why do some greens feel weak in flesh shadows?”
* “What causes muddy shadows in oils?”

## 12.2 Limitations

Vector search may over-associate broad or generic teaching text if not reranked properly.

---

# 13. Candidate Pool Construction

Build a candidate pool from both lexical and vector results.

Recommended process:

1. retrieve lexical top N
2. retrieve vector top N
3. merge by `chunk_id`
4. retain provenance and match scores
5. annotate candidate with source and metadata context

### Suggested initial defaults

* lexical N = 20
* vector N = 20
* merged candidate pool = deduplicated union

These can be tuned later.

---

# 14. Initial Weighting Rules

Before reranking, assign base weights using:

* lexical match score
* vector similarity score
* source trust tier
* review status
* approval level
* duplicate suppression state
* quality flags

## 14.1 Base preference order

All else equal, prefer chunks that are:

1. reviewed
2. approved for live use
3. from stronger source tiers
4. citation-ready
5. not duplicate-suppressed
6. high-quality extraction

---

# 15. Reranking Policy

Reranking is mandatory for live retrieval.

The reranker must consider:

* semantic relevance
* lexical relevance
* source trust tier
* metadata review state
* query-mode fit
* question-type fit
* case specificity
* source freshness where relevant
* duplicate status
* chunk quality flags
* citation readiness
* source diversity

## 15.1 Reranking must not do this

* erase meaningful conflicting evidence
* erase necessary product-specific evidence from product questions
* overreward generic explanatory prose over exact technical data
* allow same-source flooding

---

# 16. Trust-Tier Weighting Rules

Trust tier should affect ranking, but not blindly.

## 16.1 General rule

For general chemistry, historical, and conservation questions:

* Tier 1 should usually outrank lower tiers
* Tier 2 should usually outrank Tier 3–5

## 16.2 Product question exception

For exact product questions:

* Tier 3 may outrank Tier 1–2 if the question is product-specific
* but broader technical evidence may still need to appear as caveat/support

## 16.3 Teaching question exception

For explicitly instructional/atelier workflow questions:

* Tier 4 may be useful
* but should not silently replace technical evidence where factual claims are involved

---

# 17. Review-State Weighting Rules

Reviewed content should generally outrank unreviewed content.

Recommended preference order:

1. `live_allowed`
2. `retrieval_allowed`
3. `testing_only`
4. `internal_draft_only`

At field level, reviewed metadata should carry more weight than inferred or model-suggested metadata.

## Rule

Unreviewed metadata may help soft ranking, but should not dominate hard filtering.

---

# 18. Freshness Rules in Retrieval

Freshness must be applied selectively.

## 18.1 High freshness relevance

Apply recency preference to:

* manufacturer product pages
* technical data sheets
* SDS/TDS
* updated web product documentation

## 18.2 Low freshness relevance

Do not overreward recency for:

* historical technical bulletins
* archival conservation studies
* older but authoritative reference texts
* historically relevant case studies

## Rule

Freshness is contextual, not universal.

---

# 19. Case-Specificity Rules

Retrieval must distinguish between:

* `case_specific`
* `broadly_reference`
* `mixed`
* `unknown`

## 19.1 General question rule

For broad general questions, prefer:

* broadly reference chunks
* then case-specific chunks as nuance, if useful

## 19.2 Specific question rule

If the user asks about:

* a specific artist
* a specific painting
* a specific case
* a specific product version

then case-specific or version-specific evidence may be primary.

## Rule

Case-specific chunks should not dominate general questions unless the question clearly warrants them.

---

# 20. Duplicate Suppression Rules

Retrieval must respect duplicate clusters and suppression state.

## 20.1 Default rule

Do not allow multiple near-identical chunks from the same duplicate cluster into the main answer context unless comparison is required.

## 20.2 Cluster rule

Prefer the canonical member of the duplicate cluster.

## 20.3 Boilerplate rule

Heavily downweight `boilerplate_duplicate` chunks, especially in manufacturer pages.

---

# 21. Diversity Rules

High relevance is not enough. Retrieval must also preserve evidence diversity.

## 21.1 Source diversity

Avoid too many chunks from the same source.

Suggested default:

* no more than 2 chunks from same source in primary context

## 21.2 Source-family diversity

When appropriate, preserve useful variety across:

* museum conservation
* pigment reference
* manufacturer
* color theory
* historical practice

## 21.3 Role diversity

When appropriate, allow the final context to include different evidence roles:

* general technical reference
* product-specific data
* case-specific nuance
* teaching interpretation

## 21.4 Exception rule

If one source genuinely contains the best evidence for a narrow question, diversity should not force irrelevant variety.

---

# 22. Conflict-Aware Retrieval

Retrieval must preserve meaningful disagreement when relevant.

## 22.1 If conflict matters to the answer

Retain both sides if:

* both are reviewed or otherwise credible
* both are relevant to the exact question
* suppressing one side would distort truth

## 22.2 If conflict is noise

Downweight or exclude if:

* conflict comes from duplicate noise
* one side is stale and irrelevant for current framing
* one side is unreviewed weak inference against reviewed stronger evidence

## Rule

Conflict-aware retrieval is not “retrieve everything that disagrees.”
It is “retrieve the disagreement that matters.”

---

# 23. Query-Type Retrieval Guidance

## 23.1 Chemistry

Prefer:

* conservation
* scientific papers
* pigment references
* then product data if exact products are involved

## 23.2 Handling / Studio

Prefer:

* product data
* practical technical references
* then broader material guidance

## 23.3 Historical plausibility

Prefer:

* museum conservation
* historical technical studies
* pigment references
* avoid modern product noise unless explicitly asked

## 23.4 Conservation risk

Prefer:

* conservation literature
* technical bulletins
* then product caveats if relevant

## 23.5 Color analysis

Prefer:

* color theory references
* pigment/material-specific behavior
* serious teaching texts where useful

## 23.6 Product comparison

Prefer:

* product pages
* technical sheets
* structured product data
* then broader technical caveats

## 23.7 Terminology

Prefer:

* glossary/reference chunks
* structured technical entries
* short high-clarity definitional chunks

---

# 24. Context Assembly Rules

After reranking, the system must assemble a context package for generation.

## 24.1 Context assembly goals

The context should contain:

* the most relevant evidence
* enough diversity to avoid distortion
* enough citation structure to support answering
* not too much redundancy

## 24.2 Context package contents

For each selected chunk, preserve:

* chunk text
* source_id
* source title
* source type
* trust tier
* case specificity
* citation format
* page range / section path if available
* key metadata flags

## 24.3 Suggested primary context size

Use a manageable number of chunks.

Suggested default:

* 5 to 8 primary chunks for standard answers
* more only when comparison or conflict handling requires it

---

# 25. Citation Readiness Rules

Retrieval should prefer chunks with usable citation metadata where possible.

Prefer chunks with:

* clear source identity
* page or section info
* citation format
* reviewed metadata
* clear scope labeling

If a highly relevant chunk lacks perfect citation details, it may still be used, but its citation limitation should be recorded in the retrieval trace.

---

# 26. Retrieval Restrictions

A retrieved chunk may be excluded from primary context if it is:

* rejected
* superseded and not relevant
* heavily duplicate-suppressed
* marked not safe for live use
* unusably low quality
* citation-fatally broken for a citation-critical workflow
* severely misaligned with query scope

Do not exclude merely because the chunk is nuanced or conflicts with another strong source.

---

# 27. Experimental Retrieval Modes

The system may support non-default modes such as:

* `high_recall`
* `strict_reviewed_only`
* `product_focused`
* `historical_focused`
* `conflict_exploration`
* `benchmark_debug`

These modes must be explicit and never silently replace default live retrieval behavior.

---

# 28. Retrieval Logging Requirements

Each retrieval run should produce a structured log containing at least:

* query text
* query classification
* inferred mode(s)
* filters applied
* lexical candidates
* vector candidates
* merged candidate pool
* final reranked results
* selected primary context
* excluded candidates and why
* duplicate suppression decisions
* conflict notes if applicable

This is necessary for debugging and evaluation.

---

# 29. Retrieval Failure Conditions

A retrieval run should be flagged for inspection if:

* all top results come from one source unnecessarily
* all top results come from one source family unnecessarily
* unreviewed chunks dominate live retrieval
* product chunks dominate a historical question
* historical chunks dominate a product question
* duplicate clusters dominate context
* no citation-ready chunk appears for a citation-critical query
* relevant reviewed chunks were skipped for weaker draft chunks
* meaningful conflict was erased
* retrieval set is semantically broad but operationally useless

---

# 30. Minimum QA Questions for Retrieval Review

Before approving retrieval behavior, the reviewer should be able to answer:

1. Did retrieval match the question’s real domain?
2. Did source-tier weighting behave appropriately?
3. Did review-state handling work correctly?
4. Was diversity adequate without becoming noisy?
5. Were duplicates suppressed properly?
6. Were case-specific chunks scoped correctly?
7. Did product freshness matter appropriately?
8. Was the final context useful for truthful answer generation?

If these cannot be answered confidently, retrieval behavior is not mature enough.

---

# 31. Operational Checklist

## Classification

* [ ] Query classified
* [ ] Mode inferred
* [ ] Candidate domains selected

## Filtering

* [ ] Hard filters applied appropriately
* [ ] Soft filters used appropriately
* [ ] Approval state respected

## Retrieval

* [ ] Lexical results gathered
* [ ] Vector results gathered
* [ ] Candidate pool merged

## Reranking

* [ ] Trust-tier effects checked
* [ ] Review-state effects checked
* [ ] Query-fit checked
* [ ] Duplicate suppression applied

## Context assembly

* [ ] Diversity checked
* [ ] Conflict-aware evidence preserved if needed
* [ ] Citation-ready context assembled
* [ ] Retrieval log stored

---

# 32. Recommended Outputs

This policy should be supported by:

1. `retrieval_trace_schema.json`
2. `reranking_weights_config.json`
3. `retrieval_debug_report.json`
4. `context_package_schema.json`
5. `retrieval_failure_log.csv`

These make retrieval inspectable and tunable.

---
