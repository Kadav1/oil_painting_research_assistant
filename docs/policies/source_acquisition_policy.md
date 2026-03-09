# Source Acquisition Policy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-001
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Corpus intake and source admission policy
**Applies to:** All source collection for the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This policy defines how sources are selected, admitted, recorded, and prepared for inclusion in the Oil Painting Research Assistant corpus.

Its purpose is to ensure that the knowledge base is:

* trustworthy
* consistent
* auditable
* legally and practically manageable
* useful for retrieval and evaluation
* resistant to source drift and low-quality accumulation

This policy governs the **intake stage** only. It does not replace later policies for:

* deduplication
* conflict resolution
* retrieval
* reranking
* benchmark scoring
* licensing interpretation
* review workflow

Those should remain separate documents.

---

# 2. Core Principle

The system must not become “large.” It must become **selective**.

A source is not admitted because it exists.
A source is admitted because it improves the corpus in a way that is:

* relevant
* reliable
* distinguishable
* retrievable
* reviewable

The default posture is:

* **curate first**
* **admit selectively**
* **label uncertainty**
* **preserve provenance**
* **avoid silent contamination**

---

# 3. Policy Objectives

This policy is designed to achieve six things:

## 3.1 Protect source quality

Prevent weak, repetitive, or misleading material from entering the corpus.

## 3.2 Preserve source distinctions

Ensure that conservation papers, pigment references, product pages, and teaching texts are not treated as interchangeable.

## 3.3 Standardize intake

Make every source pass through the same minimum process.

## 3.4 Support later retrieval quality

Ensure that sources are admitted with enough structure to be useful later.

## 3.5 Reduce hidden failure

Prevent problems such as:

* duplicate sources
* stale product data
* uncited historical claims
* case studies treated as universal
* forum myths entering the corpus as if they were evidence

## 3.6 Enable auditability

Every source in the system must be traceable:

* where it came from
* why it was included
* what type of source it is
* what level of trust it carries
* whether it has been reviewed

---

# 4. In-Scope Source Families

The following source families are allowed in the corpus.

## 4.1 Museum conservation

Examples:

* technical bulletins
* collection research pages
* conservation department publications
* analytical case studies

**Primary value:** high-trust evidence about historical materials, paint structure, degradation, and technical examination.

---

## 4.2 Pigment reference

Examples:

* pigment encyclopedias
* structured pigment entries
* technical pigment reference works
* chemistry-centered pigment databases

**Primary value:** pigment identity, chemistry, history, lightfastness tendencies, material properties.

---

## 4.3 Manufacturer

Examples:

* product pages
* technical data sheets
* safety data sheets
* official brand material guides

**Primary value:** modern product-specific facts such as pigment codes, vehicle oils, opacity, drying notes, permanence claims.

---

## 4.4 Color theory

Examples:

* structured color-order system references
* formal educational references
* technical color education sources

**Primary value:** stable conceptual frameworks for hue, value, chroma, notation, and color relationships.

---

## 4.5 Historical practice

Examples:

* art-history technique texts
* historically grounded atelier manuals
* method surveys tied to sources or traditions

**Primary value:** documented or well-argued historical practice and workflow interpretation.

---

## 4.6 Scientific paper

Examples:

* peer-reviewed studies
* conservation/material science papers
* chemistry or degradation studies relevant to oil painting

**Primary value:** experimental or analytical evidence around materials behavior.

---

# 5. Out-of-Scope or Restricted Sources

The following are excluded by default unless explicitly approved.

## 5.1 Casual web sources

Examples:

* generic blogs
* personal websites
* unsourced tutorials
* listicles
* affiliate content

**Default status:** excluded

Reason:
They often restate conventional lore without traceable evidence.

---

## 5.2 Forums and social media

Examples:

* Reddit
* Facebook groups
* Instagram posts
* comment threads
* Discord screenshots

**Default status:** excluded

Exception:
May be used only for vocabulary discovery or question harvesting, not as evidentiary sources.

---

## 5.3 Video-only material

Examples:

* YouTube videos
* TikTok clips
* reels
* workshop videos without transcript or source grounding

**Default status:** excluded from evidentiary corpus

Exception:
Can be used later as a separate teaching layer if transcribed and explicitly categorized as instructional/interpretive.

---

## 5.4 AI-generated summaries without source grounding

Examples:

* autogenerated explainers
* model-written notes with no source chain
* scraped summary pages

**Default status:** excluded

---

## 5.5 Unverifiable scans or reposts

Examples:

* reposted PDFs with no publisher trace
* unattributed excerpts
* scans missing title/author/date context

**Default status:** excluded until verified

---

## 5.6 General art advice not specific to oil painting

Examples:

* vague “painting tips”
* generic creativity advice
* non-medium-specific commentary

**Default status:** excluded unless clearly useful and classifiable

---

# 6. Trust Hierarchy for Intake

All admitted sources must be assigned a provisional trust tier during intake.

## Tier 1 — Highest trust

* museum conservation
* major conservation bulletins
* conservation institute publications
* high-quality scientific material studies

## Tier 2 — Strong reference

* structured pigment references
* established technical reference works
* high-quality material encyclopedias

## Tier 3 — Practical product data

* manufacturer product pages
* official technical sheets
* SDS/TDS documents

## Tier 4 — Instructional / interpretive

* serious atelier texts
* technical teaching sources
* historical method overviews not based on primary technical analysis

## Tier 5 — Supplemental only

* low-rigor educational web content
* general explanatory articles
* vocabulary-only discovery sources

### Rule

A Tier 5 source may inform **vocabulary**, but not **core truth claims**.

---

# 7. Admission Criteria

A source should only be admitted if it meets the following minimum criteria.

## 7.1 Relevance

The source must contribute to at least one core domain:

* pigment
* binder
* medium
* conservation
* color theory
* technique
* historical practice
* product

If relevance is weak or indirect, reject it.

---

## 7.2 Source identity clarity

The source must have enough identity metadata to be tracked.

Minimum required:

* title or equivalent label
* institution/publisher or author
* URL or file origin
* source type
* source family

If the source cannot be identified, it must not be admitted.

---

## 7.3 Extractability

The source must be reasonably processable.

Questions:

* Can text be extracted cleanly?
* Are headings interpretable?
* Are tables readable?
* Are key material names preserved?

If extraction is severely broken, the source may be:

* deferred
* partially admitted
* rejected until better capture is possible

---

## 7.4 Corpus value

The source must add at least one of these:

* new coverage
* stronger authority
* better structure
* better product detail
* missing material/failure mode coverage
* historically important nuance
* retrieval usefulness

If it adds no meaningful value beyond existing sources, do not admit it.

---

## 7.5 Reviewability

A source must be reviewable by a human later.

If the source is so messy that no one can meaningfully verify its extraction or classification, it should not enter the active corpus.

---

# 8. Source Selection Priorities

When choosing what to collect next, prioritize in this order:

## Priority 1

High-authority sources covering foundational topics:

* whites
* earth pigments
* ultramarine
* drying oils
* glazing/scumbling
* cracking/sinking in
* hue/value/chroma

## Priority 2

Sources that improve comparison ability:

* manufacturer pages
* technical sheets
* structured pigment references

## Priority 3

Sources that improve historical specificity:

* school- or period-specific technical studies

## Priority 4

Sources that expand rare materials or edge cases:

* smalt
* verdigris
* historic lakes
* degradation case studies

---

# 9. Intake Scoring Model

Before admission, each candidate source should receive a provisional score.

## 9.1 Scoring dimensions

### Authority

How reliable is the publisher/source class?

Score:

* 5 = museum/conservation institute/peer-reviewed technical source
* 4 = structured technical reference
* 3 = reputable official manufacturer
* 2 = serious instructional source
* 1 = weak general source

### Coverage Value

How much does this improve the corpus?

Score:

* 5 = fills major gap
* 4 = strong useful addition
* 3 = useful but not essential
* 2 = marginal
* 1 = redundant or weak

### Extractability

How cleanly can it be processed?

Score:

* 5 = highly structured
* 4 = mostly clean
* 3 = usable with cleanup
* 2 = difficult
* 1 = poor

### Density

How much useful signal per page/document?

Score:

* 5 = dense technical value
* 4 = mostly high-value
* 3 = mixed
* 2 = sparse
* 1 = mostly low-value

## 9.2 Priority score

Recommended formula:

`priority_score = authority + coverage_value + extractability + density`

## 9.3 Use of score

The score is a prioritization aid, not an automatic admission rule.

A high score supports intake priority.
A low score supports rejection or deferment.

---

# 10. Admission Status Types

Every source candidate must be assigned one of the following statuses:

* `candidate`
* `approved_for_capture`
* `captured`
* `normalized`
* `metadata_drafted`
* `qa_pending`
* `approved_for_chunking`
* `rejected`
* `deferred`
* `superseded`

---

# 11. Intake Workflow

Every source must pass through this flow.

## Step 1 — Discovery

The source is identified as potentially useful.

Required outputs:

* provisional title
* source URL or origin
* source family guess
* provisional relevance note

---

## Step 2 — Registration

The source is added to the Source Register before major processing.

Required outputs:

* `source_id`
* basic identity fields
* provisional trust tier
* provisional domain/subdomain
* intake status = `candidate`

---

## Step 3 — Pre-Admission Review

The source is quickly checked for:

* scope fit
* obvious duplication
* publisher clarity
* obvious low quality
* copyright/storage concerns

Decision:

* approve for capture
* defer
* reject

---

## Step 4 — Capture

The raw source is acquired and stored.

Required outputs:

* raw file saved
* URL preserved
* capture date recorded
* capture method recorded
* raw filename standardized

---

## Step 5 — Normalization

The source is converted to clean text/markdown.

Required outputs:

* normalized file
* tables extracted where possible
* gross boilerplate removed
* obvious corruption flagged

---

## Step 6 — Metadata Drafting

A first metadata record is created.

Required outputs:

* source-level metadata draft
* provisional chunk-readiness status
* materials detected
* pigment codes detected
* binder/media terms detected
* summary draft
* limitations note draft

---

## Step 7 — QA Gate

A human reviewer checks:

* identity fields
* source classification
* trust tier
* extraction quality
* table integrity
* duplication risk
* admission suitability

Decision:

* approve for chunking
* revise
* reject
* defer

---

# 12. Required Minimum Fields at Admission

A source must not be admitted into the active corpus unless the following are present:

* `source_id`
* `title`
* `source_family`
* `source_type`
* `institution_or_publisher`
* `source_url` or equivalent origin record
* `capture_date`
* `raw_file_path`
* `domain`
* `trust_tier` or provisional trust tier
* `summary`
* `limitations_notes`
* `qa_reviewed`
* `ready_for_use = false` until approved

If these are missing, the source may remain in holding but not active use.

---

# 13. Family-Specific Admission Rules

## 13.1 Museum conservation

Must preserve:

* exact title
* institution
* year
* case-study scope
* artist/work if applicable
* whether findings are case-specific

Must not be admitted as general reference without a note on case specificity.

---

## 13.2 Pigment reference

Must preserve:

* pigment name
* chemistry identity if given
* historical usage notes if given
* lightfastness/handling caveats if present

Must not invent pigment codes unless explicitly present.

---

## 13.3 Manufacturer

Must preserve:

* brand
* line
* product name
* product page date/snapshot
* pigment code(s) if present
* product-specific nature of the data

Must not be treated as universal chemistry by default.

Older product pages may be admitted but should be marked as time-sensitive.

---

## 13.4 Color theory

Must preserve:

* concept name
* formal definition
* conceptual role

Must not be treated as material chemistry unless linked to pigment/material evidence.

---

## 13.5 Historical practice

Must preserve:

* period/school if applicable
* whether claims are documentary, interpretive, or reconstructed

Must not be admitted as strong historical evidence if sourcing is weak.

---

## 13.6 Scientific paper

Must preserve:

* paper identity
* publication date
* analytical or experimental scope
* whether results are broadly generalizable

---

# 14. Rejection Criteria

Reject a source if any of the following apply:

* no clear author/publisher/origin
* outside oil-painting scope
* mostly redundant without stronger structure or authority
* extraction is unusably poor
* severe metadata ambiguity
* unverifiable repost
* legal/storage concerns block normal use
* source is low-rigor and adds no special value
* the source encourages myth propagation more than evidence

Rejected sources should remain logged in the register with:

* rejection reason
* date
* reviewer note

Do not silently delete rejected candidates from project memory.

---

# 15. Deferred Source Rules

A source may be deferred instead of rejected if it is potentially useful but blocked by:

* poor extraction quality
* uncertain licensing/storage conditions
* missing metadata
* pending duplicate check
* pending comparison with stronger source
* need for manual transcription

Deferred sources must have:

* reason for deferment
* next action
* status review date if applicable

---

# 16. Duplicate and Supersession Handling at Intake

This policy does not replace the full deduplication policy, but intake must still perform a first-pass duplicate check.

Check for:

* same URL
* same title + same publisher
* same document in multiple formats
* same product page captured twice
* revised versions of same document

Use one of these markers:

* `unique`
* `possible_duplicate`
* `confirmed_duplicate`
* `superseded_version`
* `superseding_version`

### Rule

Do not admit multiple near-identical versions into active use without a clear reason.

---

# 17. Freshness Rules

Freshness matters differently by source type.

## 17.1 High priority for freshness

These should be checked for updates regularly:

* manufacturer product pages
* product line technical sheets
* SDS/TDS documents

## 17.2 Medium priority for freshness

These should be reviewed occasionally:

* structured educational pages
* color theory reference pages if web-maintained

## 17.3 Low priority for freshness

These are mostly stable:

* historical technical bulletins
* older conservation papers
* historical texts
* stable pigment references

### Rule

Do not reject older sources just because they are old if they remain authoritative and relevant.

---

# 18. Raw Storage Rules

Every approved-for-capture source must preserve:

* raw original file or captured representation
* standardized filename
* origin metadata
* capture date
* source register entry

Recommended separation:

* raw source
* cleaned text
* extracted tables
* metadata sidecar

Do not rely only on normalized output.
Always preserve the source form that was actually captured.

---

# 19. Legal and Usage Guardrails

This policy does not replace a full licensing policy, but intake must record:

* whether raw storage is permitted
* whether content is public web
* whether the source should be summarized only
* whether redistribution is restricted
* whether quotation should be limited

If legal status is unclear:

* admit only provisionally
* restrict downstream use until reviewed

---

# 20. Human Review Requirement

No source becomes `ready_for_use = true` without human review.

Automation may:

* capture
* normalize
* extract metadata
* suggest classifications

Automation may not be the final authority on:

* trust tier
* case-study scope
* claim-type classification
* admission approval
* rejection reason

---

# 21. Minimum QA Questions Before Approval

Before a source is approved for active use, the reviewer must be able to answer:

1. What kind of source is this?
2. Why is it in the corpus?
3. What does it add that we do not already have?
4. Is it case-specific or general?
5. Is it product-specific or broader material evidence?
6. Are the extracted fields believable?
7. Are there obvious duplication or freshness issues?
8. Is this safe to use in retrieval later?

If not, it is not ready.

---

# 22. Required Output Artifacts from Intake

A successfully admitted source should produce:

* Source Register record
* raw source file
* normalized text/markdown file
* metadata sidecar
* extraction notes if needed
* QA status record
* admission decision state

Optional:

* extracted tables
* source summary note
* candidate topic-bundle link

---

# 23. Roles and Responsibilities

## Collector / Intake Operator

Responsible for:

* discovery
* registration
* capture
* normalization
* draft metadata

## Reviewer

Responsible for:

* trust-tier confirmation
* classification confirmation
* duplicate/freshness check
* approval / rejection / deferment

## Maintainer

Responsible for:

* policy consistency
* versioning
* source-family standards
* update schedules
* corpus integrity

One person may hold multiple roles, but the roles should remain conceptually separate.

---

# 24. Policy-Level Non-Negotiables

The following rules are absolute:

## 24.1 No silent admission

Every source must be registered.

## 24.2 No anonymous truth

Every source must have traceable identity.

## 24.3 No source flattening

Product pages, museum studies, and teaching texts are not the same kind of evidence.

## 24.4 No active use without review

Draft sources are not live sources.

## 24.5 No universalizing case studies

Specific findings must remain scoped.

## 24.6 No universalizing product claims

Brand-specific product behavior is not automatically universal.

## 24.7 No low-rigor creep

Weak sources must not accumulate just because they are easy to collect.

---

# 25. Quick Intake Checklist

Use this as the operational summary.

## Discovery

* [ ] Source identified
* [ ] Scope relevance confirmed
* [ ] Basic identity visible

## Registration

* [ ] `source_id` assigned
* [ ] Register row created
* [ ] Source family assigned
* [ ] Source type assigned
* [ ] Domain assigned

## Pre-Admission Review

* [ ] Publisher/author checked
* [ ] Obvious duplicate checked
* [ ] Obvious low-value source rejected
* [ ] Freshness need noted
* [ ] Legal/storage concern noted

## Capture

* [ ] Raw saved
* [ ] URL saved
* [ ] Capture date saved
* [ ] Filename standardized

## Normalization

* [ ] Clean text created
* [ ] Tables extracted or flagged
* [ ] Obvious corruption flagged

## Metadata

* [ ] Summary drafted
* [ ] Limitations note drafted
* [ ] Materials captured
* [ ] Pigment codes captured if present
* [ ] Provisional trust tier set

## QA

* [ ] Reviewer checked source type
* [ ] Reviewer checked scope/value
* [ ] Reviewer checked case/general status
* [ ] Reviewer checked duplication risk
* [ ] Reviewer approved / deferred / rejected

---

# 26. Recommended Companion Documents

This policy should be followed by:

1. `metadata_provenance_rules.md`
2. `material_alias_map.json`
3. `deduplication_policy.md`
4. `conflict_resolution_policy.md`
5. `review_workflow.md`

These documents make the intake policy operational.

---

# 27. Adoption Rule

This policy should be treated as the canonical intake standard for v1 of the Oil Painting Research Assistant.

Any source collected after adoption should conform to this policy unless explicitly exempted and documented.

---
