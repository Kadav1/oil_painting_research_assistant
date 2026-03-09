You are a senior Python engineer, retrieval architect, and RAG systems designer.

Your task is to design and implement a production-minded Retrieval-Augmented Generation (RAG) system for a project called:

Oil Painting Research Assistant

This assistant is a specialist research system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

The system must be built as a trustworthy, provenance-aware, citation-friendly RAG application.

Do NOT build a generic chatbot.
Do NOT build a toy demo.
Do NOT ignore governance, provenance, review-state handling, or source hierarchy.

The system must reflect the following project rules:

1. Source hierarchy matters.
2. Metadata provenance matters.
3. Case studies must not be flattened into universal rules.
4. Product-specific claims must not be presented as universal chemistry.
5. The assistant must distinguish:
   - conservation evidence
   - general technical reference
   - product-specific information
   - historical documentation
   - teaching/interpretive explanation
6. The system must support uncertainty explicitly.
7. The corpus must remain auditable and reviewable.

You should assume the project already has the following policy/architecture documents defined:
- Foundation Pack v1
- Source Acquisition Policy
- Metadata Provenance Rules
- Deduplication Policy
- Conflict Resolution Policy
- Review Workflow
- Retrieval Policy v1
- Answer Labeling Standard

Your implementation must be compatible with those documents.

==================================================
1. PRIMARY GOAL
==================================================

Build the full RAG backbone for the Oil Painting Research Assistant, including:

1. corpus storage design
2. chunk storage and indexing
3. metadata-aware retrieval
4. hybrid search
5. reranking
6. citation assembly
7. answer generation pipeline
8. evaluation harness
9. CLI and/or local API interface
10. tests and documentation

The system should be able to answer questions like:
- Why does zinc white often raise concerns in oil painting?
- What is the difference between lead white, zinc white, and titanium white?
- Would a 15th-century painter have used titanium white?
- Why do my shadows turn muddy?
- How can two paints with the same pigment code behave differently?
- What does “sinking in” mean in oil painting?

==================================================
2. REQUIRED DESIGN PRINCIPLES
==================================================

The system must be:

- modular
- typed
- provenance-aware
- source-aware
- review-state aware
- citation-capable
- testable
- maintainable
- explicit about uncertainty
- local-first where practical

It must not:
- hallucinate metadata
- hallucinate citations
- treat low-trust sources as equal to high-trust ones
- rely on naive vector search alone
- merge all source types into one undifferentiated retrieval space
- treat unreviewed inferred metadata as hard truth
- assume product data is timeless
- replace ChromaDB with another vector database unless explicitly justified

==================================================
3. CHROMADB REQUIREMENT
==================================================

You MUST use ChromaDB as the vector database.

Use:
- `chromadb`
- persistent local storage
- collection-based organization
- metadata filtering at query time
- stable `chunk_id` values as document IDs

The implementation should use a persistent Chroma client, such as:
- `chromadb.PersistentClient(...)`

Store the Chroma database under a predictable local path, for example:
- `data/indexes/chroma/`

The vector layer must:
- persist embeddings and metadata in ChromaDB
- support upsert/update by `chunk_id`
- support deletion by `chunk_id` or `source_id`
- support collection rebuild
- support filtering on metadata fields
- support retrieval inspection/debugging

Do not use ChromaDB only as a placeholder. It must be a real operational part of the design.

==================================================
4. CHROMADB COLLECTION DESIGN
==================================================

Design the ChromaDB layer explicitly.

At minimum, define a primary collection for chunks, such as:
- `oil_painting_chunks`

Optionally justify additional collections if useful, for example:
- `oil_painting_chunks_live`
- `oil_painting_chunks_testing`
- `oil_painting_glossary`
- `oil_painting_products`

But do not fragment collections unnecessarily.

Each Chroma record should include:
- `id` = `chunk_id`
- `document` = chunk text
- `metadata` = reviewed, normalized chunk/source metadata used for filtering and ranking

Metadata stored in Chroma should include at minimum:
- `source_id`
- `source_family`
- `source_type`
- `domain`
- `subdomain`
- `trust_tier`
- `review_status`
- `approval_level`
- `case_specificity`
- `historical_period`
- `artist_or_school`
- `materials_mentioned`
- `pigment_codes`
- `binder_types`
- `question_types_supported`
- `duplicate_status`
- `duplicate_cluster_id`
- `citability`
- `ready_for_use`
- `source_title`
- `citation_format`

Design the metadata encoding so it works cleanly with ChromaDB filters and is still practical to inspect.

==================================================
5. PRIMARY ARCHITECTURE REQUIREMENTS
==================================================

Build the system with these major components:

A. Source / document layer
- raw source storage
- normalized source storage
- source-level metadata
- provenance sidecars

B. Chunk layer
- chunk generation
- chunk metadata
- chunk provenance
- chunk review state
- chunk storage

C. Index layer
- ChromaDB vector index
- lexical/BM25 index
- optional structured filter layer
- reranker layer

D. Retrieval layer
- question classification
- metadata filtering
- hybrid retrieval
- reranking
- diversity control
- citation context assembly

E. Generation layer
- answer prompt builder
- source-aware response generation
- mode handling
- citation rendering
- uncertainty and evidence framing

F. Evaluation layer
- benchmark runner
- scoring harness
- failure logging
- answer comparison support
- retrieval trace inspection

==================================================
6. SOURCE-AWARE RETRIEVAL RULES
==================================================

The system must implement retrieval that respects source hierarchy and metadata.

Required behaviors:

1. Use source tiers in ranking.
2. Allow filtering by:
   - source_family
   - source_type
   - domain
   - question_type
   - historical_period
   - artist_or_school
   - pigment_codes
   - binder_types
   - review_status
   - case_specificity
   - approval_level
3. Prefer reviewed metadata over unreviewed inferred metadata.
4. Prefer high-trust sources for historical and conservation claims.
5. Prefer manufacturer sources for modern product-specific questions.
6. Enforce source diversity so retrieval is not flooded by multiple near-duplicate chunks.
7. Distinguish between:
   - case-specific evidence
   - general reference
   - product specification
   - interpretive explanation
8. Support recency weighting only where appropriate, especially for manufacturer/product data.

==================================================
7. REQUIRED ANSWER BEHAVIOR
==================================================

The answer pipeline must support these modes:

- Studio Mode
- Conservation Mode
- Art History Mode
- Color Analysis Mode
- Product Comparison Mode

The answer builder must produce responses that, when possible, follow this structure:

A. Direct answer
B. Why / explanation
C. What kind of source supports this
D. Limits / uncertainty
E. Practical takeaway

The system must explicitly label or at least internally reason about whether evidence is:
- well established
- historically documented
- product-specific
- case-specific
- likely but context-dependent
- mixed evidence
- uncertain

==================================================
8. REQUIRED METADATA SUPPORT
==================================================

The system must work with source-level and chunk-level metadata compatible with the project’s schema.

At minimum, support these source-level fields:
- source_id
- title
- short_title
- source_family
- source_type
- institution_or_publisher
- author
- publication_year
- edition_or_version
- source_url
- access_type
- raw_file_name
- raw_file_path
- capture_date
- capture_method
- trust_tier
- authority_score
- extractability_score
- coverage_value_score
- density_score
- priority_score
- domain
- subdomain
- materials_mentioned
- pigment_codes
- binder_types
- historical_period
- artist_or_school
- question_types_supported
- raw_captured
- normalized_text_created
- tables_extracted
- metadata_attached
- qa_reviewed
- chunked
- indexed
- ready_for_use
- case_study_vs_general
- claim_types_present
- confidence_level
- limitations_notes
- license_or_usage_notes
- citation_format
- summary
- retrieval_notes
- internal_notes

At minimum, support these chunk-level fields:
- chunk_id
- source_id
- chunk_index
- chunk_title
- section_path
- page_range
- text
- token_estimate
- chunk_type
- domain
- subdomain
- materials_mentioned
- pigment_codes
- binder_types
- historical_period
- artist_or_school
- question_types_supported
- claim_types_present
- case_specificity
- citability
- retrieval_weight_hint
- quality_flags
- review_status
- approval_level
- duplicate_status
- duplicate_cluster_id

==================================================
9. PROVENANCE REQUIREMENTS
==================================================

Every important metadata field must be provenance-aware.

Support:
- provenance_type
- provenance_method
- confidence
- review_status
- last_updated_at
- last_updated_by
- override_status

Allowed provenance types should include:
- extracted
- rule_inferred
- model_suggested
- manual_entered
- manual_reviewed
- manual_overridden
- imported
- derived

The system must preserve field history for overridden values.

Unreviewed model-suggested or inferred fields must not be treated as equally trusted with reviewed factual fields.

==================================================
10. CHUNKING REQUIREMENTS
==================================================

Implement chunking by semantic unit, not arbitrary size alone.

Support chunk types such as:
- prose
- table
- glossary
- figure_note
- mixed

Chunking rules:
- split by heading changes
- split by material/topic change
- split by product change
- preserve coherent explanations
- keep tables separate when useful
- attach sufficient metadata to every chunk
- flag low-quality extraction

Make chunking configurable.

==================================================
11. HYBRID RETRIEVAL REQUIREMENTS
==================================================

Do not rely on ChromaDB vector search alone.

Implement hybrid retrieval with:
- ChromaDB vector search
- lexical/BM25 search
- metadata filtering
- reranking

Support a retrieval flow like:
1. classify query
2. infer likely mode
3. identify candidate domains
4. apply filters
5. retrieve ChromaDB vector candidates
6. retrieve lexical candidates
7. merge candidates
8. rerank
9. enforce diversity
10. assemble context package

==================================================
12. CHROMADB INDEXING REQUIREMENTS
==================================================

Implement a dedicated ChromaDB index manager.

It should support:
- collection creation
- collection existence checks
- chunk upsert
- chunk delete
- delete by source_id
- rebuild collection
- full reindex
- partial incremental index update
- metadata-only update when possible
- retrieval with filters
- retrieval debug inspection

Indexing rules:
- by default, only chunks approved for retrieval should be indexed into the live collection
- optionally support a testing collection for draft/testing chunks
- preserve `chunk_id` as the stable Chroma document ID
- preserve enough metadata in Chroma for prefiltering and inspection

==================================================
13. RERANKING REQUIREMENTS
==================================================

Implement reranking that considers:
- semantic relevance
- keyword relevance
- source trust tier
- review status
- domain fit
- question-type fit
- case specificity
- freshness where relevant
- source diversity
- chunk quality flags
- citation readiness

Do not let five near-duplicate chunks from one source dominate the final context.

==================================================
14. CITATION REQUIREMENTS
==================================================

The system must support citation-ready answers.

Each retrieved chunk should preserve enough information to cite:
- source title
- short citation text
- page range or section if available
- source URL if applicable
- source type and case-specificity if relevant

Do not hallucinate citations.
If citation data is missing, surface the limitation internally and degrade gracefully.

==================================================
15. EVALUATION REQUIREMENTS
==================================================

Build an evaluation harness based on benchmark questions.

Support:
- benchmark JSON loading
- batch evaluation
- answer logging
- scoring stub or rubric integration
- failure categorization
- retrieval inspection

Benchmark categories should include:
- pigments
- binders/media
- conservation
- historical practice
- color theory
- product comparison
- terminology

Failure taxonomy should include:
- wrong pigment identity
- wrong pigment code
- case-study overgeneralization
- product/history confusion
- weak uncertainty handling
- retrieval mismatch
- source-tier misuse
- citation failure

==================================================
16. INTERFACE REQUIREMENTS
==================================================

Provide a practical interface.

At minimum include:
- CLI using Typer
- local API using FastAPI or similar

CLI commands should include examples like:
- ingest-source
- chunk-source
- index-corpus
- rebuild-chroma
- search
- answer
- inspect-retrieval
- inspect-chroma
- run-benchmark
- validate-metadata
- refresh-index

API endpoints may include:
- /search
- /answer
- /inspect
- /benchmark
- /index/status
- /index/rebuild

==================================================
17. SUGGESTED PROJECT STRUCTURE
==================================================

Use a maintainable structure like:

oil_painting_rag/
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
├── data/
│   ├── raw/
│   ├── clean/
│   ├── chunks/
│   ├── indexes/
│   │   ├── chroma/
│   │   └── lexical/
│   ├── metadata/
│   ├── benchmarks/
│   └── register/
└── tests/

You may improve this structure if you justify it clearly.

==================================================
18. TECHNICAL REQUIREMENTS
==================================================

Use:
- Python 3.11+
- type hints
- pathlib
- Pydantic models or dataclasses
- structured logging

Reasonable libraries may include:
- typer
- fastapi
- pydantic
- pandas
- numpy
- scikit-learn
- rank-bm25 or equivalent
- sentence-transformers or pluggable embedding backend
- chromadb
- rapidfuzz

Design embedding and generation backends as swappable interfaces.

Do not hardwire the system to a single vendor API.

==================================================
19. CHROMADB IMPLEMENTATION DETAILS
==================================================

The ChromaDB layer should:
- use a persistent client
- create collections explicitly
- upsert by chunk ID
- store metadata in Chroma for filters
- allow filtered similarity search
- return distances/scores plus metadata
- support collection reset/rebuild
- be wrapped behind a clean repository/index interface

Design for local-first usage.
Assume the database should run embedded/persistent on disk rather than requiring a separate hosted service.

If there are limitations in ChromaDB metadata filtering or list handling, design a practical encoding strategy and document it clearly.

==================================================
20. IMPLEMENTATION ORDER
==================================================

Implement in this order:

1. architecture summary
2. data models
3. storage layer
4. chunking layer
5. ChromaDB indexing layer
6. lexical indexing layer
7. retrieval layer
8. generation layer
9. evaluation layer
10. CLI/API
11. tests
12. README

==================================================
21. REQUIRED OUTPUT STYLE
==================================================

When you respond:

1. First provide a concise architecture summary.
2. Then provide the project files one by one.
3. Use clear filename headers.
4. Ensure imports are complete.
5. Do not omit critical logic with vague TODOs.
6. If any part is intentionally simplified, say so explicitly.
7. Keep the code internally consistent.

==================================================
22. IMPORTANT BEHAVIORAL RULES
==================================================

Do not:
- collapse provenance into one flat trust state
- pretend all metadata is equally reliable
- skip reranking
- skip lexical retrieval
- skip source-tier logic
- output fake citations
- build only a notebook demo
- ignore failure analysis
- silently choose defaults that weaken truthfulness
- use ChromaDB only as a stub while the real logic happens elsewhere

Build this as if it will be used to answer real material, historical, and product questions where accuracy matters.
