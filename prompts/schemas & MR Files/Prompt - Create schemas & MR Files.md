You are a senior knowledge-systems architect, schema designer, and data-modeling specialist.

Your task is to generate the machine-readable schema and data-resource files for a project named:

Oil Painting Research Assistant

This project is a provenance-aware, source-aware, review-aware, ChromaDB-based RAG system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

Your job is to write the schema layer and structured support files only.

Do NOT write implementation code in this task.
Do NOT rewrite the prose documentation docs in this task.
Do NOT produce vague placeholders unless explicitly required.
Do NOT invent values that are not consistent with the established documentation.

The schema and structured files must be:
- formal
- internally consistent
- machine-readable
- implementation-aware
- aligned with the foundation docs and policy docs
- suitable for direct later use in Python models, validation, ingestion, chunking, retrieval, evaluation, and ChromaDB indexing

==================================================
1. PRIMARY GOAL
==================================================

Create the machine-readable files for the project under:

- schemas/
- vocab/
- benchmarks/

These files should define the structured backbone for:
- source records
- chunk records
- field provenance
- duplicate clusters
- conflict records
- review records
- approval states
- context packages
- retrieval traces
- answer labels
- controlled vocabulary
- alias maps
- benchmark templates

The structured files must be compatible with a ChromaDB-based hybrid retrieval architecture.

==================================================
2. FILES TO CREATE
==================================================

Create these files:

A. Schemas
- schemas/source_register_schema.json
- schemas/chunk_schema.json
- schemas/field_provenance_schema.json
- schemas/duplicate_cluster_schema.json
- schemas/conflict_record_schema.json
- schemas/review_record_schema.json
- schemas/approval_state_schema.json
- schemas/context_package_schema.json
- schemas/retrieval_trace_schema.json
- schemas/benchmark_template.json
- schemas/restriction_flags.json
- schemas/answer_label_schema.json

B. Vocabulary / structured resources
- vocab/controlled_vocabulary.json
- vocab/material_alias_map.json
- vocab/product_alias_map.json
- vocab/material_ontology_v1.json

C. Benchmark support files
- benchmarks/benchmark_template.json
- benchmarks/benchmark_gold_set_v1.json

==================================================
3. REQUIRED OUTPUT FORMAT
==================================================

When you respond:

1. First provide a short summary of the schema layer as a whole.
2. Then write the files one by one.
3. Use clear file path headers before each file.
4. All JSON must be valid.
5. Keep field names and enum values internally consistent.
6. Do not omit required structures.
7. If a schema is intentionally lightweight, say so explicitly.
8. Do not include code fences inside JSON.
9. Do not add comments inside JSON unless you use a valid field-based documentation pattern.

==================================================
4. REQUIRED CONSISTENCY RULES
==================================================

All schemas and structured resources must align with the project’s documented concepts, especially:

- source hierarchy
- metadata schema
- controlled vocabulary
- chunking rules
- benchmark template
- system prompt logic
- source acquisition policy
- metadata provenance rules
- deduplication policy
- conflict resolution policy
- review workflow
- retrieval policy
- answer labeling standard
- file naming policy

If a field or enum appears in multiple files, use the same exact wording everywhere.

==================================================
5. CHROMADB REQUIREMENT
==================================================

Because the project uses ChromaDB as the vector database, the schemas must be compatible with:

- chunk-level indexing
- stable `chunk_id` keys
- metadata filtering
- local persistent collection storage
- hybrid retrieval with lexical + vector search

This means the chunk schema, context package schema, and retrieval trace schema should support metadata that is practical for ChromaDB storage and filtering.

At minimum, the chunk schema and related retrieval structures should support fields such as:
- chunk_id
- source_id
- source_family
- source_type
- domain
- subdomain
- trust_tier
- review_status
- approval_level
- case_specificity
- historical_period
- artist_or_school
- materials_mentioned
- pigment_codes
- binder_types
- question_types_supported
- duplicate_status
- duplicate_cluster_id
- citability
- ready_for_use
- source_title
- citation_format

Do not write code, but ensure the schema structure works for this architecture.

==================================================
6. SCHEMA EXPECTATIONS
==================================================

### source_register_schema.json
Define the structure for a source-level record.

It should include:
- source identity
- source family/type
- provenance-related operational fields
- review state fields
- corpus lifecycle fields
- materials/pigment/binder fields
- historical and artist/school fields
- summary/retrieval/citation fields
- duplicate/supersession-related fields if appropriate

Be clear about:
- required fields
- field types
- enum-backed fields
- list fields
- nullable fields

### chunk_schema.json
Define the structure for a chunk-level record.

It should include:
- chunk identity
- parent source relationship
- chunk text
- section path
- page range
- token estimate
- chunk type
- domain/subdomain
- materials/pigment/binder fields
- case specificity
- citability
- quality flags
- review status
- approval level
- duplicate fields
- retrieval-weight hints if used

### field_provenance_schema.json
Define the per-field provenance structure.

It should include:
- value
- provenance_type
- provenance_method
- confidence
- review_status
- last_updated_at
- last_updated_by
- override_status
- notes

This should support both source and chunk metadata provenance.

### duplicate_cluster_schema.json
Define:
- cluster_id
- entity_type
- member_ids
- canonical_id
- duplicate_type
- reason
- reviewer
- decision_date
- status

### conflict_record_schema.json
Define:
- conflict_id
- conflict_type
- entity_type
- entity_ids
- summary
- resolution_status
- preferred_value_or_source
- reason
- reviewer
- reviewed_at
- requires_answer_disclosure

### review_record_schema.json
Define:
- review_id
- entity_type
- entity_id
- review_stage
- reviewer
- review_date
- action
- status_before
- status_after
- summary_of_findings
- field_changes
- warnings
- next_action
- notes

### approval_state_schema.json
Define the canonical approval levels and their meanings in machine-readable form.

It should support:
- not_approved
- internal_draft_only
- testing_only
- retrieval_allowed
- live_allowed

### context_package_schema.json
Define the retrieval-to-generation context package.

It should include:
- query
- mode(s)
- selected chunks
- chunk metadata snapshot
- citation data
- conflict notes
- retrieval notes
- assembly timestamp

### retrieval_trace_schema.json
Define the structure of a retrieval trace.

It should include:
- query
- query classification
- inferred mode(s)
- filters applied
- lexical candidates
- vector candidates
- merged candidate pool
- final reranked results
- selected context chunks
- excluded candidates and reasons
- duplicate suppression notes
- conflict notes
- trace timestamp

### benchmark_template.json
Define the conceptual structure of a benchmark record.

It should include:
- benchmark_id
- category
- question
- difficulty
- target_modes
- expected_source_tiers
- must_use_domains
- must_not_confuse
- expected_answer_shape
- evaluation_notes
- gold_claims
- known_uncertainties
- status

### restriction_flags.json
Define structured restriction flags that can be attached to sources/chunks, such as:
- product_only
- not_for_historical_use
- retrieval_only
- citation_caution
- case_specific_only
- needs_manual_review
- not_live_allowed

### answer_label_schema.json
Define the machine-readable structure for answer-status labels.

It should include:
- label
- description
- scope_level
- typical_source_basis
- conflict_compatibility
- display_mode
- allowed_user_facing_phrases

==================================================
7. VOCAB FILE EXPECTATIONS
==================================================

### controlled_vocabulary.json
Create a canonical machine-readable vocabulary file containing the enums and controlled values used across the project.

It should include at minimum:
- source_family
- source_type
- domain
- question_type
- claim_type
- confidence_level
- case_study_vs_general
- review_status
- tables_extracted
- citability
- chunk_type
- approval_level
- conflict_type
- resolution_status
- duplicate_status
- provenance_type
- provenance_method
- override_status
- answer_labels
- historical_period
- artist_or_school
- binder_vocabulary

Structure it cleanly so it can be imported later by validation code.

### material_alias_map.json
Create the canonical material alias map.

It should include:
- canonical_name
- display_name
- category
- pigment_codes_explicit
- aliases_strict
- aliases_soft
- ambiguity_warnings
- notes

Include a strong starter set for:
- lead_white
- zinc_white
- titanium_white
- ultramarine
- natural_ultramarine
- yellow_ochre
- raw_umber
- burnt_umber
- raw_sienna
- burnt_sienna
- terre_verte
- viridian
- verdigris
- smalt
- ivory_black
- mars_black
- cadmium_red
- alizarin_crimson
- cobalt_blue
- linseed
- walnut
- safflower
- poppy
- stand_oil
- alkyd
- resin
- solvent
- drier

### product_alias_map.json
Create a starter structure for mapping product-line naming variants.

This file can be intentionally lighter than material_alias_map.json, but should define a clean pattern for:
- brand
- line
- canonical_product_family
- aliases
- notes

Use a small starter structure rather than pretending to know a complete product universe.

### material_ontology_v1.json
Create a lightweight ontology structure for material relationships.

It should support:
- entity_id or canonical_name
- entity_type
- parent_category
- related_entities
- relationship_type
- notes

Examples of relationship types:
- is_a
- historical_variant_of
- not_equivalent_to
- often_compared_with
- binder_of
- associated_risk
- associated_use

Keep it implementation-friendly rather than overengineered.

==================================================
8. BENCHMARK FILE EXPECTATIONS
==================================================

### benchmarks/benchmark_template.json
Create the machine-readable starter template for a benchmark record or benchmark collection.

### benchmarks/benchmark_gold_set_v1.json
Create a starter gold set aligned with the benchmark template.

Include a representative set across:
- pigments
- binders/media
- conservation
- historical practice
- color theory
- product comparison
- terminology
- integrated reasoning

Examples should cover questions such as:
- difference between lead white, zinc white, and titanium white
- why burnt umber often dries faster
- what smalt is and why it can discolor
- when walnut oil might be preferred over linseed oil
- what stand oil does differently
- why oil paint wrinkles
- what sinking in means
- whether a 15th-century painter would likely use titanium white
- whether verdigris was historically used
- difference between hue, value, and chroma
- why complementary mixtures can go muddy
- how two paints with the same pigment code can behave differently
- difference between opacity and tinting strength
- terre verte in flesh shadows and whether that is historically grounded

Each gold-set record should include:
- must_include
- required_distinctions
- must_not_say
- uncertainty_handling
- citation_expectation
- failure_tags_if_wrong
- status

==================================================
9. JSON DESIGN PREFERENCES
==================================================

Use JSON structures that are:
- human-readable
- implementation-friendly
- stable
- not overly nested unless nesting is genuinely useful

Prefer:
- arrays for enum lists
- objects for structured records
- explicit keys over positional structures

Where a schema file needs to act as a conceptual schema rather than a strict JSON Schema draft spec, that is acceptable — but it must still be valid JSON and clearly structured.

You may choose one of these styles consistently:
1. strict JSON Schema-like structure, or
2. structured project-specific schema definition format

If you choose project-specific schema definitions, keep them highly systematic.

==================================================
10. IMPORTANT CONSISTENCY RULES
==================================================

- Enum values must match across files.
- IDs and naming conventions must align with the file naming policy.
- Provenance fields must align with provenance rules.
- Approval states and review states must align with review workflow.
- Duplicate and conflict fields must align with the relevant policies.
- Benchmark fields must align with the benchmark template foundation doc.
- Answer label values must align with the answer labeling standard.
- Chunk schema must align with ChromaDB filtering and retrieval usage.

==================================================
11. IMPORTANT BEHAVIORAL RULES
==================================================

Do not:
- invent conflicting enum values
- produce invalid JSON
- create placeholders that conflict with the project architecture
- overcomplicate the ontology into an unusable academic structure
- weaken the distinction between product-specific, case-specific, and general evidence
- ignore review state or provenance state
- ignore ChromaDB compatibility
- silently omit key files or structures

Write these as the canonical schema and structured support files for a real research-grade project.
