# Answer Labeling Standard v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-POL-007
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Epistemic labeling and answer-status framing for generated responses
**Applies to:** All user-facing answers, benchmark answers, retrieval-supported synthesis, and evaluation outputs in the Oil Painting Research Assistant knowledge base

---

# 1. Purpose

This document defines how the Oil Painting Research Assistant should label the **status of claims** in its answers.

Its purpose is to prevent the system from presenting all statements with the same apparent certainty, even when the underlying evidence differs in:

* trust level
* scope
* source type
* product specificity
* historical specificity
* conflict state
* review state
* uncertainty level

This standard exists so the assistant can distinguish between:

* broadly established material facts
* historically documented practices
* case-specific findings
* product-specific claims
* likely but context-dependent conclusions
* genuinely uncertain or mixed-evidence areas

Without a labeling standard, answers can sound smoother and more certain than the evidence actually supports.

---

# 2. Core Principle

Not every true-sounding statement has the same evidentiary status.

The assistant must not flatten:

* technical references
* historical documentation
* product specifications
* case studies
* teaching interpretations
* unresolved conflicts

into the same voice of certainty.

The system should make it possible, either explicitly in the answer or internally in the answer logic, to tell the user:

* what is well established
* what is historically evidenced
* what is specific to a product
* what is specific to a case
* what is a practical inference
* what is uncertain or contested

---

# 3. Policy Objectives

This standard is designed to achieve seven things:

## 3.1 Improve truthfulness

Make the certainty level of the answer match the evidence.

## 3.2 Preserve scope

Ensure that product data, case studies, and broader technical claims are not blurred together.

## 3.3 Reduce overclaiming

Prevent the assistant from sounding more certain than the source base permits.

## 3.4 Improve usefulness

Help the user understand what kind of answer they are getting.

## 3.5 Support consistent writing

Give the generation layer a stable set of answer-status categories.

## 3.6 Support evaluation

Allow benchmark review to inspect whether the assistant labeled evidence appropriately.

## 3.7 Support governance

Make epistemic framing inspectable and reviewable rather than stylistic and implicit only.

---

# 4. What Answer Labels Are For

Answer labels are used to describe the **status of a claim**, not its tone.

They help answer questions like:

* Is this a broad technical point or a brand-specific statement?
* Is this documented historically or only commonly taught?
* Is this based on one case study or multiple general references?
* Is this a stable fact or a context-dependent conclusion?
* Is the evidence split or uncertain?

These labels do **not** replace:

* citations
* full explanations
* caveats
* conflict resolution
* provenance

They complement those systems.

---

# 5. Canonical Label Set

The standard label set for v1 is:

1. **Well established**
2. **Historically documented**
3. **Product-specific**
4. **Case-specific**
5. **Likely but context-dependent**
6. **Mixed evidence**
7. **Uncertain**

These labels should be treated as canonical for v1.

---

# 6. Label Definitions

## 6.1 Well established

### Meaning

The claim is broadly supported by high-quality technical, conservation, or reference evidence and is not heavily dependent on one narrow case or one product line.

### Typical evidence pattern

* multiple strong sources agree
* or one strong source states a stable technical fact clearly
* low conflict
* broad applicability

### Examples of suitable use

* hue, value, and chroma are distinct concepts
* titanium white is a modern pigment, not a 15th-century one
* product names and pigment identity are not always the same thing

### Not suitable for

* one-off case-study outcomes
* exact product behavior
* disputed historical generalizations

### Writing guidance

Use when the answer can be direct and clear without pretending there are no nuances at all.

---

## 6.2 Historically documented

### Meaning

The claim is supported by historical or conservation evidence tied to documented materials, practices, or period use.

### Typical evidence pattern

* museum conservation
* historical technical analysis
* pigment history references
* artist/workshop documentation

### Examples of suitable use

* verdigris was historically used
* lead white was historically important in European oil painting
* certain layer practices are documented in specific schools or periods

### Not suitable for

* modern product claims
* modern teaching advice without historical support
* inferred historical claims with weak sourcing

### Writing guidance

Use when the assistant is answering a historical plausibility or documented-practice question.

---

## 6.3 Product-specific

### Meaning

The claim applies to a specific modern paint, product, brand, line, or formulation, not necessarily to the whole material category in every context.

### Typical evidence pattern

* product page
* technical data sheet
* SDS/TDS
* official manufacturer guidance

### Examples of suitable use

* this paint uses PW4
* this specific line lists a certain drying behavior
* this brand describes a paint as semi-opaque

### Not suitable for

* broad historical claims
* universal material chemistry claims
* blanket rules about all paints with the same pigment code

### Writing guidance

Always preserve the product frame. Do not let a product-specific statement sound universal unless corroborated more broadly.

---

## 6.4 Case-specific

### Meaning

The claim is supported by evidence from a specific painting, artist, document, restoration campaign, or technical case, and should remain scoped to that case unless broader support exists.

### Typical evidence pattern

* technical bulletin on one artwork
* conservation case study
* one artist-specific medium analysis
* one historically situated example

### Examples of suitable use

* a particular painting showed a certain binder usage
* a specific study found a certain degradation pattern in that case
* one documented workshop example showed a certain material combination

### Not suitable for

* universal rules
* broad technical generalizations
* brand-level product comparisons

### Writing guidance

Use when the evidence is strong but narrow. The answer should preserve that narrowness.

---

## 6.5 Likely but context-dependent

### Meaning

The claim is plausible and useful, but depends materially on context such as:

* formulation
* proportion
* workflow
* period
* support
* layer structure
* product line
* exact pigments involved

### Typical evidence pattern

* partial agreement across sources
* strong practical pattern with important caveats
* good general guidance, but not absolute

### Examples of suitable use

* burnt umber often dries relatively quickly, though formulation matters
* complementary mixtures often reduce chroma, though results depend on pigments and ratios
* walnut oil may be preferred in some contexts, but not universally

### Not suitable for

* highly stable core facts
* truly unresolved or contradictory evidence
* one-off case studies unless generalized carefully

### Writing guidance

This is often the best label for painterly advice that is real and useful but not absolute.

---

## 6.6 Mixed evidence

### Meaning

The evidence base contains meaningful disagreement, tension, or competing interpretations that materially affect the answer.

### Typical evidence pattern

* credible sources disagree
* product data and conservation data point in different directions
* historical interpretation is split
* multiple reviewed sources support different scopes or conclusions

### Examples of suitable use

* zinc white guidance may differ depending on whether the focus is product handling or long-term conservation framing
* some historical practices may be interpreted differently by different technical or pedagogical sources

### Not suitable for

* simple definitional questions
* clearly resolved technical facts
* cases where only one strong source exists and no real disagreement is present

### Writing guidance

Use when the answer should not be forced into a single neat rule. The assistant should explain the split.

---

## 6.7 Uncertain

### Meaning

The available evidence is limited, ambiguous, under-reviewed, or insufficient to support a strong conclusion.

### Typical evidence pattern

* low corpus coverage
* incomplete metadata
* unresolved terminology
* insufficient reviewed sources
* unclear historical mapping
* unresolved product/version uncertainty

### Examples of suitable use

* ambiguous historical terminology
* incomplete current product formulation comparison
* uncertain equivalence between two names without stronger source support

### Not suitable for

* avoiding clear answers when evidence is actually strong
* replacing careful reasoning with vagueness

### Writing guidance

Use sparingly and honestly. “Uncertain” should signal a real evidence boundary, not stylistic hesitation.

---

# 7. Label Selection Rules

The assistant should choose the label based on:

1. source type
2. source tier
3. scope of evidence
4. conflict state
5. freshness relevance
6. review state
7. generalizability of the claim

## Rule

The label describes the **claim as used in the answer**, not merely the source it came from.

A product page may support:

* a **Product-specific** claim directly
  but a cross-source synthesis built partly from it might become:
* **Likely but context-dependent**

---

# 8. Label Priority Rules

If more than one label could apply, use this priority logic:

## 8.1 Scope-specific labels take precedence over general confidence labels

Prefer:

* **Product-specific**
* **Case-specific**
* **Historically documented**

before defaulting to:

* **Well established**
* **Likely but context-dependent**

Example:
If a claim is well supported but only for one product, use **Product-specific**, not **Well established**.

## 8.2 Conflict labels override smooth certainty labels

If credible disagreement materially affects the answer, prefer:

* **Mixed evidence**
  or
* **Uncertain**

rather than forcing:

* **Well established**

## 8.3 Uncertainty should not replace strong scoped labels unnecessarily

If a claim is clearly documented for a case, use:

* **Case-specific**
  not:
* **Uncertain**

if the real issue is scope, not doubt.

---

# 9. Labeling by Source Pattern

## 9.1 Multiple high-quality general technical sources agree

Preferred label:

* **Well established**

## 9.2 Historical and conservation sources support a period/material claim

Preferred label:

* **Historically documented**

## 9.3 Manufacturer source is central to the claim

Preferred label:

* **Product-specific**

## 9.4 One technical study supports a narrow finding

Preferred label:

* **Case-specific**

## 9.5 Several sources support a useful pattern but with important variability

Preferred label:

* **Likely but context-dependent**

## 9.6 Strong sources disagree in materially relevant ways

Preferred label:

* **Mixed evidence**

## 9.7 Source support is weak, incomplete, or unresolved

Preferred label:

* **Uncertain**

---

# 10. Labeling by Question Type

## 10.1 Chemistry questions

Often labeled:

* Well established
* Likely but context-dependent
* Mixed evidence

## 10.2 Historical plausibility questions

Often labeled:

* Historically documented
* Case-specific
* Uncertain

## 10.3 Product questions

Often labeled:

* Product-specific
* Likely but context-dependent

## 10.4 Conservation questions

Often labeled:

* Well established
* Case-specific
* Mixed evidence

## 10.5 Color theory questions

Often labeled:

* Well established
* Likely but context-dependent

## 10.6 Terminology questions

Often labeled:

* Well established
* Uncertain, if historical term mapping is weak

---

# 11. Labeling by Answer Structure

When possible, the label should appear at the **claim level** or **section level**, not necessarily as one global label for the whole answer.

A single answer may contain multiple label types.

Example:

* general definition = **Well established**
* historical example = **Historically documented**
* brand-specific note = **Product-specific**
* practical recommendation = **Likely but context-dependent**

## Rule

Do not force one label to cover an entire answer if the answer contains multiple evidence roles.

---

# 12. Global vs Local Labeling

## 12.1 Global answer label

Optional, used when the whole answer clearly has one dominant status.

Example:
A short terminology answer may simply be **Well established** overall.

## 12.2 Local claim labels

Preferred for complex answers.

Example:

* “This is historically documented.”
* “That part is product-specific.”
* “The broader conclusion is likely but context-dependent.”

## Rule

For nuanced questions, local labeling is preferred over one oversimplified global label.

---

# 13. Relationship to Citations

Labels do not replace citations.

A labeled claim should still be supported by:

* source identity
* retrieval evidence
* appropriate scope
* citation-ready chunk selection

## Rule

The label should match the citation role.

Examples:

* a **Product-specific** claim should not be cited only with a general historical source
* a **Historically documented** claim should not rest only on modern product pages

---

# 14. Relationship to Conflict Handling

If a conflict materially changes the answer, the labeling should reflect that.

## Rule

When conflict is live and relevant:

* use **Mixed evidence**
  or
* use scoped dual labels

Example:

* manufacturer claim = **Product-specific**
* broader technical caveat = **Likely but context-dependent**
  or
* overall framing = **Mixed evidence**

Do not label a conflict-smoothed answer as **Well established** unless the conflict has been properly resolved and no longer materially affects the claim.

---

# 15. Relationship to Provenance and Review State

Labels should be sensitive to review state.

## Rule

A claim should not normally be labeled **Well established** if it rests mainly on:

* unreviewed metadata
* model-suggested field interpretation
* unresolved conflict
* draft-only artifacts

## Rule

Low review state pushes labels toward:

* Product-specific
* Case-specific
* Likely but context-dependent
* Uncertain

rather than toward overly broad certainty labels.

---

# 16. Writing Rules for Explicit Label Use

If labels are shown directly in user-facing text, they should be used naturally.

Preferred style:

* “This is well established.”
* “This is historically documented.”
* “This part is product-specific.”
* “That finding is case-specific.”
* “This is likely, but context-dependent.”
* “The evidence here is mixed.”
* “This point remains uncertain.”

Avoid robotic formatting unless the user wants structured output.

---

# 17. Internal Labeling Rules

Even if labels are not always shown to the user, the answer-generation pipeline should assign internal labels to major claims or sections.

At minimum, internal labeling should support:

* ranking certainty
* shaping hedging language
* preventing scope collapse
* benchmark evaluation
* conflict-aware answer assembly

---

# 18. Prohibited Labeling Behavior

## 18.1 No certainty inflation

Do not label a claim **Well established** just because it sounds plausible.

## 18.2 No scope erasure

Do not label a narrow product or case claim as broad general truth.

## 18.3 No fake uncertainty

Do not label clear facts as **Uncertain** merely to sound cautious.

## 18.4 No conflict hiding

Do not label genuinely contested claims as **Well established** if disagreement materially remains.

## 18.5 No label/source mismatch

Do not use a label whose evidentiary basis does not match the sources being used.

---

# 19. Minimum Labeling QA Questions

Before approving answer behavior, the reviewer should be able to answer:

1. Does the label match the evidence scope?
2. Does the label match the source type?
3. Does the label hide a real conflict?
4. Does the label overgeneralize product or case evidence?
5. Is the label too weak for a genuinely strong claim?
6. Would the user be misled by the label choice?

If these cannot be answered confidently, labeling is not mature enough.

---

# 20. Label-to-Language Guidance

Suggested language patterns:

## Well established

* “This is well established.”
* “Broadly speaking, this is a stable point.”
* “The evidence here is strong and consistent.”

## Historically documented

* “This is historically documented.”
* “There is documented historical support for this.”
* “This is supported by historical/conservation evidence.”

## Product-specific

* “This is product-specific.”
* “For this particular paint/product…”
* “This applies to that brand/line, not necessarily all paints of that type.”

## Case-specific

* “This is case-specific.”
* “That finding comes from a specific case/study.”
* “It is strong for that case, but not automatically universal.”

## Likely but context-dependent

* “This is likely, but context-dependent.”
* “That is a common pattern, though the details depend on context.”
* “This is a useful general rule, but not an absolute one.”

## Mixed evidence

* “The evidence here is mixed.”
* “Different sources support different framings.”
* “This depends on which level of evidence you prioritize.”

## Uncertain

* “This remains uncertain.”
* “The evidence here is limited or incomplete.”
* “I would treat that point cautiously.”

---

# 21. Example Labeling Patterns

## Example 1 — Titanium white in the 15th century

Preferred label:

* **Well established**
  or
* **Historically documented** if framed historically

Reason:
Strong historical plausibility question with stable answer.

## Example 2 — One brand’s zinc white drying note

Preferred label:

* **Product-specific**

Reason:
Applies to one product/line, not all zinc whites universally.

## Example 3 — One analyzed painting used walnut oil

Preferred label:

* **Case-specific**
  or
* **Historically documented** if framed carefully

Reason:
Strong but narrow historical evidence.

## Example 4 — Burnt umber often drying faster

Preferred label:

* **Likely but context-dependent**

Reason:
Real and useful pattern, but formulation still matters.

## Example 5 — Zinc white risk framing

Preferred label:

* **Mixed evidence**
  or split between:

  * **Product-specific**
  * **Likely but context-dependent**

Reason:
Different source types often answer different aspects of the question.

---

# 22. Evaluation Use

Benchmark evaluation should inspect whether the answer label status was appropriate.

Scoring should penalize:

* overuse of **Well established**
* misuse of **Uncertain**
* failure to label product-specific answers as such
* failure to preserve case-specific scope
* smoothing mixed evidence into one absolute answer

---

# 23. Machine-Readable Support

This standard should later be paired with a structured file such as:

* `answer_label_schema.json`

Suggested fields:

* `label`
* `scope_level`
* `confidence`
* `source_basis`
* `conflict_state`
* `display_mode`

This would allow labels to be used consistently in generation and evaluation.

---

# 24. Non-Negotiable Rules

## 24.1 No scope inflation

Narrow evidence must stay narrow.

## 24.2 No certainty theater

Labels must reflect real evidentiary status.

## 24.3 No conflict smoothing

Mixed evidence must not be mislabeled as settled.

## 24.4 No product flattening

Product claims must stay product-specific unless broader support exists.

## 24.5 No case-study flattening

Case findings must not be presented as universal without support.

---

# 25. Operational Checklist

## Before labeling a claim

* [ ] Source type identified
* [ ] Scope identified
* [ ] Conflict state checked
* [ ] Review state checked
* [ ] Generalizability checked

## Before approving answer behavior

* [ ] Labels match evidence class
* [ ] Labels do not hide conflict
* [ ] Labels do not overgeneralize
* [ ] Labels remain useful to the user

---

# 26. Recommended Companion Documents

This standard works together with:

1. `foundation/FOUNDATION_PACK_v1.md`
2. `source_acquisition_policy.md`
3. `metadata_provenance_rules.md`
4. `conflict_resolution_policy.md`
5. `retrieval_policy_v1.md`
6. `benchmark_gold_set_v1.json`

---

# 27. Adoption Rule

This document should be treated as the canonical answer-labeling standard for v1 of the Oil Painting Research Assistant.

No answer-generation pipeline, benchmark evaluation system, or live synthesis mode should be considered complete unless it can apply these labels consistently and truthfully.
