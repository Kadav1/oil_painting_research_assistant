You are a senior Python engineer, retrieval architect, and knowledge-systems implementer.

Your task is to generate the actual code layer for a project named:

Oil Painting Research Assistant

This project is a provenance-aware, source-aware, review-aware, ChromaDB-based RAG system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

Your job is to implement the codebase from the established documentation and schema layer.

Do NOT redesign the project from scratch.
Do NOT ignore the docs and schemas.
Do NOT build a generic chatbot.
Do NOT write a toy prototype.
Do NOT bypass provenance, review state, source hierarchy, or hybrid retrieval.

The code must be:
- modular
- typed
- maintainable
- local-first
- ChromaDB-based for vector storage
- hybrid-retrieval capable
- consistent with the canonical docs and schemas
- ready for incremental extension

==================================================
1. AUTHORITATIVE INPUTS
==================================================

Assume the following documentation and schema files already exist and are authoritative.

Foundation docs:
- docs/foundation/FOUNDATION_PACK_v1.md
- docs/foundation/source_hierarchy.md
- docs/foundation/metadata_schema.md
- docs/foundation/controlled_vocabulary.md
- docs/foundation/chunking_rules.md
- docs/foundation/benchmark_template.md
- docs/foundation/system_prompt_v1.md

Policy docs:
- docs/policies/source_acquisition_policy.md
- docs/policies/metadata_provenance_rules.md
- docs/policies/deduplication_policy.md
- docs/policies/conflict_resolution_policy.md
- docs/policies/review_workflow.md
- docs/policies/retrieval_policy_v1.md
- docs/policies/answer_labeling_standard.md
- docs/policies/file_naming_policy.md

Schemas / machine-readable files:
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

Vocabulary / resources:
- vocab/controlled_vocabulary.json
- vocab/material_alias_map.json
- vocab/product_alias_map.json
- vocab/material_ontology_v1.json

Benchmarks:
- benchmarks/benchmark_template.json
- benchmarks/benchmark_gold_set_v1.json

Your implementation must align with those files.
If the docs and schemas imply a rule, follow that rule.
Do not invent contradictory enums, statuses, or field names.

==================================================
2. PRIMARY GOAL
==================================================

Generate the Python codebase for the project, including:

1. typed data models
2. config/settings
3. storage layer
4. ingestion support
5. chunking layer
6. ChromaDB indexing layer
7. lexical index layer
8. hybrid retrieval
9. reranking and diversity control
10. citation assembly
11. answer-generation pipeline
12. evaluation harness
13. CLI
14. local API
15. tests
16. README

The code must be designed for real use, not only demonstration.

==================================================
3. REQUIRED ARCHITECTURE
==================================================

Use this project structure unless you justify a small improvement clearly:

oil_painting_research_assistant/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── oil_painting_rag/
│       ├── __init__.py
│       ├── config.py
│       ├── cli.py
│       ├── api.py
│       ├── logging_utils.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── source_models.py
│       │   ├── chunk_models.py
│       │   ├── provenance_models.py
│       │   ├── retrieval_models.py
│       │   └── benchmark_models.py
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── filesystem_store.py
│       │   ├── metadata_store.py
│       │   └── register_store.py
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── capture.py
│       │   ├── loader.py
│       │   └── source_registry.py
│       ├── chunking/
│       │   ├── __init__.py
│       │   ├── chunker.py
│       │   ├── table_chunker.py
│       │   └── chunk_validators.py
│       ├── indexing/
│       │   ├── __init__.py
│       │   ├── embeddings.py
│       │   ├── chroma_index.py
│       │   ├── lexical_index.py
│       │   └── index_manager.py
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── classifier.py
│       │   ├── filters.py
│       │   ├── hybrid_retriever.py
│       │   ├── reranker.py
│       │   ├── diversity.py
│       │   └── citation_assembler.py
│       ├── generation/
│       │   ├── __init__.py
│       │   ├── prompt_builder.py
│       │   ├── answerer.py
│       │   └── mode_router.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── benchmark_runner.py
│       │   ├── scorer.py
│       │   └── failure_logger.py
│       ├── policies/
│       │   ├── __init__.py
│       │   ├── source_policy.py
│       │   ├── provenance_policy.py
│       │   ├── retrieval_policy.py
│       │   └── conflict_policy.py
│       └── utils/
│           ├── __init__.py
│           ├── text_utils.py
│           ├── citation_utils.py
│           ├── enum_utils.py
│           └── hash_utils.py
└── tests/

==================================================
4. CHROMADB REQUIREMENT
==================================================

You MUST use ChromaDB as the vector database.

Use:
- `chromadb`
- `chromadb.PersistentClient`
- stable `chunk_id` values as document IDs
- persistent local storage under something like:
  `data/indexes/chroma/`

The Chroma layer must support:
- collection creation
- collection existence checks
- upsert by `chunk_id`
- delete by `chunk_id`
- delete by `source_id`
- filtered similarity search
- collection rebuild
- inspection/debugging
- metadata storage for query-time filters

Do not treat ChromaDB as an optional add-on.
It must be part of the real operational design.

==================================================
5. HYBRID RETRIEVAL REQUIREMENT
==================================================

Do not build vector-only retrieval.

Implement hybrid retrieval with:
- ChromaDB vector search
- lexical/BM25 retrieval
- metadata filtering
- reranking
- diversity control
- duplicate suppression
- conflict-aware context assembly

The retrieval flow should support:
1. query classification
2. mode inference
3. metadata filters
4. vector candidate retrieval
5. lexical candidate retrieval
6. candidate merge
7. reranking
8. diversity enforcement
9. context packaging
10. citation packaging

==================================================
6. METADATA + PROVENANCE REQUIREMENT
==================================================

The code must honor the schema and provenance rules.

Support:
- source-level metadata
- chunk-level metadata
- field-level provenance
- review state
- approval level
- duplicate status
- duplicate clusters
- conflict records
- answer labeling support

Important:
- reviewed and unreviewed metadata must remain distinguishable
- model-suggested fields must not silently become hard truth
- critical fields must support provenance and review information
- code should align with the documented enums and status values

==================================================
7. APPROVAL / REVIEW REQUIREMENT
==================================================

The code must support the distinction between:
- draft/internal
- testing-only
- retrieval-allowed
- live-allowed

The indexing and retrieval layers must be able to respect these distinctions.

For example:
- live retrieval should exclude chunks not approved for live use by default
- testing mode may include broader data if explicitly requested

==================================================
8. REQUIRED IMPLEMENTATION DETAILS
==================================================

Use:
- Python 3.11+
- pathlib
- type hints
- Pydantic models or dataclasses
- structured logging
- Typer for CLI
- FastAPI for local API
- ChromaDB for vectors
- rank-bm25 or equivalent for lexical retrieval
- sentence-transformers or a pluggable embedding backend
- pandas where useful for register/log handling

Design major backends as swappable interfaces where practical:
- embedding backend
- answer-generation backend

But do not make the project abstract for abstraction’s sake.

==================================================
9. DATA MODEL REQUIREMENTS
==================================================

Implement data models that align with the schemas.

At minimum:
- source metadata model
- chunk metadata model
- field provenance model
- duplicate cluster model
- conflict record model
- review record model
- approval state model
- retrieval request/response models
- context package model
- retrieval trace model
- benchmark model
- answer label model

Use the canonical field names and enum values from the schema/vocab layer.

==================================================
10. STORAGE REQUIREMENTS
==================================================

Implement storage for:
- raw source files
- normalized markdown/text
- metadata JSON sidecars
- chunk files
- register CSVs
- logs
- benchmark results
- retrieval traces

Use filesystem-based local storage with clear path handling.

==================================================
11. CHUNKING REQUIREMENTS
==================================================

Implement semantic chunking, aligned with the docs.

Support:
- prose chunks
- table chunks
- glossary chunks
- figure-note chunks
- mixed chunks

Chunking behavior should:
- preserve semantic units
- preserve section paths
- preserve citation-relevant context
- attach chunk metadata
- minimize harmful overlap
- support configurable limits
- flag low-quality extraction

==================================================
12. RERANKING + DIVERSITY REQUIREMENTS
==================================================

Reranking should consider:
- semantic relevance
- lexical relevance
- source trust tier
- review state
- approval level
- domain fit
- question-type fit
- case specificity
- freshness where relevant
- duplicate status
- chunk quality flags
- citation readiness

Diversity logic should prevent:
- one source flooding the answer context
- duplicate clusters dominating context
- repetitive product boilerplate dominating results

==================================================
13. CITATION REQUIREMENTS
==================================================

Implement citation assembly using available metadata.

Each citation-ready chunk should support:
- source title
- short citation text
- page range or section path
- source URL if available
- source type
- case specificity if relevant

Do not hallucinate citations.
If citation support is incomplete, the system must degrade gracefully.

==================================================
14. GENERATION REQUIREMENTS
==================================================

Implement the answer-generation layer so it reflects the system prompt logic and answer-labeling standard.

Support modes:
- Studio
- Conservation
- Art History
- Color Analysis
- Product Comparison

The answer builder should internally support:
- evidence framing
- source-type awareness
- conflict-aware synthesis
- uncertainty handling
- answer labeling logic

You may implement the LLM/generation backend as a pluggable interface if no concrete model is mandated.

==================================================
15. EVALUATION REQUIREMENTS
==================================================

Implement evaluation support using the benchmark files.

At minimum:
- load benchmark records
- run retrieval + answer generation over benchmark questions
- store answers
- store retrieval traces
- attach failure tags manually or via scoring stubs
- support inspection of failed cases

Support failure categories such as:
- wrong pigment identity
- wrong pigment code
- case-study overgeneralization
- product/history confusion
- weak uncertainty handling
- retrieval mismatch
- source-tier misuse
- citation failure
- overconfident synthesis
- scope collapse
- terminology confusion

==================================================
16. CLI REQUIREMENTS
==================================================

Provide a Typer CLI with commands such as:
- ingest-source
- normalize-source
- chunk-source
- index-corpus
- rebuild-chroma
- search
- answer
- inspect-retrieval
- inspect-chroma
- run-benchmark
- validate-metadata
- export-trace

The CLI should be practical and readable.

==================================================
17. API REQUIREMENTS
==================================================

Provide a local FastAPI app with endpoints such as:
- /search
- /answer
- /inspect
- /benchmark
- /index/status
- /index/rebuild

Keep the API useful but not bloated.

==================================================
18. TEST REQUIREMENTS
==================================================

Write tests for:
- core models
- metadata/provenance handling
- chunking logic
- Chroma indexing logic
- lexical retrieval
- hybrid retrieval
- reranking basics
- benchmark loading

Tests should be realistic and useful, not only smoke tests.

==================================================
19. README REQUIREMENTS
==================================================

Write a README that explains:
- project purpose
- architecture
- folder structure
- required docs/schemas
- install
- configuration
- ChromaDB usage
- CLI commands
- API usage
- workflow overview
- limitations
- development notes

==================================================
20. IMPLEMENTATION ORDER
==================================================

Implement in this order:

1. architecture summary
2. data models
3. storage layer
4. ingestion helpers
5. chunking layer
6. ChromaDB indexing layer
7. lexical index layer
8. hybrid retrieval layer
9. reranking + diversity
10. citation assembly
11. generation layer
12. evaluation layer
13. CLI/API
14. tests
15. README

==================================================
21. OUTPUT STYLE
==================================================

When you respond:

1. First provide a concise architecture summary.
2. Then provide the files one by one.
3. Use clear filename headers.
4. Ensure imports are complete.
5. Do not omit critical logic with vague TODOs.
6. If any part is intentionally simplified, say so explicitly.
7. Keep the code internally consistent.
8. Keep naming aligned with the docs and schemas.

==================================================
22. IMPORTANT BEHAVIORAL RULES
==================================================

Do not:
- ignore the docs/schemas and invent a different architecture
- collapse provenance into a flat trust field
- treat all metadata as equally reliable
- skip lexical retrieval
- skip reranking
- skip review-state handling
- output fake citations
- build only notebook code
- silently weaken source-tier rules
- replace ChromaDB with another vector store
- use different enum names from the schema layer

Build this as if it will be used to answer real historical, material, and product questions where accuracy matters.
