You are a senior Python engineer and project scaffolding specialist.

Your task is to generate a safe, production-minded script that creates the full folder and file structure for a project named:

oil_painting_research_assistant

The goal is to scaffold the entire repository structure for a provenance-aware RAG system focused on:
- oil paint chemistry
- pigments
- binders/media
- conservation
- historical painting practice
- color theory
- manufacturer product data

==================================================
1. PRIMARY REQUIREMENT
==================================================

Generate a Python 3.11+ script that creates the full folder structure and placeholder files for the project.

Requirements:
- use pathlib
- be safe to run multiple times
- do NOT overwrite existing files
- create missing directories
- create missing files as empty placeholders or minimal starter files
- print a summary of:
  - created directories
  - created files
  - skipped existing files
- keep the script readable and maintainable

If useful, you may also provide an optional Bash version after the Python version, but the Python version is required.

==================================================
2. OUTPUT REQUIREMENTS
==================================================

When you respond:

1. First give a short summary of the scaffold strategy.
2. Then provide the full Python script in one block.
3. The script must be complete and runnable.
4. Use comments where logic is non-obvious.
5. Do not omit imports.
6. Do not leave critical TODO placeholders in the script logic.
7. After the script, provide a short note explaining what it creates.

==================================================
3. SAFETY RULES
==================================================

- Do not delete anything.
- Do not overwrite existing files.
- If a file already exists, leave it untouched and report it as skipped.
- Use UTF-8 when writing files.
- Prefer minimal placeholder content over blank files for important top-level files.
- Create `.gitkeep` files only where needed to preserve empty directories.
- Keep the script local-only. Do not require network access.

==================================================
4. ROOT PROJECT NAME
==================================================

Create everything under this root folder:

oil_painting_research_assistant/

==================================================
5. EXACT PROJECT STRUCTURE TO CREATE
==================================================

Create this exact structure:

oil_painting_research_assistant/
├── docs/
│   ├── foundation/
│   │   ├── FOUNDATION_PACK_v1.md
│   │   ├── source_hierarchy.md
│   │   ├── metadata_schema.md
│   │   ├── controlled_vocabulary.md
│   │   ├── chunking_rules.md
│   │   ├── benchmark_template.md
│   │   └── system_prompt_v1.md
│   │
│   ├── policies/
│   │   ├── source_acquisition_policy.md
│   │   ├── metadata_provenance_rules.md
│   │   ├── deduplication_policy.md
│   │   ├── conflict_resolution_policy.md
│   │   ├── review_workflow.md
│   │   ├── retrieval_policy_v1.md
│   │   ├── answer_labeling_standard.md
│   │   └── file_naming_policy.md
│   │
│   └── roadmap/
│       ├── CHANGELOG.md
│       └── versioning_policy.md
│
├── schemas/
│   ├── source_register_schema.json
│   ├── chunk_schema.json
│   ├── field_provenance_schema.json
│   ├── duplicate_cluster_schema.json
│   ├── conflict_record_schema.json
│   ├── review_record_schema.json
│   ├── approval_state_schema.json
│   ├── context_package_schema.json
│   ├── retrieval_trace_schema.json
│   ├── benchmark_template.json
│   ├── restriction_flags.json
│   └── answer_label_schema.json
│
├── vocab/
│   ├── material_alias_map.json
│   ├── controlled_vocabulary.json
│   ├── product_alias_map.json
│   └── material_ontology_v1.json
│
├── benchmarks/
│   ├── benchmark_gold_set_v1.json
│   ├── benchmark_template.json
│   └── benchmark_runs/
│       └── .gitkeep
│
├── data/
│   ├── raw/
│   │   ├── museum/
│   │   │   └── .gitkeep
│   │   ├── pigments/
│   │   │   └── .gitkeep
│   │   ├── manufacturers/
│   │   │   └── .gitkeep
│   │   ├── color_theory/
│   │   │   └── .gitkeep
│   │   ├── historical/
│   │   │   └── .gitkeep
│   │   └── scientific/
│   │       └── .gitkeep
│   │
│   ├── clean/
│   │   ├── markdown/
│   │   │   └── .gitkeep
│   │   ├── tables/
│   │   │   └── .gitkeep
│   │   └── metadata/
│   │       └── .gitkeep
│   │
│   ├── chunks/
│   │   ├── text/
│   │   │   └── .gitkeep
│   │   ├── tables/
│   │   │   └── .gitkeep
│   │   └── metadata/
│   │       └── .gitkeep
│   │
│   ├── indexes/
│   │   ├── chroma/
│   │   │   └── .gitkeep
│   │   ├── lexical/
│   │   │   └── .gitkeep
│   │   └── cache/
│   │       └── .gitkeep
│   │
│   ├── register/
│   │   ├── source_register.csv
│   │   ├── acquisition_log.csv
│   │   ├── qa_log.csv
│   │   ├── duplicate_review_log.csv
│   │   ├── conflict_review_log.csv
│   │   ├── source_review_log.csv
│   │   ├── metadata_review_log.csv
│   │   ├── chunk_review_log.csv
│   │   └── release_approval_log.csv
│   │
│   └── logs/
│       ├── retrieval_failure_log.csv
│       ├── source_similarity_report.json
│       ├── chunk_similarity_report.json
│       ├── open_conflicts_report.json
│       ├── retrieval_debug_report.json
│       └── recheck_queue.json
│
├── src/
│   └── oil_painting_rag/
│       ├── __init__.py
│       ├── config.py
│       ├── cli.py
│       ├── api.py
│       ├── logging_utils.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── source_models.py
│       │   ├── chunk_models.py
│       │   ├── provenance_models.py
│       │   ├── retrieval_models.py
│       │   └── benchmark_models.py
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── filesystem_store.py
│       │   ├── metadata_store.py
│       │   └── register_store.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── capture.py
│       │   ├── loader.py
│       │   └── source_registry.py
│       │
│       ├── chunking/
│       │   ├── __init__.py
│       │   ├── chunker.py
│       │   ├── table_chunker.py
│       │   └── chunk_validators.py
│       │
│       ├── indexing/
│       │   ├── __init__.py
│       │   ├── embeddings.py
│       │   ├── chroma_index.py
│       │   ├── lexical_index.py
│       │   └── index_manager.py
│       │
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── classifier.py
│       │   ├── filters.py
│       │   ├── hybrid_retriever.py
│       │   ├── reranker.py
│       │   ├── diversity.py
│       │   └── citation_assembler.py
│       │
│       ├── generation/
│       │   ├── __init__.py
│       │   ├── prompt_builder.py
│       │   ├── answerer.py
│       │   └── mode_router.py
│       │
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── benchmark_runner.py
│       │   ├── scorer.py
│       │   └── failure_logger.py
│       │
│       ├── policies/
│       │   ├── __init__.py
│       │   ├── source_policy.py
│       │   ├── provenance_policy.py
│       │   ├── retrieval_policy.py
│       │   └── conflict_policy.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── text_utils.py
│           ├── citation_utils.py
│           ├── enum_utils.py
│           └── hash_utils.py
│
├── tests/
│   ├── test_models.py
│   ├── test_chunking.py
│   ├── test_retrieval.py
│   ├── test_reranking.py
│   ├── test_provenance.py
│   └── test_benchmarks.py
│
├── pyproject.toml
├── README.md
└── .env.example

==================================================
6. FILE CONTENT RULES
==================================================

Create files with these content rules:

A. Markdown docs:
- create minimal starter content
- include an H1 title based on the filename
- include a one-line placeholder note like:
  "Canonical draft placeholder."

B. JSON files:
- create valid JSON, not empty text files
- use `{}` for schema/map placeholders unless the filename already implies an array
- keep them valid JSON

C. CSV files:
- create empty files with just a newline
- do not invent headers unless explicitly justified

D. Python files:
- create minimal valid Python files
- for `__init__.py`, create either empty file or short module docstring
- for module files, create a short module docstring only

E. Top-level files:
- `README.md`: create a minimal project title and one short description
- `pyproject.toml`: create a minimal valid starter file
- `.env.example`: create a minimal placeholder comment

==================================================
7. IMPLEMENTATION PREFERENCES
==================================================

Use:
- `pathlib.Path`
- a helper for creating directories
- a helper for creating files only if missing
- clean separation between:
  - directories to create
  - files to create
  - file contents by extension or exact filename

Make the script easy to modify later.

==================================================
8. OPTIONAL NICE-TO-HAVES
==================================================

If useful, include:
- a dry-run flag
- a configurable root path
- a final tree-style summary printout

But do not make the script overly complicated.

==================================================
9. IMPORTANT BEHAVIOR RULES
==================================================

Do not:
- compress the structure into fewer folders
- rename files
- drop placeholder files
- use a different root package name
- overwrite existing files
- leave JSON files invalid
- leave the script incomplete

Generate the full scaffold exactly as specified.
