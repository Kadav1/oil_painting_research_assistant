# Benchmark Template v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-FND-005
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** Structure, categories, record fields, scoring dimensions, failure taxonomy, and design rules for the Oil Painting Research Assistant benchmark set
**Applies to:** Benchmark authoring, benchmark evaluation, answer scoring, failure logging, and system quality assessment

---

# 1. Purpose

This document defines the canonical benchmark template for the Oil Painting Research Assistant.

It specifies:

* the purpose and scope of benchmarking in this system
* the categories that benchmarks must cover
* the structure of each benchmark record
* the dimensions on which answers are scored
* the failure taxonomy for logging retrieval and generation failures
* the rules for designing good benchmark questions
* guidance for building the starter benchmark set

This is the **conceptual template**, not the gold set itself.
The gold set is stored in `benchmarks/benchmark_gold_set_v1.json`.
The structure of benchmark records must conform to `schemas/benchmark_template.json`.

---

# 2. Core Principle

The benchmark exists to test whether the assistant is actually accurate and trustworthy — not just fluent.

A benchmark is not passed by producing a confident-sounding answer.
A benchmark is passed by producing an answer that is:

* factually correct
* appropriately scoped (case-specific claims not universalized, product-specific claims not generalized)
* grounded in the right kind of sources
* explicit about uncertainty where uncertainty is real
* practically useful to the intended audience

Fluency without accuracy is a benchmark failure.

---

# 3. Objectives

1. Define a reusable benchmark record structure applicable to all question categories
2. Establish the minimum benchmark categories that v1 must cover
3. Define scoring dimensions that reward accuracy, scope-awareness, and useful uncertainty handling
4. Define a failure taxonomy that supports systematic diagnosis of retrieval and generation problems
5. Provide design rules for authoring rigorous benchmark questions

---

# 4. Benchmark Categories

The minimum benchmark categories for v1 are:

| Category | Code | What it tests |
|---------|------|--------------|
| Pigments | `PIG` | Pigment identity, chemistry, historical use, lightfastness, handling |
| Binders and Media | `BND` | Oil, resin, wax, and medium chemistry, drying, handling |
| Conservation | `CON` | Degradation, failure modes, archival risk, conservation evidence |
| Historical Practice | `HIS` | Historical plausibility, period-specific practices, documented technique |
| Color Theory | `COL` | Hue, value, chroma, mixture behavior, optical behavior |
| Product Comparison | `PRD` | Modern commercial product comparison, brand/line-specific questions |
| Terminology | `TRM` | Definition, disambiguation, conceptual distinctions |

Additional categories may be introduced in later versions. The seven categories above must be covered in v1.

---

# 5. Benchmark Record Structure

Each benchmark record contains the following fields.

## 5.1 Identity and Classification Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `benchmark_id` | string | yes | Unique benchmark ID. Format: `BMK-{CATEGORY_CODE}-{NNN}`. |
| `category` | enum | yes | Benchmark category. One of the seven in §4. |
| `question` | string | yes | The user-style question, as a natural language prompt. |
| `difficulty` | enum | yes | `easy`, `medium`, or `hard`. |
| `status` | enum | yes | `draft`, `approved`, or `revised`. |

## 5.2 Target and Expectation Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_modes` | list[string] | yes | Answer modes the question is expected to activate. Values: `Studio`, `Conservation`, `Art History`, `Color Analysis`, `Product Comparison`. |
| `expected_source_tiers` | list[int] | yes | Source trust tiers expected to dominate the answer (1–5). |
| `must_use_domains` | list[string] | yes | Domains that must be represented in a correct answer. |
| `must_not_confuse` | list[string] | yes | Known confusion traps this question is designed to expose. |
| `expected_answer_shape` | string | yes | Description of what a correct, well-formed answer should contain. |

## 5.3 Evaluation Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gold_claims` | list[string] | yes | Core factual claims that a correct answer must include or be consistent with. |
| `known_uncertainties` | list[string] | yes | Areas where the answer should hedge or acknowledge uncertainty. |
| `evaluation_notes` | string | yes | Guidance for human evaluators: what to look for, what to penalize. |

---

# 6. Scoring Dimensions

Each answer is scored on six dimensions, each rated 1–5.

| Dimension | What it tests | Score 5 | Score 1 |
|-----------|--------------|---------|---------|
| **Accuracy** | Are the material facts correct? | All gold claims present; no factual errors | Factual errors or missing core claims |
| **Source Fitness** | Did the answer rely on the right kind of sources? | Correct tier prioritization for question type | Wrong tier used as primary authority |
| **Usefulness** | Is the answer practically useful to the intended audience? | Directly actionable; explains implications | Technically present but practically unhelpful |
| **Uncertainty Handling** | Did it hedge where appropriate? | Explicitly states limits; uses answer labels correctly | False certainty or unacknowledged uncertainty |
| **Distinction Quality** | Did it separate chemistry, history, and product data correctly? | Correct scope applied throughout | Scope conflation: product generalized, case universalized |
| **Citation Readiness** | Can the answer be tied back cleanly to sources? | Clear, traceable source attribution | No attributable source basis |

### Pass threshold

* Average score ≥ 4.0 across all six dimensions
* No individual dimension score below 3 in **Accuracy** or **Source Fitness**

Answers that pass on average but fail the Accuracy or Source Fitness floor do not pass.

---

# 7. Difficulty Definitions

| Level | Meaning | Typical characteristics |
|-------|---------|------------------------|
| `easy` | Single-domain question with a clear, well-sourced answer | One source tier relevant; minimal uncertainty; direct answer |
| `medium` | Cross-domain or nuanced question requiring scope awareness | Multiple tiers may apply; some uncertainty or conflict expected |
| `hard` | Requires synthesis across sources, explicit conflict handling, or careful historical reasoning | Conflicting sources likely; case-specificity essential; answer labels required |

---

# 8. Answer Mode Definitions

The benchmark uses five answer modes to classify the type of response expected.

| Mode | Activated by | Emphasis |
|------|-------------|---------|
| `Studio` | Studio handling, mixing, practical decision questions | Practical advice grounded in material behavior |
| `Conservation` | Degradation, risk, archival, failure questions | Long-term material stability; conservation evidence |
| `Art History` | Historical plausibility, period practice, attribution questions | Historical documentation; case-specific scope |
| `Color Analysis` | Hue, value, chroma, mixture behavior questions | Color mechanics; pigment optical behavior |
| `Product Comparison` | Brand/line/product-specific questions | Modern product data; Tier 3 authority |

A benchmark question may target multiple modes. `target_modes` is a list.

---

# 9. Failure Taxonomy

Failures are recorded in `data/logs/retrieval_failure_log.csv` and scored during benchmark evaluation.

| Failure type | Code | Definition |
|-------------|------|-----------|
| No relevant chunks retrieved | `RETRIEVAL_EMPTY` | Retrieval returned zero relevant results for a query that should have matches |
| Wrong tier prioritized | `WRONG_TIER` | A lower-tier source was ranked above a higher-tier source for a question where tier matters |
| Case generalized | `CASE_GENERALIZED` | A case-specific result was presented as a general rule |
| Product universalized | `PRODUCT_UNIVERSALIZED` | A product-specific claim was presented as universal material chemistry |
| Scope mismatch | `SCOPE_MISMATCH` | Retrieved chunks were from the wrong domain or question type |
| Fabricated citation | `FABRICATED_CITATION` | The answer cited a source or fact not present in the retrieved corpus |
| Uncertainty collapsed | `UNCERTAINTY_COLLAPSED` | Mixed-evidence or uncertain content was presented with false confidence |
| Conflict not disclosed | `CONFLICT_UNDISCLOSED` | A known conflict between sources was not surfaced in the answer |
| Historical anachronism | `HISTORICAL_ANACHRONISM` | A modern material or practice was asserted as historically accurate |
| Mode misalignment | `MODE_MISALIGNMENT` | The answer did not match the question's expected mode (e.g. conservation answer to a studio question) |

---

# 10. Benchmark Question Design Rules

Good benchmark questions are not just hard — they are **diagnostic**.

A well-designed benchmark question:

1. **Targets a known risk** — it is designed to expose a specific failure mode (e.g. product universalization, case generalization)
2. **Has a clear correct answer** — the evaluator can determine pass/fail without excessive interpretation
3. **Uses natural language** — phrased as a real user would ask, not as an abstract test item
4. **Specifies what a correct answer must contain** — gold claims and expected answer shape are explicit
5. **Specifies what a correct answer must not confuse** — the `must_not_confuse` list names the traps
6. **Has appropriate difficulty** — easy questions test basic retrieval; hard questions test synthesis and conflict handling

A benchmark question should **not**:

* Test trivial lookup with an obvious answer
* Be so ambiguous that any answer could be defended
* Target facts not present in the corpus
* Require reasoning about modern events after the knowledge cutoff
* Expect the assistant to invent historical facts

---

# 11. Starter Benchmark Coverage Requirements

The v1 gold set in `benchmarks/benchmark_gold_set_v1.json` must include at minimum:

| Category | Minimum questions | Notes |
|---------|------------------|-------|
| Pigments | 4 | Include at least one chemistry question and one historical use question |
| Binders and Media | 3 | Include at least one drying/handling question |
| Conservation | 3 | Include at least one failure mode and one risk question |
| Historical Practice | 3 | Include at least one historical plausibility question |
| Color Theory | 2 | Include at least one mixture behavior question |
| Product Comparison | 2 | Include at least one same-pigment-different-product question |
| Terminology | 2 | Include at least one disambiguation question |

**Total minimum: 19 questions**

Hard questions must represent at least 25% of the set.

---

# 12. Benchmark Record Example

```json
{
  "benchmark_id": "BMK-PIG-001",
  "category": "PIG",
  "question": "Why does zinc white often cause concern in oil painting?",
  "difficulty": "medium",
  "status": "approved",
  "target_modes": ["Studio", "Conservation"],
  "expected_source_tiers": [1, 3],
  "must_use_domains": ["pigment", "conservation", "product"],
  "must_not_confuse": [
    "Do not treat product-specific warnings as a universal prohibition on zinc white",
    "Do not confuse zinc white with titanium white"
  ],
  "expected_answer_shape": "Direct answer explaining brittleness and slow-drying concerns; distinction between modern product guidance and broader conservation findings; practical takeaway with appropriate hedging",
  "gold_claims": [
    "Zinc white is associated with brittleness concerns in oil paint films",
    "The degree of risk varies by formulation, proportion, and application context",
    "Conservation literature and modern product guidance should be distinguished"
  ],
  "known_uncertainties": [
    "Risk level is context-dependent and not a simple yes/no",
    "Different formulations and brands may present different risk profiles"
  ],
  "evaluation_notes": "Answer should be careful, not alarmist. Penalize answers that either dismiss concerns entirely or treat the risk as absolute. Look for explicit scope qualification."
}
```

---

# 13. QA Questions

Before approving a benchmark record:

1. Does the question expose a specific, realistic failure risk?
2. Are `gold_claims` specific enough to evaluate against?
3. Are `must_not_confuse` entries the actual known confusion traps — not generic cautions?
4. Is the `expected_answer_shape` descriptive enough to guide evaluation?
5. Is `difficulty` correctly assigned — not all questions medium?
6. Does `expected_source_tiers` reflect what tier should actually dominate for this question type?
7. Are `known_uncertainties` honest about where hedging is required?
8. Is the question phrased as a real user would ask it?

---

# 14. Recommended Companion Documents

1. `docs/foundation/source_hierarchy.md` — defines trust tiers referenced in `expected_source_tiers`
2. `docs/foundation/controlled_vocabulary.md` — defines answer labels referenced in scoring
3. `docs/foundation/system_prompt_v1.md` — defines answer modes referenced in `target_modes`
4. `docs/policies/answer_labeling_standard.md` — defines how answer labels are applied in scored answers
5. `docs/policies/retrieval_policy_v1.md` — governs what retrieval behavior the benchmark exercises
6. `schemas/benchmark_template.json` — the machine-readable schema for benchmark records
7. `benchmarks/benchmark_gold_set_v1.json` — the v1 gold question set

---

# 15. Adoption Rule

This document is the canonical benchmark template for v1 of the Oil Painting Research Assistant.

All benchmark records in the gold set must conform to the structure defined in §5.
All scoring must use the dimensions defined in §6 with the pass threshold defined in §6.
All failure logging must use the failure codes defined in §9.

---
