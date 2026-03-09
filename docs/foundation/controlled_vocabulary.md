# Controlled Vocabulary v1.0

## Oil Painting Research Assistant

**Document ID:** OPRA-FND-003
**Version:** v1.0
**Status:** Canonical Draft
**Scope:** All canonical enum values, list values, and naming rules used across the metadata schema, retrieval system, schemas, and code
**Applies to:** Ingestion, metadata authoring, chunking, indexing, retrieval, generation, evaluation, and all schema and code layers of the Oil Painting Research Assistant

---

# 1. Purpose

This document is the single source of truth for all controlled vocabulary in the Oil Painting Research Assistant.

It defines:

* which enum values are canonical for each metadata field
* which naming rules apply to materials, pigments, binders, historical periods, and artists
* which values are permitted, and which are not

Every enum used in a metadata record, schema file, Pydantic model, or Python constant must match a value defined here.

No new enum values may be introduced in schemas or code without first being added to this document.

---

# 2. Core Principle

Vocabulary stability is a precondition for system reliability.

If different modules use different names for the same concept — `museum_conservation` in one place and `museum` in another — filtering, retrieval, and citation will silently fail.

This document locks the vocabulary at v1. Changes require a version increment and coordinated updates to all referencing files.

---

# 3. Canonical Vocabulary

---

## 3.1 Source Family

The broad institutional classification of a source.

| Value | Meaning |
|-------|---------|
| `museum_conservation` | Museum conservation departments, technical bulletins, conservation institute publications |
| `pigment_reference` | Pigment encyclopedias, handbooks, structured technical pigment references |
| `manufacturer` | Manufacturer product pages, technical data sheets, SDS/TDS, official product guides |
| `color_theory` | Color theory references, optics-oriented painting references |
| `historical_practice` | Art history technique texts, atelier texts, historical painting manuals |
| `scientific_paper` | Peer-reviewed scientific articles on materials, degradation, and analysis |

Exactly these six values are permitted. No abbreviations or variants.

---

## 3.2 Source Type

The more specific type of a source within its family.

| Value | Typical Family | Meaning |
|-------|---------------|---------|
| `technical_bulletin` | `museum_conservation` | Conservation technical study or bulletin |
| `case_study` | `museum_conservation` | Documentation of a specific artwork or restoration campaign |
| `pigment_entry` | `pigment_reference` | A single-pigment reference entry |
| `product_page` | `manufacturer` | Official product page for a paint or material |
| `technical_data_sheet` | `manufacturer` | TDS: detailed technical specification |
| `safety_data_sheet` | `manufacturer` | SDS: safety and compositional data |
| `glossary` | `pigment_reference`, `color_theory` | Structured glossary or terminology reference |
| `educational_reference` | `color_theory`, `historical_practice` | Structured educational or reference work |
| `historical_text` | `historical_practice` | Primary or secondary historical source |
| `atelier_text` | `historical_practice` | Practical teaching text from an atelier tradition |
| `scientific_article` | `scientific_paper` | Peer-reviewed scientific publication |

---

## 3.3 Domain

The primary knowledge domain of a source or chunk.

| Value | Meaning |
|-------|---------|
| `pigment` | Pigment identity, chemistry, history, lightfastness, handling |
| `binder` | Oils, resins, waxes, drying media — binder chemistry and behavior |
| `medium` | Mixed media, mediums, varnishes, vehicles |
| `conservation` | Degradation, failure modes, archival concerns, restoration |
| `color_theory` | Hue, value, chroma, mixture behavior, optical theory |
| `technique` | Painting technique, layer structure, application method |
| `historical_practice` | Historically documented practices, period-specific methods |
| `product` | Modern commercial paint products, brand-specific data |

A source or chunk has one primary domain. `subdomain` may refine it further with free text.

---

## 3.4 Question Type

The class of user question a source or chunk is suited to answer.

| Value | Meaning |
|-------|---------|
| `chemistry` | Pigment or binder composition, molecular structure, chemical behavior |
| `handling` | Studio handling, drying, mixing, application, compatibility |
| `historical_plausibility` | Whether a material or practice is historically documented |
| `conservation_risk` | Degradation, failure modes, long-term stability, archival risk |
| `product_comparison` | Comparison of modern commercial products |
| `color_analysis` | Hue, value, chroma, mixture, optical behavior |
| `terminology` | Definition of terms, disambiguation of names |

---

## 3.5 Claim Type

The epistemological nature of the evidence or claims in a source or chunk.

| Value | Meaning |
|-------|---------|
| `observed_case_evidence` | Evidence documented in a specific artwork, case study, or examination |
| `general_technical_reference` | Broadly applicable technical reference material |
| `product_specification` | Manufacturer-specified product data for a specific product |
| `historical_documentation` | Documented historical practice or period evidence |
| `teaching_framework` | Instructional or pedagogical framing of practice |
| `interpretive_explanation` | Interpretive or explanatory content; not primary evidence |

---

## 3.6 Case Specificity

Whether a source or chunk represents case-specific or generally applicable evidence.

**For source-level field `case_study_vs_general`:**

| Value | Meaning |
|-------|---------|
| `case_study` | The source primarily documents a specific case, artwork, or campaign |
| `general_reference` | The source is a general-purpose reference |
| `mixed` | The source contains both case-specific and general content |
| `unknown` | Scope has not yet been determined |

**For chunk-level field `case_specificity`:**

| Value | Meaning |
|-------|---------|
| `case_specific` | This chunk's content is specific to a particular case, artwork, or context |
| `broadly_applicable` | This chunk's content applies generally across materials or practices |
| `mixed` | This chunk contains both case-specific and general content |
| `unknown` | Scope has not yet been determined |

The distinction must be preserved. Do not default to `general_reference` or `broadly_applicable` without reviewing the content.

---

## 3.7 Access Type

How a source was accessed for ingestion.

| Value | Meaning |
|-------|---------|
| `open_access` | Publicly available without restriction |
| `licensed` | Accessed under an institutional license or subscription |
| `purchased` | Acquired through direct purchase |
| `physical_scan` | Digitized from a physical document |
| `direct_download` | Downloaded from an official source |
| `manual_entry` | Content manually transcribed or entered |

---

## 3.8 Capture Method

The technical method used to capture the source.

| Value | Meaning |
|-------|---------|
| `pdf_download` | Downloaded as a PDF file |
| `html_scrape` | Captured from web HTML |
| `manual_copy` | Content manually copied and saved |
| `api_fetch` | Retrieved via an API |
| `ocr_scan` | Digitized using OCR from physical or image source |
| `structured_export` | Exported from a structured data source |

---

## 3.9 Tables Extracted

The extraction status of tabular content in a source.

| Value | Meaning |
|-------|---------|
| `yes` | All tables have been extracted |
| `no` | Tables exist but have not been extracted |
| `partial` | Some tables extracted; others remain |
| `not_applicable` | The source contains no significant tabular content |

---

## 3.10 Confidence Level

Reviewer confidence in the completeness and accuracy of a source's metadata.

| Value | Meaning |
|-------|---------|
| `high` | Reviewer is confident all fields are accurate and complete |
| `medium` | Most fields are accurate; some uncertainty remains |
| `low` | Significant uncertainty; metadata requires further review |

---

## 3.11 Chunk Type

The structural type of a chunk.

| Value | Meaning |
|-------|---------|
| `prose` | Narrative or explanatory text |
| `table` | A table or structured comparative data |
| `glossary` | A definition or glossary entry |
| `figure_note` | A figure caption or accompanying explanatory note |
| `mixed` | A chunk combining multiple structural types |

---

## 3.12 Binder Vocabulary

Canonical forms for binder and medium terms used in `binder_types` fields.

| Canonical value | Includes / aliases |
|----------------|-------------------|
| `linseed` | cold-pressed linseed oil, refined linseed oil, raw linseed oil |
| `walnut` | cold-pressed walnut oil, refined walnut oil |
| `safflower` | safflower oil |
| `poppy` | poppy oil, poppyseed oil |
| `stand_oil` | stand oil, sun-thickened oil (only when context is unambiguous) |
| `alkyd` | alkyd medium, alkyd binder |
| `resin` | damar, mastic, copal — preserve specific resin name in subdomain |
| `wax` | beeswax, carnauba — preserve specific wax name in subdomain |
| `solvent` | mineral spirits, turpentine, odourless mineral spirits |
| `drier` | cobalt drier, manganese drier, japan drier |

When a text refers to "sun-thickened oil," verify context before mapping to `stand_oil`. Preserve the original wording in the source text.

---

## 3.13 Citability

How a chunk may be used in citation.

| Value | Meaning |
|-------|---------|
| `direct` | The chunk may be directly cited or closely paraphrased with attribution |
| `paraphrase_only` | The chunk may be paraphrased but not directly quoted in an answer |
| `caution` | The chunk requires caution — license restrictions, OCR quality issues, or interpretive ambiguity apply |

---

## 3.14 Approval State

The operational retrieval gate for a chunk. Determines in which contexts the chunk may be served.

| Value | Meaning |
|-------|---------|
| `not_approved` | Chunk has not been approved for any retrieval context |
| `internal_draft_only` | Chunk may be used for internal development and testing only |
| `testing_only` | Chunk may be used in automated test and benchmark runs only |
| `retrieval_allowed` | Chunk may be included in retrieval results for development and review sessions |
| `live_allowed` | Chunk may be included in retrieval results for live user-facing sessions |

Only chunks with `approval_state` of `retrieval_allowed` or `live_allowed` are eligible for retrieval in production contexts.

`approval_state` is distinct from `review_status`. See §3.17.

---

## 3.15 Historical Period

The historical period scope of a source or chunk.

| Value | Meaning |
|-------|---------|
| `medieval` | Pre-1400 |
| `15th_century` | 1400–1499 |
| `16th_century` | 1500–1599 |
| `17th_century` | 1600–1699 |
| `18th_century` | 1700–1799 |
| `19th_century` | 1800–1899 |
| `20th_century` | 1900–1999 |
| `modern` | 2000–present |
| `mixed` | Content spans multiple historical periods |
| `not_applicable` | Historical period is not relevant to this source or chunk |

---

## 3.16 Artist or School Vocabulary

Canonical forms for artist and school references used in `artist_or_school` fields.

| Canonical value | Notes |
|----------------|-------|
| `flemish` | Flemish school broadly |
| `venetian` | Venetian school |
| `northern_european` | Northern European tradition broadly |
| `dutch` | Dutch school (Golden Age and related) |
| `italian` | Italian school broadly |
| `spanish` | Spanish school |
| `french` | French school |
| `baroque` | Baroque period broadly |
| `van_dyck` | Anthony van Dyck |
| `rogier_van_der_weyden` | Rogier van der Weyden |
| `rembrandt` | Rembrandt van Rijn |
| `rubens` | Peter Paul Rubens |
| `titian` | Tiziano Vecelli |
| `general` | No specific artist or school attribution |

New artist or school values must be added here before use in metadata.

---

## 3.17 Review Status

The metadata review lifecycle state of a chunk record.

| Value | Meaning |
|-------|---------|
| `draft` | Chunk metadata has been auto-populated but not reviewed |
| `reviewed` | A human reviewer has inspected the metadata |
| `approved` | Metadata has been approved as correct and complete |
| `rejected` | Chunk has been rejected and must be revised or discarded |

`review_status` tracks metadata review lifecycle.
`approval_state` (§3.14) tracks operational retrieval permission.
These two fields are distinct and serve different purposes.

---

## 3.18 Conflict Type

The type of conflict when two or more sources or chunks assert contradictory content.

| Value | Meaning |
|-------|---------|
| `factual_contradiction` | Two sources state mutually exclusive factual claims |
| `scope_mismatch` | Sources appear to conflict but apply to different scopes (e.g. one product-specific, one general) |
| `temporal_divergence` | Claims reflect different time periods or formulation eras |
| `interpretive_disagreement` | Sources offer different interpretations rather than factual contradiction |
| `provenance_gap` | One source lacks sufficient provenance to resolve the conflict |

---

## 3.19 Duplicate Type

The type of similarity when two or more chunks are identified as duplicates.

| Value | Meaning |
|-------|---------|
| `exact` | Identical text content |
| `format_variant` | Same content in different format (e.g. prose vs table) |
| `version_variant` | Different versions of the same document |
| `near_duplicate` | Highly similar content with minor differences |
| `mirror_rehost` | The same content republished at a different URL or in a different source |

---

## 3.20 Provenance Type

How a metadata field value was determined.

| Value | Meaning |
|-------|---------|
| `extracted` | Automatically extracted from source content |
| `rule_inferred` | Inferred by applying a deterministic rule to other field values |
| `model_suggested` | Suggested by a machine learning model |
| `manual_entered` | Entered by a human reviewer |
| `manual_reviewed` | A model or rule-based value that has been reviewed and confirmed by a human |
| `manual_overridden` | A model or rule-based value replaced by a human reviewer |
| `imported` | Copied from an external structured source |
| `derived` | Computed from other confirmed field values |

---

## 3.21 Answer Labels

Canonical labels describing the epistemic status of an answer or a claim within an answer.

| Value | Meaning |
|-------|---------|
| `well_established` | Supported by multiple strong, corroborating sources |
| `historically_documented` | Documented in conservation, historical, or analytical sources |
| `product_specific` | Specific to a particular product, brand, or modern formulation |
| `case_specific` | Observed in a specific case, artwork, or conservation instance |
| `likely_but_context_dependent` | Probable but varies with context, formulation, or application |
| `mixed_evidence` | Multiple credible sources give different answers |
| `uncertain` | Insufficient evidence to give a confident answer |
| `interpretive` | Based on teaching or interpretive frameworks, not primary evidence |

These labels must be applied to answers and claims where applicable. They must not be collapsed into a single confidence score.

---

# 4. Material Naming Rule

Use the **canonical primary name** for materials in all metadata fields. Aliases are recorded in `vocab/material_alias_map.json` but must not replace canonical names.

## 4.1 Canonical Material Names

| Canonical Name | Common Aliases |
|---------------|---------------|
| `lead_white` | flake white, Cremnitz white, basic lead carbonate, PW1 |
| `zinc_white` | Chinese white, zinc oxide, PW4 |
| `titanium_white` | titanium dioxide, PW6 |
| `ultramarine` | French ultramarine, ultramarine blue, PB29 |
| `yellow_ochre` | ochre, iron yellow ochre, PY43 |
| `raw_sienna` | sienna, PBr7 (raw sienna) |
| `burnt_sienna` | burnt sienna, PBr7 (burnt) |
| `raw_umber` | umber, PBr7 (raw umber) |
| `burnt_umber` | burnt umber, PBr7 (burnt umber) |
| `terre_verte` | green earth, PG23 |
| `ivory_black` | bone black, PBk9 |
| `lamp_black` | carbon black, PBk6 |
| `smalt` | smalt blue, potassium glass blue |
| `verdigris` | copper acetate, green of Greece |
| `viridian` | hydrated chromium oxide, PG18 |
| `cadmium_red` | cadmium red (deep/medium/light), PR108 |
| `alizarin_crimson` | alizarin, PR83 |

Do not collapse distinct materials. `lead_white` and `zinc_white` are distinct materials. `raw_umber` and `burnt_umber` are distinct materials.

## 4.2 Pigment Code Normalization Rule

* Store pigment codes exactly as they appear in the Color Index (e.g. `PW1`, `PW4`, `PB29`, `PBr7`, `PR108`, `PY43`)
* Preserve official casing
* Never infer a pigment code not explicitly present in the source
* If a product contains multiple pigments, preserve the full list
* If a text mentions a pigment name but no code, leave the pigment code field empty and record the name in `materials_mentioned`

---

# 5. QA Questions

Before using this vocabulary in any schema, code, or metadata record:

1. Is every enum value being used present in this document with the exact same casing?
2. Are any values appearing in schemas or code absent from this document?
3. Have any values been renamed or abbreviated relative to the definitions here?
4. Are `case_specificity` (chunk-level) and `case_study_vs_general` (source-level) being kept distinct?
5. Are `review_status` and `approval_state` being kept as separate fields with distinct meaning?
6. Are `conflict_type` and `duplicate_type` being kept distinct?
7. Are answer labels applied in full — not collapsed to a single confidence level?
8. Are material names using canonical forms — not aliases?

---

# 6. Recommended Companion Documents

1. `docs/foundation/metadata_schema.md` — defines which fields use which vocabulary sections
2. `docs/foundation/source_hierarchy.md` — trust tiers referenced by source family and type
3. `docs/policies/metadata_provenance_rules.md` — uses provenance type values from §3.20
4. `docs/policies/conflict_resolution_policy.md` — uses conflict type values from §3.18
5. `docs/policies/deduplication_policy.md` — uses duplicate type values from §3.19
6. `docs/policies/answer_labeling_standard.md` — uses answer label values from §3.21
7. `vocab/controlled_vocabulary.json` — machine-readable implementation of this document
8. `vocab/material_alias_map.json` — alias mappings for §4.1

---

# 7. Adoption Rule

This document is the canonical vocabulary reference for v1 of the Oil Painting Research Assistant.

All metadata records, JSON schemas, Pydantic models, and Python constants must use values defined here.

No new enum value may be introduced in code, schemas, or metadata without first being added to this document and to `vocab/controlled_vocabulary.json`.

If a value must change, the change must propagate to all referencing documents, schemas, models, and existing data records before the change is considered complete.

---
