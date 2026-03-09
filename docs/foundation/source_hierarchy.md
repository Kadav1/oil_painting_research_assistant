# Source Hierarchy v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-FND-001
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Source trust order, evidentiary role hierarchy, and source-priority rules
**Applies to:** Ingestion, metadata review, retrieval, reranking, conflict resolution, benchmark evaluation, and answer generation in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This document defines the canonical hierarchy of source types used by the Oil Painting Research Assistant.

Its purpose is to ensure that the system does not treat all sources as equally authoritative, equally generalizable, or equally suited to every question.

This hierarchy exists to help the system answer:

* which sources should generally be trusted more
* which sources are best for which kinds of questions
* how different evidence types should be combined
* how to avoid flattening product data, case studies, and broad technical references into one undifferentiated evidence pool

This document is a foundation document, not a workflow policy.
It defines the **hierarchy of source roles**, not the detailed operational steps for reviewing, deduplicating, or retrieving them.

---

# 2. Core Principle

The strongest source is not always the most useful source for every question.

A source hierarchy must do two things at once:

1. rank sources by **general evidentiary strength**
2. preserve the fact that different source types answer different question types best

For example:

* a museum conservation bulletin may be the strongest source for degradation and historical material evidence
* a manufacturer product page may be the best source for a specific modern paint’s pigment code
* a color-theory reference may be the best source for defining hue, value, and chroma
* a serious teaching text may be useful for painterly explanation without being the highest authority on material chemistry

The hierarchy must therefore be:

* **ranked**
* **scoped**
* **role-aware**

---

# 3. Foundational Rule

The assistant must never treat repeated availability as equivalent to evidentiary strength.

A source should not be elevated merely because it is:

* easier to scrape
* more common on the web
* more verbose
* more commercially visible
* more duplicated in the corpus

What matters is:

* evidence quality
* source type
* scope fit
* review state
* applicability to the user’s question

---

# 4. Canonical Source Tiers

The canonical trust hierarchy for v1 is:

| Tier | Label                        | Source Class                                                                                                                  | Default Trust Role                                                                                                          |
| ---- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1    | Highest Trust                | Museum conservation departments, technical bulletins, conservation science papers, conservation institute publications        | Strongest general authority for historical materials, technical examination, degradation, and documented paint structure    |
| 2    | Strong Reference             | Pigment encyclopedias, pigment handbooks, structured technical references, serious material reference works                   | Strong authority for pigment identity, chemistry, historical background, and broad technical properties                     |
| 3    | Practical Product Data       | Manufacturer product pages, technical data sheets, SDS/TDS, official material guides                                          | Best authority for modern product-specific facts                                                                            |
| 4    | Instructional / Interpretive | Serious atelier texts, technical teaching references, historically grounded manuals, interpretive art-history technique texts | Useful for explanation, workflow, and painterly framing, but not automatically highest authority for general material truth |
| 5    | Supplemental / Low Trust     | Blogs, casual tutorials, forums, social posts, weak unsourced web content                                                     | Not core evidence; may be used only for vocabulary discovery or limited supplemental context                                |

---

# 5. Tier Definitions

## 5.1 Tier 1 — Highest Trust

### Includes

* museum conservation departments
* collection research publications
* technical bulletins
* conservation institute publications
* peer-reviewed material or degradation studies
* historically grounded technical examination of artworks

### Primary strengths

* documented historical materials
* paint-layer structure
* binder and pigment evidence in actual works
* degradation and conservation behavior
* artist-, school-, or object-specific technical evidence
* analytical findings grounded in real objects

### Main limitations

* can be case-specific
* may not generalize universally
* may not answer modern product comparison questions directly
* can be narrow in scope

### Best use cases

* historical plausibility
* conservation risk
* degradation
* artist/workshop-specific technical questions
* documented binder/pigment use in real paintings

### Example status in answers

Often supports:

* **Historically documented**
* **Case-specific**
* **Well established**, if multiple strong sources converge

---

## 5.2 Tier 2 — Strong Reference

### Includes

* pigment encyclopedias
* pigment handbooks
* technical pigment databases
* structured material references
* chemistry-oriented art material references

### Primary strengths

* pigment identity
* composition
* general handling tendencies
* historical timeline of use
* lightfastness tendencies
* terminology clarity
* stable, general-purpose reference support

### Main limitations

* may be less precise about brand-level product behavior
* may simplify edge cases
* may not always capture modern formulation differences

### Best use cases

* “what is this pigment?”
* chemistry and terminology
* historical availability at a broad level
* general material comparison
* support for color/material explanation

### Example status in answers

Often supports:

* **Well established**
* **Historically documented**
* **Likely but context-dependent**

---

## 5.3 Tier 3 — Practical Product Data

### Includes

* manufacturer product pages
* technical data sheets
* safety data sheets
* official brand material guides
* official line-specific product specifications

### Primary strengths

* modern pigment code declarations
* current product formulation notes
* opacity/transparency statements
* vehicle/binder information
* lightfastness/permanence claims
* line-specific drying notes
* exact product identity

### Main limitations

* product-specific, not universal
* can reflect marketing language
* may omit broader conservation nuance
* may change over time
* not automatically reliable for historical claims

### Best use cases

* current product comparison
* brand/line-specific questions
* pigment code lookup for specific paints
* handling questions tied to modern commercial products

### Example status in answers

Often supports:

* **Product-specific**
* **Likely but context-dependent**

---

## 5.4 Tier 4 — Instructional / Interpretive

### Includes

* serious atelier texts
* technical painting manuals
* interpretive teaching texts
* historically grounded but non-primary method summaries
* painterly explanation sources

### Primary strengths

* practical explanation
* workflow framing
* painterly interpretation
* teaching language that helps users act on information
* bridge between chemistry/history and studio decision-making

### Main limitations

* can contain inherited studio lore
* may simplify or overgeneralize
* may present strong advice with weaker sourcing
* may blur historical reconstruction and modern teaching habit

### Best use cases

* turning technical material into painterly guidance
* explaining mixture logic
* workflow discussion
* understanding how painters talk about practice

### Example status in answers

Often supports:

* **Likely but context-dependent**
* occasionally **Historically documented** only when corroborated
* should rarely stand alone for hard factual claims

---

## 5.5 Tier 5 — Supplemental / Low Trust

### Includes

* generic blogs
* casual tutorial pages
* forums
* social media posts
* unsourced explanatory content
* weak aggregated advice pages

### Primary strengths

* vocabulary discovery
* identifying common misunderstandings
* finding common user phrasing
* surfacing candidate questions for the benchmark set

### Main limitations

* low rigor
* unclear provenance
* repeated myths
* uncontrolled scope
* weak citation value

### Best use cases

* almost never as core evidence
* optional supplemental context only
* vocabulary expansion only

### Example status in answers

Should generally **not** be primary support for user-facing technical answers.

---

# 6. Hierarchy Is Not the Same as Universality

Higher tier does not always mean “use this source first in every answer.”

A strong hierarchy must distinguish between:

* **general authority**
* **question-fit authority**

Examples:

* Tier 1 may outrank Tier 3 for general conservation truth
* Tier 3 may outrank Tier 1 for a specific current paint’s pigment code
* Tier 2 may outrank Tier 4 for defining a pigment
* Tier 4 may still be useful for explaining how a painter might practically apply the information

## Rule

The correct source is the one with the best combination of:

* trust tier
* scope fit
* question fit
* review quality
* currentness where relevant

---

# 7. Source Role Matrix

| Question Type            | Preferred Primary Tiers         | Secondary Tiers | Notes                                                                          |
| ------------------------ | ------------------------------- | --------------- | ------------------------------------------------------------------------------ |
| General pigment identity | 2                               | 1, 3            | Tier 2 usually best for broad reference; Tier 1 may add historical nuance      |
| Historical plausibility  | 1                               | 2, 4            | Avoid modern product data as primary evidence                                  |
| Conservation risk        | 1                               | 2, 3            | Tier 3 may help for exact products, but not replace broader conservation logic |
| Product comparison       | 3                               | 2, 4            | Tier 3 should dominate; Tier 2 can supply broader material context             |
| Color theory definition  | 2, specialized color references | 4               | Avoid vague blog-like explanations                                             |
| Studio handling advice   | 3, 4                            | 2, 1            | Depends whether the question is product-specific or general                    |
| Terminology              | 2                               | 3, 4            | Prefer clear, structured references                                            |
| Case-study question      | 1                               | 2               | Keep case-specific scope explicit                                              |

---

# 8. Source Hierarchy by Question Mode

## 8.1 Studio Mode

Prefer:

* Tier 3 for exact products
* Tier 4 for practical application
* Tier 2 for broader material grounding

Use Tier 1 when long-term material behavior or historically grounded nuance matters.

---

## 8.2 Conservation Mode

Prefer:

* Tier 1 first
* Tier 2 second
* Tier 3 only for product-specific caveats or formulation details

Tier 4 should not override conservation evidence.

---

## 8.3 Art History Mode

Prefer:

* Tier 1 first
* Tier 2 second
* Tier 4 only when interpretive framing is useful and clearly labeled

Tier 3 is usually secondary unless the question explicitly compares historical and modern materials.

---

## 8.4 Color Analysis Mode

Prefer:

* structured color references
* Tier 2 material references
* Tier 4 painterly explanation

Avoid letting abstract theory float free from pigment/material reality when the question is about oil paint behavior.

---

## 8.5 Product Comparison Mode

Prefer:

* Tier 3 first
* Tier 2 second
* Tier 1 only as broader technical caveat
* Tier 4 only as interpretive help

Do not answer specific product questions with only general technical advice.

---

# 9. Scope Rules

The hierarchy must always be read together with source scope.

## 9.1 Broadly general sources

These may support more general claims.

Examples:

* structured pigment reference
* stable definitional reference
* broad materials overview

## 9.2 Narrow case sources

These may be very strong but narrow.

Examples:

* one painting analysis
* one artist-specific medium study
* one restoration report

## Rule

A narrow Tier 1 source may still be less suitable for a broad claim than a broader Tier 2 reference, unless the answer explicitly preserves case-specificity.

---

# 10. Product-Specific Rule

Tier 3 sources must be treated as **product truth**, not automatically as **universal material truth**.

Examples of appropriate Tier 3 use:

* identifying pigment code for a specific paint
* comparing opacity labels across a brand line
* reporting the binder or vehicle used by a current product

Examples of inappropriate Tier 3 overreach:

* using one brand page to define the eternal chemistry of a pigment
* using one current formulation as proof of historical practice
* treating one product warning as a universal rule for all paints of that pigment

---

# 11. Case-Specific Rule

Tier 1 sources must not be automatically universalized.

If a conservation study concerns:

* one artist
* one painting
* one school
* one degradation case
* one material interaction under particular conditions

then the answer must preserve that scope.

## Rule

A case-specific Tier 1 source is strong evidence for:

* that case
* closely related cases
* broader inference only when corroborated

It is not automatic permission to universalize.

---

# 12. Historical Rule

For historical questions, the hierarchy must prioritize sources that are historically grounded.

Prefer:

* Tier 1 conservation and technical examination
* Tier 2 pigment history/reference
* Tier 4 only when clearly grounded

Avoid:

* modern product pages as primary historical evidence
* modern naming conventions as proof of historical continuity

---

# 13. Teaching and Interpretive Rule

Tier 4 sources are valuable but must remain clearly interpretive unless corroborated.

They are best used to:

* explain
* translate technical information into painterly action
* help the assistant sound useful, not merely archival

They are not best used to:

* define hard chemistry without support
* settle disputed historical claims
* replace higher-tier evidence in conflict

---

# 14. Supplemental Source Rule

Tier 5 sources may help with:

* common user wording
* question discovery
* vocabulary variation
* identifying popular misconceptions

They should not be primary support for:

* historical truth
* chemistry
* conservation risk
* product identity
* benchmark gold standards

---

# 15. Review-State Overlay

Source tier is not enough by itself.

A high-tier source with poor metadata review may still be less operationally reliable than a lower-tier source with strong reviewed metadata for a narrow question.

## Rule

Practical retrieval should consider:

* source tier
* review state
* scope fit
* citation readiness
* freshness relevance

A high-tier source does not bypass the review workflow.

---

# 16. Freshness Overlay

Freshness matters differently by source class.

## High freshness relevance

* Tier 3 manufacturer sources
* product pages
* technical sheets
* SDS/TDS

## Low freshness relevance

* Tier 1 historical technical bulletins
* stable Tier 2 references
* fixed historical and conservation publications

## Rule

Freshness should affect ranking only where the source type makes freshness materially relevant.

---

# 17. Conflict Handling Implications

When sources conflict, the hierarchy helps rank them, but does not eliminate the need for scoped reasoning.

Examples:

* Tier 3 product page vs Tier 1 conservation warning
  → both may be relevant, but at different levels

* Tier 4 teaching advice vs Tier 2 pigment reference
  → Tier 2 usually dominates factual material claims

* one Tier 1 case study vs broader Tier 2 reference
  → likely requires scope split, not winner-takes-all

## Rule

The hierarchy supports conflict resolution, but does not replace it.

---

# 18. Retrieval Implications

Retrieval and reranking should generally prefer:

* higher tiers for general technical and historical questions
* Tier 3 for exact product questions
* Tier 4 as explanatory support, not default factual authority
* Tier 5 only in controlled supplemental roles

## Rule

The hierarchy must shape ranking, not hard-code every answer.

It is a structured preference system, not a blind sorting rule.

---

# 19. Benchmark Implications

Benchmark design should reflect the hierarchy.

Examples:

* historical plausibility benchmarks should expect Tier 1 or 2 support
* product benchmarks should expect Tier 3 support
* color-theory definitions should expect structured reference support, not casual blogs
* mixed questions should expect cross-tier but scoped answers

---

# 20. Canonical Source Hierarchy Summary

## Tier 1 — Highest Trust

Best for:

* conservation
* historical technical evidence
* documented materials in actual works

## Tier 2 — Strong Reference

Best for:

* pigment identity
* technical reference
* terminology
* broad material facts

## Tier 3 — Practical Product Data

Best for:

* modern product specifics
* exact paint/line comparisons

## Tier 4 — Instructional / Interpretive

Best for:

* explanation
* practical translation
* painterly framing

## Tier 5 — Supplemental / Low Trust

Best for:

* vocabulary discovery only
* limited supplemental context

---

# 21. Non-Negotiable Rules

## 21.1 No flattening

Different source types must not be treated as interchangeable.

## 21.2 No product universalization

Tier 3 does not automatically define universal truth.

## 21.3 No case universalization

Tier 1 case studies remain scoped unless broader support exists.

## 21.4 No convenience bias

Availability and repetition do not equal authority.

## 21.5 No low-trust creep

Tier 5 sources must not quietly become core evidence.

---

# 22. Minimum QA Questions

Before approving hierarchy-aware behavior, the reviewer should be able to answer:

1. Does this source sit in the correct tier?
2. Is this source being used for the right kind of question?
3. Is a narrow source being generalized too broadly?
4. Is a product source being used too universally?
5. Is a teaching source being treated as stronger than it should be?
6. Does the hierarchy improve truthfulness rather than just ranking neatness?

If not, hierarchy use is not mature enough.

---

# 23. Recommended Companion Documents

This foundation document works together with:

1. `docs/policies/source_acquisition_policy.md`
2. `docs/policies/conflict_resolution_policy.md`
3. `docs/policies/retrieval_policy_v1.md`
4. `docs/policies/review_workflow.md`
5. `docs/foundation/metadata_schema.md`
6. `docs/foundation/controlled_vocabulary.md`

---

# 24. Adoption Rule

This document should be treated as the canonical source hierarchy for v1 of the Oil Painting Research Assistant.

All ingestion, review, retrieval, reranking, benchmarking, and answer-generation logic should remain compatible with this hierarchy unless an explicit later version supersedes it.

---
