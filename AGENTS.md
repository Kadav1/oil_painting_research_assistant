# Repository Guidelines

## Project Structure & Module Organization
Core code lives in `src/oil_painting_rag/`, organized by pipeline stage: `ingestion/`, `chunking/`, `indexing/`, `retrieval/`, `generation/`, and `evaluation/`. Shared contracts are in `models/`, policy rules in `policies/`, and storage adapters in `storage/`.

Project data is under `data/` (`raw/`, `clean/`, `chunks/`, `indexes/`, `register/`, `logs/`). Canonical documentation and governance live in `docs/foundation/` and `docs/policies/`. JSON schemas are in `schemas/`, controlled vocab files in `vocab/`, and benchmark artifacts in `benchmarks/`.

## Build, Test, and Development Commands
Use Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Common run commands:

```bash
python -m oil_painting_rag.cli
python -m oil_painting_rag.api
python -m oil_painting_rag.evaluation.benchmark_runner
pytest tests/ -v
```

Note: 60 tests exist across models, chunking, retrieval, and utils. Use `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` prefix when the embedding model is cached but network is unavailable.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation and explicit type hints on public functions. Prefer `snake_case` for functions/modules, `PascalCase` for classes, and clear domain names (for example, `provenance_models.py`, `hybrid_retriever.py`).

Keep modules focused on one pipeline responsibility. Centralize paths/settings in `config.py`; avoid hardcoded filesystem locations outside config.

## Testing Guidelines
Place tests in `tests/` (currently flat: `test_models.py`, `test_chunking.py`, `test_retrieval.py`, `test_utils.py`). Use `test_*.py` naming and arrange cases around pipeline behavior, provenance integrity, and policy enforcement.

For retrieval or generation changes, add/update benchmark scenarios in `benchmarks/` and include before/after notes in your PR.

## Commit & Pull Request Guidelines
Current history follows Conventional Commit style (example: `feat: ...`); continue using prefixes like `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

PRs should include:
- concise problem/solution summary
- linked issue (if available)
- impacted modules and docs/schemas updated
- test/benchmark evidence for behavior changes

## Domain Data Integrity

- All `domain`, `approval_state`, `chunk_type`, `source_type`, `citability`, and `case_specificity` values MUST match `vocab/controlled_vocabulary.json` exactly. Non-canonical values (e.g. `"pigments"` instead of `"pigment"`) silently break retrieval filters.
- `IndexManager.status()` returns `chroma_counts` (dict) and `bm25_size` (int) — not `chroma`/`lexical`.
- ChromaDB metadata list fields are pipe-encoded strings. Use `pipe_encode()`/`pipe_decode()` from `utils/text_utils.py`.

## Security & Configuration Tips
Do not commit secrets. Keep runtime config in `.env` (seed from `.env.example`) and keep large/raw datasets inside `data/` rather than source directories.
