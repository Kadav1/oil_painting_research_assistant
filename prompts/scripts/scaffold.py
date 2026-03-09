#!/usr/bin/env python3
"""
Scaffold script for oil_painting_research_assistant project.

Creates full folder structure and placeholder files safely.
Idempotent: safe to run multiple times.
"""

import pathlib
import json
import sys


def create_directory(base: pathlib.Path, path: str) -> pathlib.Path:
    """Create a directory if it doesn't exist."""
    full_path = base / path
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def create_file_if_missing(base: pathlib.Path, path: str, content: str) -> tuple:
    """
    Create a file only if it doesn't exist.
    Returns tuple of (success: bool, path: pathlib.Path)
    """
    full_path = base / path
    if full_path.exists():
        return False, full_path
    
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True, full_path


def create_markdown_file(base: pathlib.Path, path: str) -> tuple:
    """Create markdown file with H1 title and placeholder note."""
    filename = pathlib.Path(path).name
    content = f"# {filename}\n\nCanonical draft placeholder.\n"
    return create_file_if_missing(base, path, content)


def create_json_file(base: pathlib.Path, path: str, content: dict) -> tuple:
    """Create JSON file with valid content."""
    full_path = base / path
    if full_path.exists():
        return False, full_path
    
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    return True, full_path


def create_csv_file(base: pathlib.Path, path: str) -> tuple:
    """Create empty CSV file with at least a newline."""
    full_path = base / path
    if full_path.exists():
        return False, full_path
    
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write('\n')
    return True, full_path


def create_python_init(base: pathlib.Path, path: str) -> tuple:
    """Create __init__.py with module docstring."""
    full_path = base / path
    if full_path.exists():
        return False, full_path
    
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f'# Module: {path}\n\n"""\nThis module provides {path.split("/")[-1].replace("_", " ")} functionality.\n"""\n\n')
    return True, full_path


def create_python_module(base: pathlib.Path, path: str, docstring: str) -> tuple:
    """Create Python module with docstring."""
    filename = pathlib.Path(path).name
    content = f'# Module: {filename}\n\n"""\nProvides {docstring}.\n"""\n\n'
    return create_file_if_missing(base, path, content)


def create_gitkeep(base: pathlib.Path, path: str) -> tuple:
    """Create .gitkeep file for empty directories."""
    full_path = base / path
    if full_path.exists():
        return False, full_path
    
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write('')
    return True, full_path


# Project structure definition
ROOT_NAME = 'oil_painting_research_assistant'

# All directories to create
DIRECTORIES = [
    'docs/foundation',
    'docs/policies',
    'docs/roadmap',
    'schemas',
    'vocab',
    'benchmarks',
    'benchmarks/benchmark_runs',
    'data/raw/museum',
    'data/raw/pigments',
    'data/raw/manufacturers',
    'data/raw/color_theory',
    'data/raw/historical',
    'data/raw/scientific',
    'data/clean/markdown',
    'data/clean/tables',
    'data/clean/metadata',
    'data/chunks/text',
    'data/chunks/tables',
    'data/chunks/metadata',
    'data/indexes/chroma',
    'data/indexes/lexical',
    'data/indexes/cache',
    'data/register',
    'data/logs',
    'src/oil_painting_rag',
    'src/oil_painting_rag/models',
    'src/oil_painting_rag/storage',
    'src/oil_painting_rag/ingestion',
    'src/oil_painting_rag/chunking',
    'src/oil_painting_rag/indexing',
    'src/oil_painting_rag/retrieval',
    'src/oil_painting_rag/generation',
    'src/oil_painting_rag/evaluation',
    'src/oil_painting_rag/policies',
    'src/oil_painting_rag/utils',
    'tests',
]

# All markdown documentation files
MARKDOWN_DOCS = [
    ('docs/foundation/FOUNDATION_PACK_v1.md', ''),
    ('docs/foundation/source_hierarchy.md', ''),
    ('docs/foundation/metadata_schema.md', ''),
    ('docs/foundation/controlled_vocabulary.md', ''),
    ('docs/foundation/chunking_rules.md', ''),
    ('docs/foundation/benchmark_template.md', ''),
    ('docs/foundation/system_prompt_v1.md', ''),
    ('docs/policies/source_acquisition_policy.md', ''),
    ('docs/policies/metadata_provenance_rules.md', ''),
    ('docs/policies/deduplication_policy.md', ''),
    ('docs/policies/conflict_resolution_policy.md', ''),
    ('docs/policies/review_workflow.md', ''),
    ('docs/policies/retrieval_policy_v1.md', ''),
    ('docs/policies/answer_labeling_standard.md', ''),
    ('docs/policies/file_naming_policy.md', ''),
    ('docs/roadmap/CHANGELOG.md', ''),
    ('docs/roadmap/versioning_policy.md', ''),
    ('README.md', ''),
]

# All JSON schema files
JSON_FILES = {
    'schemas/source_register_schema.json': {'type': 'object', 'properties': {}},
    'schemas/chunk_schema.json': {'type': 'object', 'properties': {}},
    'schemas/field_provenance_schema.json': {'type': 'object', 'properties': {}},
    'schemas/duplicate_cluster_schema.json': {'type': 'array', 'items': {}},
    'schemas/conflict_record_schema.json': {'type': 'object', 'properties': {}},
    'schemas/review_record_schema.json': {'type': 'object', 'properties': {}},
    'schemas/approval_state_schema.json': {'type': 'object', 'properties': {}},
    'schemas/context_package_schema.json': {'type': 'object', 'properties': {}},
    'schemas/retrieval_trace_schema.json': {'type': 'object', 'properties': {}},
    'schemas/benchmark_template.json': {'type': 'object', 'properties': {}},
    'schemas/restriction_flags.json': {'type': 'array', 'items': {}},
    'schemas/answer_label_schema.json': {'type': 'object', 'properties': {}},
    'vocab/material_alias_map.json': {},
    'vocab/controlled_vocabulary.json': {},
    'vocab/product_alias_map.json': {},
    'vocab/material_ontology_v1.json': {},
    'benchmarks/benchmark_gold_set_v1.json': {'type': 'array', 'items': {}},
    'benchmarks/benchmark_template.json': {},
}

# All CSV log files
CSV_FILES = [
    'data/register/source_register.csv',
    'data/register/acquisition_log.csv',
    'data/register/qa_log.csv',
    'data/register/duplicate_review_log.csv',
    'data/register/conflict_review_log.csv',
    'data/register/source_review_log.csv',
    'data/register/metadata_review_log.csv',
    'data/register/chunk_review_log.csv',
    'data/register/release_approval_log.csv',
    'data/logs/retrieval_failure_log.csv',
]

# All __init__.py files (with docstring)
PYTHON_INIT = [
    'src/oil_painting_rag/__init__.py',
    'src/oil_painting_rag/models/__init__.py',
    'src/oil_painting_rag/storage/__init__.py',
    'src/oil_painting_rag/ingestion/__init__.py',
    'src/oil_painting_rag/chunking/__init__.py',
    'src/oil_painting_rag/indexing/__init__.py',
    'src/oil_painting_rag/retrieval/__init__.py',
    'src/oil_painting_rag/generation/__init__.py',
    'src/oil_painting_rag/evaluation/__init__.py',
    'src/oil_painting_rag/policies/__init__.py',
    'src/oil_painting_rag/utils/__init__.py',
]

# All .gitkeep files
GITKEEP_FILES = [
    'benchmarks/benchmark_runs/.gitkeep',
    'data/raw/museum/.gitkeep',
    'data/raw/pigments/.gitkeep',
    'data/raw/manufacturers/.gitkeep',
    'data/raw/color_theory/.gitkeep',
    'data/raw/historical/.gitkeep',
    'data/raw/scientific/.gitkeep',
    'data/clean/markdown/.gitkeep',
    'data/clean/tables/.gitkeep',
    'data/clean/metadata/.gitkeep',
    'data/chunks/text/.gitkeep',
    'data/chunks/tables/.gitkeep',
    'data/chunks/metadata/.gitkeep',
    'data/indexes/chroma/.gitkeep',
    'data/indexes/lexical/.gitkeep',
    'data/indexes/cache/.gitkeep',
]

# All Python module files (with docstrings)
PYTHON_MODULES = [
    ('src/oil_painting_rag/config.py', 'Provides configuration settings and defaults.'),
    ('src/oil_painting_rag/cli.py', 'Provides command-line interface entry point.'),
    ('src/oil_painting_rag/api.py', 'Provides REST API endpoints.'),
    ('src/oil_painting_rag/logging_utils.py', 'Provides logging utilities and configuration.'),
    ('src/oil_painting_rag/models/source_models.py', 'Provides source entity models.'),
    ('src/oil_painting_rag/models/chunk_models.py', 'Provides chunk entity models.'),
    ('src/oil_painting_rag/models/provenance_models.py', 'Provides provenance and metadata models.'),
    ('src/oil_painting_rag/models/retrieval_models.py', 'Provides retrieval entity models.'),
    ('src/oil_painting_rag/models/benchmark_models.py', 'Provides benchmark entity models.'),
    ('src/oil_painting_rag/storage/filesystem_store.py', 'Provides filesystem-based storage.'),
    ('src/oil_painting_rag/storage/metadata_store.py', 'Provides metadata storage abstractions.'),
    ('src/oil_painting_rag/storage/register_store.py', 'Provides source registration storage.'),
    ('src/oil_painting_rag/ingestion/capture.py', 'Provides source capture logic.'),
    ('src/oil_painting_rag/ingestion/loader.py', 'Provides data loading logic.'),
    ('src/oil_painting_rag/ingestion/source_registry.py', 'Provides source registry management.'),
    ('src/oil_painting_rag/chunking/chunker.py', 'Provides text chunking logic.'),
    ('src/oil_painting_rag/chunking/table_chunker.py', 'Provides table chunking logic.'),
    ('src/oil_painting_rag/chunking/chunk_validators.py', 'Provides chunk validation logic.'),
    ('src/oil_painting_rag/indexing/embeddings.py', 'Provides embedding generation.'),
    ('src/oil_painting_rag/indexing/chroma_index.py', 'Provides Chroma-based indexing.'),
    ('src/oil_painting_rag/indexing/lexical_index.py', 'Provides lexical indexing.'),
    ('src/oil_painting_rag/indexing/index_manager.py', 'Provides index management logic.'),
    ('src/oil_painting_rag/retrieval/classifier.py', 'Provides retrieval classifier logic.'),
    ('src/oil_painting_rag/retrieval/filters.py', 'Provides retrieval filter logic.'),
    ('src/oil_painting_rag/retrieval/hybrid_retriever.py', 'Provides hybrid retrieval logic.'),
    ('src/oil_painting_rag/retrieval/reranker.py', 'Provides retrieval reranking logic.'),
    ('src/oil_painting_rag/retrieval/diversity.py', 'Provides retrieval diversity logic.'),
    ('src/oil_painting_rag/retrieval/citation_assembler.py', 'Provides citation assembly logic.'),
    ('src/oil_painting_rag/generation/prompt_builder.py', 'Provides prompt building logic.'),
    ('src/oil_painting_rag/generation/answerer.py', 'Provides answer generation logic.'),
    ('src/oil_painting_rag/generation/mode_router.py', 'Provides generation mode routing.'),
    ('src/oil_painting_rag/evaluation/benchmark_runner.py', 'Provides benchmark execution logic.'),
    ('src/oil_painting_rag/evaluation/scorer.py', 'Provides evaluation scoring logic.'),
    ('src/oil_painting_rag/evaluation/failure_logger.py', 'Provides failure logging logic.'),
    ('src/oil_painting_rag/policies/source_policy.py', 'Provides source acquisition policy.'),
    ('src/oil_painting_rag/policies/provenance_policy.py', 'Provides provenance management policy.'),
    ('src/oil_painting_rag/policies/retrieval_policy.py', 'Provides retrieval policy enforcement.'),
    ('src/oil_painting_rag/policies/conflict_policy.py', 'Provides conflict resolution policy.'),
    ('src/oil_painting_rag/utils/text_utils.py', 'Provides text processing utilities.'),
    ('src/oil_painting_rag/utils/citation_utils.py', 'Provides citation formatting utilities.'),
    ('src/oil_painting_rag/utils/enum_utils.py', 'Provides enum-related utilities.'),
    ('src/oil_painting_rag/utils/hash_utils.py', 'Provides hash generation utilities.'),
]

# Environment file
ENV_FILE = '.env.example'
ENV_CONTENT = '''# Environment variables for oil_painting_research_assistant
# Add your configuration here
'''

# Pyproject.toml
PYPROJECT_FILE = 'pyproject.toml'
PYPROJECT_CONTENT = '''[project]
name = "oil-painting-research-assistant"
version = "0.1.0"
description = "Provenance-aware RAG system for oil painting research"
requires-python = ">=3.11"
dependencies = [
    "chromadb>=0.4.0",
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''


def main():
    """Main scaffolding function."""
    print("=" * 70)
    print("OIL PAINTING RESEARCH ASSISTANT - SCAFFOLD SCRIPT")
    print("=" * 70)
    print()
    
    # Set root path
    if len(sys.argv) > 1:
        root_path = pathlib.Path(sys.argv[1])
    else:
        root_path = pathlib.Path(ROOT_NAME)
    
    # Ensure root exists
    root_path.mkdir(parents=True, exist_ok=True)
    
    # Track results
    created_dirs = []
    skipped_dirs = []
    created_files = []
    skipped_files = []
    
    # Create directories
    print("[1/6] Creating directories...")
    for dir_path in DIRECTORIES:
        full_path = root_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(dir_path)
    
    # Create markdown docs
    print("[2/6] Creating markdown documentation files...")
    for md_path, md_content in MARKDOWN_DOCS:
        content = f"# {md_path.split('/')[-1]}\n\nCanonical draft placeholder.\n" if not md_content else md_content
        success, full_path = create_file_if_missing(root_path, md_path, content)
        if success:
            created_files.append(md_path)
        else:
            skipped_files.append(md_path)
    
    # Create JSON files
    print("[3/6] Creating JSON schema files...")
    for json_path, json_content in JSON_FILES.items():
        success, full_path = create_file_if_missing(root_path, json_path, json.dumps(json_content))
        if success:
            created_files.append(json_path)
        else:
            skipped_files.append(json_path)
    
    # Create CSV files
    print("[4/6] Creating CSV log files...")
    for csv_path in CSV_FILES:
        full_path = root_path / csv_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('\n')
            created_files.append(csv_path)
        else:
            skipped_files.append(csv_path)
    
    # Create Python __init__.py files
    print("[5/6] Creating Python module init files...")
    for init_path in PYTHON_INIT:
        full_path = root_path / init_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            filename = pathlib.Path(init_path).name
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(f'# Module: {init_path}\n\n"""\nThis module provides {filename.replace("_", " ")} functionality.\n"""\n\n')
            created_files.append(init_path)
        else:
            skipped_files.append(init_path)
    
    # Create .gitkeep files
    print("[6/6] Creating gitkeep files...")
    for gitkeep_path in GITKEEP_FILES:
        full_path = root_path / gitkeep_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('')
            created_files.append(gitkeep_path)
        else:
            skipped_files.append(gitkeep_path)
    
    # Create Python module files with docstrings
    print("[7/6] Creating Python module files...")
    for path, docstring in PYTHON_MODULES:
        full_path = root_path / path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            filename = pathlib.Path(path).name
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(f'# Module: {filename}\n\n"""\nProvides {docstring}.\n"""\n\n')
            created_files.append(path)
        else:
            skipped_files.append(path)
    
    # Create ENV file
    print("[8/7] Creating environment file...")
    full_path = root_path / ENV_FILE
    if not full_path.exists():
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(ENV_CONTENT)
        created_files.append(ENV_FILE)
    else:
        skipped_files.append(ENV_FILE)
    
    # Create pyproject.toml
    print("[9/7] Creating pyproject.toml...")
    full_path = root_path / PYPROJECT_FILE
    if not full_path.exists():
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(PYPROJECT_CONTENT)
        created_files.append(PYPROJECT_FILE)
    else:
        skipped_files.append(PYPROJECT_FILE)
    
    # Print summary
    print()
    print("=" * 70)
    print("SCAFFOLD COMPLETE - SUMMARY")
    print("=" * 70)
    print()
    print(f"Created Directories: {len(created_dirs)}")
    print(f"Created Files: {len(created_files)}")
    print(f"Skipped (Already Exist): {len(skipped_files)}")
    print()
    print("Total items: " + str(len(created_dirs) + len(created_files) + len(skipped_dirs) + len(skipped_files)))
    print("=" * 70)


if __name__ == '__main__':
    main()

