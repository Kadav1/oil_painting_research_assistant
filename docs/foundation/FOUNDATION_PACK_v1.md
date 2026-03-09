# Oil Painting Research Assistant — Foundation Pack v1.0

## 0. Purpose

This Foundation Pack defines the **minimum canonical structure** for building the Oil Painting Research Assistant as a reliable RAG system.

It locks six things:

1. source hierarchy
2. metadata schema
3. controlled vocabulary
4. chunking rules
5. benchmark template
6. system prompt v1

This is the document that should be treated as the **build baseline** before ingestion, chunking, embeddings, or retrieval tuning.

---

# 1. Source Hierarchy

## 1.1 Trust Order

The assistant must not treat all sources as equal. It should rank sources by **epistemic strength**, not convenience.

| Tier | Label                        | Source Class                                                                                                           | Primary Use                                                                                 | Main Risk                                           |
| ---- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1    | Highest Trust                | Museum conservation departments, technical bulletins, conservation science papers, conservation institute publications | Historical materials evidence, degradation behavior, layer structure, technical examination | Overgeneralizing from a specific case study         |
| 2    | Strong Reference             | Pigment encyclopedias, pigment handbooks, structured technical references                                              | Pigment identity, chemistry, history, lightfastness, handling tendencies                    | Sometimes too general or not brand-specific         |
| 3    | Practical Product Data       | Manufacturer technical sheets, product pages, SDS/TDS                                                                  | Modern tube-paint facts, pigment codes, vehicle oil, opacity, drying notes                  | Brand-specific claims mistaken for universal truths |
| 4    | Instructional / Interpretive | Serious atelier texts, technical painting manuals, art-history technique references                                    | Studio method, historical workflow interpretation, painterly explanation                    | Studio lore, inherited myths, soft sourcing         |
| 5    | Low Trust / Supplemental     | Blogs, casual tutorials, forums, social posts                                                                          | Vocabulary discovery, weak supplemental context only                                        | Low rigor, repetition of myths, unclear provenance  |

## 1.2 Retrieval Priority Rule

When two sources conflict, the system should prefer:

1. Tier 1 over all lower tiers
2. Tier 2 over Tier 3–5 for general material facts
3. Tier 3 over Tier 4–5 for modern product-specific facts
4. Tier 4 only when the question is about teaching method, workflow, or painterly interpretation
5. Tier 5 only if explicitly marked as supplemental and never as core evidence

## 1.3 Case Study Rule

A Tier 1 source is not automatically universal.

If a technical bulletin describes:

* one painting
* one workshop
* one restoration campaign
* one pigment failure mode under a specific condition

then the assistant must label the claim as:

* **Observed in this case**
* **Likely relevant more broadly**
* **Not sufficient to generalize universally**

## 1.4 Source Role Mapping

| Question Type                                                | Preferred Source Tier              |
| ------------------------------------------------------------ | ---------------------------------- |
| “What is this pigment chemically?”                           | 2                                  |
| “Was this pigment used historically in 16th-century Venice?” | 1, then 2                          |
| “Why is this paint film cracking?”                           | 1, then 3                          |
| “What pigment code is in this modern paint?”                 | 3                                  |
| “Why does this shadow mixture turn muddy?”                   | 2, 4, then color-theory references |
| “How did Flemish painters structure flesh?”                  | 1, then 4                          |

---

# 2. Metadata Schema

The schema is split into:

* **Source-level metadata**: one record per source
* **Chunk-level metadata**: one record per chunk

The source record describes the document as a whole.
The chunk record describes a retrievable unit inside that document.

---

## 2.1 Source-Level Metadata

### Required fields

| Field                      | Type            | Required | Description                     |
| -------------------------- | --------------- | -------: | ------------------------------- |
| `source_id`                | string          |      yes | Unique internal source ID       |
| `title`                    | string          |      yes | Full source title               |
| `short_title`              | string          |      yes | Short scan-friendly title       |
| `source_family`            | enum            |      yes | Broad source class              |
| `source_type`              | enum            |      yes | More specific source type       |
| `institution_or_publisher` | string          |      yes | Organization or publisher       |
| `author`                   | string/null     |      yes | Author(s) if known, else org    |
| `publication_year`         | string/int/null |      yes | Year or `unknown`               |
| `edition_or_version`       | string/null     |       no | Version or snapshot label       |
| `source_url`               | string/null     |      yes | Original URL if any             |
| `access_type`              | enum            |      yes | How source was obtained         |
| `raw_file_name`            | string          |      yes | Saved raw filename              |
| `raw_file_path`            | string          |      yes | Raw file path                   |
| `capture_date`             | date            |      yes | Date acquired                   |
| `capture_method`           | enum            |      yes | Download / capture method       |
| `trust_tier`               | int/null        |      yes | 1–5, nullable until reviewed    |
| `authority_score`          | int/null        |      yes | 0–5                             |
| `extractability_score`     | int/null        |      yes | 0–5                             |
| `coverage_value_score`     | int/null        |      yes | 0–5                             |
| `density_score`            | int/null        |      yes | 0–5                             |
| `priority_score`           | int/null        |      yes | Derived score                   |
| `domain`                   | enum            |      yes | Main domain                     |
| `subdomain`                | string/null     |      yes | More specific area              |
| `materials_mentioned`      | list[string]    |      yes | Materials named                 |
| `pigment_codes`            | list[string]    |      yes | Pigment codes present           |
| `binder_types`             | list[string]    |      yes | Binders/oils/media present      |
| `historical_period`        | enum/string     |      yes | Period scope                    |
| `artist_or_school`         | list[string]    |      yes | Relevant artists/schools        |
| `question_types_supported` | list[enum]      |      yes | Answerable question classes     |
| `raw_captured`             | bool            |      yes | Raw saved                       |
| `normalized_text_created`  | bool            |      yes | Clean text exists               |
| `tables_extracted`         | enum            |      yes | yes / no / partial / n_a        |
| `metadata_attached`        | bool            |      yes | Metadata file exists            |
| `qa_reviewed`              | bool            |      yes | Human QA performed              |
| `chunked`                  | bool            |      yes | Chunking complete               |
| `indexed`                  | bool            |      yes | Indexed into retrieval store    |
| `ready_for_use`            | bool            |      yes | Approved for live retrieval     |
| `case_study_vs_general`    | enum            |      yes | Nature of source evidence       |
| `claim_types_present`      | list[enum]      |      yes | Types of claims in source       |
| `confidence_level`         | enum            |      yes | Confidence in metadata quality  |
| `limitations_notes`        | string          |      yes | Boundaries and weaknesses       |
| `license_or_usage_notes`   | string          |      yes | Internal use / summary rules    |
| `citation_format`          | string          |      yes | Preferred short citation text   |
| `summary`                  | string          |      yes | 2–4 sentence functional summary |
| `retrieval_notes`          | string          |      yes | When to retrieve it             |
| `internal_notes`           | string/null     |       no | Project-specific notes          |

---

## 2.2 Chunk-Level Metadata

### Required fields

| Field                      | Type         | Required | Description                                         |
| -------------------------- | ------------ | -------: | --------------------------------------------------- |
| `chunk_id`                 | string       |      yes | Unique chunk ID                                     |
| `source_id`                | string       |      yes | Parent source ID                                    |
| `chunk_index`              | int          |      yes | Chunk order within source                           |
| `chunk_title`              | string       |      yes | Semantic label                                      |
| `section_path`             | string       |      yes | Section hierarchy path                              |
| `page_range`               | string/null  |       no | PDF page range if relevant                          |
| `text`                     | string       |      yes | Chunk text                                          |
| `token_estimate`           | int          |      yes | Approximate token count                             |
| `chunk_type`               | enum         |      yes | prose / table / glossary / figure_note / mixed      |
| `domain`                   | enum         |      yes | Main domain                                         |
| `subdomain`                | string/null  |      yes | Specific area                                       |
| `materials_mentioned`      | list[string] |      yes | Named materials                                     |
| `pigment_codes`            | list[string] |      yes | Pigment codes in chunk                              |
| `binder_types`             | list[string] |      yes | Binder/media terms                                  |
| `historical_period`        | enum/string  |      yes | Period scope                                        |
| `artist_or_school`         | list[string] |      yes | Relevant artist/school                              |
| `question_types_supported` | list[enum]   |      yes | Question classes this chunk helps answer            |
| `claim_types_present`      | list[enum]   |      yes | Evidence style in this chunk                        |
| `case_specificity`         | enum         |      yes | case_specific / broadly_reference / mixed / unknown |
| `citability`               | enum         |      yes | direct / paraphrase_only / caution                  |
| `retrieval_weight_hint`    | int/null     |       no | Optional manual boost                               |
| `quality_flags`            | list[string] |      yes | OCR issue, table messy, etc.                        |
| `review_status`            | enum         |      yes | draft / reviewed / approved / rejected              |

---

## 2.3 File Naming Standard

### Source IDs

* `SRC-MUS-001`
* `SRC-PIG-001`
* `SRC-MFR-001`
* `SRC-COL-001`
* `SRC-HIS-001`
* `SRC-SCI-001`

### Chunk IDs

* `CHK-SRC-MUS-001-001`
* `CHK-SRC-MUS-001-002`

### Metadata files

* `SRC-MUS-001.json`
* `CHK-SRC-MUS-001-001.json`

---

# 3. Controlled Vocabulary

This vocabulary must be locked early so ingestion stays consistent.

---

## 3.1 Source Family

Allowed values:

* `museum_conservation`
* `pigment_reference`
* `manufacturer`
* `color_theory`
* `historical_practice`
* `scientific_paper`

---

## 3.2 Source Type

Allowed values:

* `technical_bulletin`
* `case_study`
* `pigment_entry`
* `product_page`
* `technical_data_sheet`
* `safety_data_sheet`
* `glossary`
* `educational_reference`
* `historical_text`
* `atelier_text`
* `scientific_article`

---

## 3.3 Domain

Allowed values:

* `pigment`
* `binder`
* `medium`
* `conservation`
* `color_theory`
* `technique`
* `historical_practice`
* `product`

---

## 3.4 Question Type

Allowed values:

* `chemistry`
* `handling`
* `historical_plausibility`
* `conservation_risk`
* `product_comparison`
* `color_analysis`
* `terminology`

---

## 3.5 Claim Type

Allowed values:

* `observed_case_evidence`
* `general_technical_reference`
* `product_specification`
* `historical_documentation`
* `teaching_framework`
* `interpretive_explanation`

---

## 3.6 Confidence Level

Allowed values:

* `high`
* `medium`
* `low`

---

## 3.7 Case Study vs General

Allowed values:

* `case_study`
* `general_reference`
* `mixed`
* `unknown`

---

## 3.8 Review Status

Allowed values:

* `draft`
* `reviewed`
* `approved`
* `rejected`

---

## 3.9 Tables Extracted

Allowed values:

* `yes`
* `no`
* `partial`
* `not_applicable`

---

## 3.10 Citability

Allowed values:

* `direct`
* `paraphrase_only`
* `caution`

---

## 3.11 Chunk Type

Allowed values:

* `prose`
* `table`
* `glossary`
* `figure_note`
* `mixed`

---

## 3.12 Binder Vocabulary

Canonical forms:

* `linseed`
* `walnut`
* `safflower`
* `poppy`
* `stand_oil`
* `alkyd`
* `resin`
* `wax`
* `solvent`
* `drier`

### Alias examples

* “cold-pressed linseed oil” → `linseed`
* “refined walnut oil” → `walnut`
* “sun-thickened oil” → `stand_oil` only if context is correct; otherwise preserve raw text in note field

---

## 3.13 Material Naming Rule

Use **canonical primary name** plus aliases.

### Example

Canonical:

* `lead_white`

Aliases:

* flake white
* Cremnitz white
* basic lead carbonate
* PW1

Do not collapse different materials incorrectly.

### Separate canonical materials

* `lead_white`
* `zinc_white`
* `titanium_white`
* `ultramarine`
* `yellow_ochre`
* `raw_umber`
* `burnt_umber`
* `terre_verte`
* `ivory_black`
* `smalt`
* `verdigris`
* `viridian`
* `cadmium_red`
* `alizarin_crimson`

---

## 3.14 Pigment Code Normalization

Rules:

* preserve official casing where possible
* store as exact strings, e.g. `PW1`, `PW4`, `PB29`, `PBr7`, `PR108`, `PY43`
* never infer a pigment code not explicitly supported
* if a product has multiple pigments, preserve full list
* if a text mentions a pigment name but not a code, leave code field empty

---

## 3.15 Historical Period Vocabulary

Suggested values:

* `medieval`
* `15th_century`
* `16th_century`
* `17th_century`
* `18th_century`
* `19th_century`
* `20th_century`
* `modern`
* `mixed`
* `not_applicable`

---

## 3.16 Artist or School Vocabulary

Use normalized names where possible:

* `flemish`
* `venetian`
* `northern_european`
* `dutch`
* `italian`
* `spanish`
* `french`
* `baroque`
* `van_dyck`
* `rogier_van_der_weyden`
* `general`

---

# 4. Chunking Rules

## 4.1 Chunking Principle

Chunk by **semantic unit**, not by arbitrary character count.

A chunk should contain **one coherent retrievable idea**.

Good chunk examples:

* one pigment entry
* one subsection on drying behavior
* one product page description
* one conservation subsection on smalt discoloration
* one glossary definition
* one table plus its interpretive note

Bad chunk examples:

* half a pigment entry
* unrelated paragraphs from different sections
* five separate products merged together
* a long section split mid-argument

---

## 4.2 Target Chunk Size

### Default prose chunk

* 500–900 tokens

### Dense technical prose

* 350–700 tokens

### Product pages

* one product per chunk whenever possible

### Glossary entries

* 100–350 tokens

### Tables

* separate chunk if table is meaningful on its own
* keep nearby explanatory text linked if needed

---

## 4.3 Chunk Boundary Rules

Start a new chunk when:

* heading changes
* material changes
* product changes
* question type changes
* document switches from explanation to table
* historical context shifts significantly
* case-study evidence changes to broader interpretation

Do not split when:

* the paragraph sequence is part of one explanation
* a technical point depends on the next paragraph
* a table needs its caption or note to make sense

---

## 4.4 Table Handling

If a table is important:

* store it as structured data when possible
* also create a text rendering for retrieval
* retain row/column meaning
* link it to source and section

If table extraction is weak:

* flag it in `quality_flags`
* do not treat it as fully reliable until reviewed

---

## 4.5 Chunk Metadata Minimum

Every chunk must have:

* parent source
* section label
* domain
* materials
* question type support
* claim type support
* review status

A chunk without metadata is not ready for indexing.

---

## 4.6 Quote and Citation Rule

Chunks should preserve enough context for safe paraphrase and citation, but not rely on huge verbatim blocks.

The chunk must make it possible to answer:

* what this claim is
* what source it came from
* whether it is case-specific
* whether it is product-specific
* whether it is historical, technical, or instructional

---

## 4.7 Duplication Rule

Avoid duplicate chunks unless one of these is true:

* one version is cleaned prose
* one version is a structured table
* one version is a glossary abstraction
* one version is a product comparison abstraction

Otherwise duplicates should be merged or rejected.

---

## 4.8 Review Flags

Suggested chunk-level quality flags:

* `ocr_suspect`
* `table_messy`
* `citation_unclear`
* `product_specific`
* `case_specific`
* `historical_scope_unclear`
* `needs_manual_review`

---

# 5. Benchmark Template

The benchmark exists to test whether the assistant is actually useful and trustworthy.

---

## 5.1 Benchmark Categories

Minimum benchmark categories:

1. pigments
2. binders and media
3. conservation failure modes
4. historical practice
5. color theory
6. product comparison
7. terminology

---

## 5.2 Benchmark Question Template

Use one record per benchmark question.

| Field                   | Type         | Description                                                               |
| ----------------------- | ------------ | ------------------------------------------------------------------------- |
| `benchmark_id`          | string       | Unique benchmark ID                                                       |
| `category`              | enum         | Main category                                                             |
| `question`              | string       | User-style question                                                       |
| `difficulty`            | enum         | easy / medium / hard                                                      |
| `target_modes`          | list         | Studio / Conservation / Art History / Color Analysis / Product Comparison |
| `expected_source_tiers` | list[int]    | Which tiers should dominate                                               |
| `must_use_domains`      | list         | Domains expected in answer                                                |
| `must_not_confuse`      | list         | Known confusion traps                                                     |
| `expected_answer_shape` | string       | What a good answer should contain                                         |
| `evaluation_notes`      | string       | Manual evaluation notes                                                   |
| `gold_claims`           | list[string] | Core facts answer should include                                          |
| `known_uncertainties`   | list[string] | Where answer should hedge                                                 |
| `status`                | enum         | draft / approved / revised                                                |

---

## 5.3 Benchmark Example

```json
{
  "benchmark_id": "BMK-PIG-001",
  "category": "pigments",
  "question": "Why does zinc white often cause concern in oil painting?",
  "difficulty": "medium",
  "target_modes": ["Studio", "Conservation"],
  "expected_source_tiers": [1, 3],
  "must_use_domains": ["pigment", "conservation", "product"],
  "must_not_confuse": [
    "Do not confuse product-specific warnings with universal prohibition",
    "Do not confuse zinc white with titanium white"
  ],
  "expected_answer_shape": "Direct answer, explanation of brittleness/slow drying concerns, distinction between modern product guidance and broader conservation issues, practical takeaway",
  "evaluation_notes": "Answer should be careful, not hysterical, and should distinguish degree of risk",
  "gold_claims": [
    "Zinc white is associated with brittleness concerns in oil paint films",
    "It should not be flattened into a simple always-never rule",
    "Modern product usage and conservation literature should be distinguished"
  ],
  "known_uncertainties": [
    "Risk varies by context, formulation, proportion, and application"
  ],
  "status": "approved"
}
```

---

## 5.4 Scoring Rubric

Each answer should be scored 1–5 on:

| Dimension            | What to check                                                   |
| -------------------- | --------------------------------------------------------------- |
| Accuracy             | Are the material facts correct?                                 |
| Source Fitness       | Did it rely on the right kind of sources?                       |
| Usefulness           | Is the answer practically useful to a painter/researcher?       |
| Uncertainty Handling | Did it hedge where appropriate?                                 |
| Distinction Quality  | Did it separate chemistry, history, and product data correctly? |
| Citation Readiness   | Could the answer be tied back cleanly to sources?               |

### Suggested pass threshold

* average score ≥ 4.0
* no score below 3 in Accuracy or Source Fitness

---

## 5.5 Starter Benchmark Set

Suggested first 20 benchmark prompts:

### Pigments

1. What is the difference between lead white, zinc white, and titanium white?
2. Why does burnt umber often dry faster than other colors?
3. What is smalt, and why can it discolor?
4. Is terre verte a useful color for flesh shadows?

### Binders / Media

5. When would I prefer walnut oil over linseed oil?
6. What does stand oil do differently from regular linseed oil?
7. Why do some mediums yellow more than others?

### Conservation

8. Why did my paint wrinkle overnight?
9. What does “sinking in” mean in oil painting?
10. Why can a glaze lose saturation over time?
11. What causes brittleness in oil paint films?

### Historical Practice

12. Would a 15th-century painter likely have used titanium white?
13. Was verdigris commonly used in oil painting?
14. How did Northern European painters commonly structure paint layers?

### Color Theory

15. Why do my shadows turn muddy?
16. What is the difference between hue, value, and chroma?
17. Why can complementary mixtures go grey instead of vibrant?

### Product Comparison

18. Compare two modern zinc white paints for drying and handling.
19. How can two paints with the same pigment code still behave differently?

### Terminology

20. What is the difference between opacity and tinting strength?

---

# 6. System Prompt v1

Below is the recommended baseline system prompt for the assistant.

```text
You are the Oil Painting Research Assistant.

Your role is to answer questions about oil painting using a disciplined retrieval-based method grounded in curated source material.

Your knowledge base includes:
- museum conservation and technical bulletins
- pigment reference sources
- manufacturer technical and product data
- color-theory references
- art-history and atelier sources
- scientific papers where relevant

Your job is not to sound authoritative.
Your job is to be accurate, source-aware, and useful.

## Core Behavior

When answering, you must:

1. Prefer higher-trust sources over lower-trust sources.
2. Distinguish clearly between:
   - conservation evidence
   - general technical reference
   - product-specific information
   - historical documentation
   - teaching or interpretive explanation
3. Avoid flattening case studies into universal rules.
4. Avoid treating brand-specific product behavior as a universal material law.
5. Say explicitly when evidence is mixed, limited, or context-dependent.
6. Never invent pigment codes, dates, authors, materials, or historical claims.
7. Preserve uncertainty where appropriate instead of pretending certainty.
8. Be practically useful: explain what the information means for a painter, researcher, or conservator-level reader.
9. Do not give invasive restoration instructions as casual advice.
10. When a question is product-specific, prioritize product data and clearly label it as modern brand information.
11. When a question is historical, prioritize conservation and historical sources over modern teaching advice.
12. When a question is about color, explain in painterly terms while preserving technical clarity.

## Answer Structure

When possible, organize answers in this order:

A. Direct answer  
B. Why it works this way  
C. What kind of source supports this  
D. Limits / uncertainty  
E. Practical takeaway

## Modes

You may implicitly shift emphasis depending on the question:

- Studio Mode: practical handling and painting decisions
- Conservation Mode: degradation, risk, archival concerns
- Art History Mode: historical plausibility and documented practice
- Color Analysis Mode: hue, value, chroma, mixture behavior
- Product Comparison Mode: compare modern paints and brands

## Source Handling Rules

If evidence comes from a case study:
- say that it is observed in a specific case
- do not automatically generalize it

If evidence comes from a manufacturer:
- label it as product-specific
- do not confuse it with universal chemistry

If evidence comes from teaching or atelier material:
- treat it as interpretive unless corroborated

## Prohibited Behavior

Do not:
- hallucinate citations
- invent technical certainty
- collapse distinct materials into one
- confuse pigment identity with product marketing names
- give definitive historical claims without source support
- overstate conservation advice beyond the evidence

## Tone

Use clear, precise, grounded language.
Be technical when needed, but never vague for the sake of sounding intelligent.
Do not use inflated language.
Do not dramatize uncertainty; state it cleanly.

## Final Goal

Your goal is to produce answers that are:
- accurate
- well-scoped
- source-aware
- practically useful
- explicit about uncertainty
```

---

# 7. Implementation Notes

## 7.1 What should be locked immediately

Lock these before ingestion begins:

* source hierarchy
* source family vocabulary
* source type vocabulary
* claim type vocabulary
* domain vocabulary
* question type vocabulary
* chunking rules
* benchmark schema

## 7.2 What can evolve later

These can expand later without breaking the foundation:

* material alias list
* artist/school vocabulary
* product-line vocabulary
* benchmark size
* scoring rubric detail
* retrieval weight hints

---

# 8. Recommended Next Files

The first files to create from this pack should be:

1. `FOUNDATION_PACK_v1.md`
2. `source_register_schema.json`
3. `chunk_schema.json`
4. `controlled_vocabulary.json`
5. `benchmark_template.json`
6. `system_prompt_v1.md`

---
