# Oil Painting Research Assistant

A provenance-aware, source-aware, review-aware RAG system for oil painting knowledge.

The project is designed to support reliable answers about:

- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

This is not intended to be a generic chatbot. It is a structured research assistant whose behavior is shaped by source hierarchy, metadata provenance, review state, conflict handling, and benchmarked evaluation.

---

## Project Status

**Current state:** documentation and governance foundation in progress.  
**Architecture direction:** local-first, ChromaDB-based hybrid RAG.  
**Primary goal:** build a trustworthy research assistant before scaling ingestion and code.

At this stage, the project is being built in the correct order:

1. folder scaffold
2. foundation documents
3. policy documents
4. machine-readable schemas and vocab files
5. code implementation
6. ingestion and evaluation
7. live retrieval and answer generation

The project is intentionally documentation-first so that retrieval, indexing, and generation logic do not drift away from the intended rules.

---

## Core Principles

### 1. Source hierarchy matters
Not all sources should be treated equally. Museum conservation, technical bulletins, pigment references, product pages, and teaching texts all play different roles.

### 2. Metadata provenance matters
The system must distinguish between values that are:
- extracted
- rule-inferred
- model-suggested
- manually entered
- manually reviewed
- manually overridden

### 3. Review state matters
Draft or unreviewed data must not silently behave like approved evidence.

### 4. Scope must be preserved
Case studies remain case-specific. Product pages remain product-specific. Historical claims remain historically scoped.

### 5. Conflict must not be hidden
When sources disagree in meaningful ways, the system should expose or properly scope the disagreement rather than flattening it into false certainty.

### 6. Retrieval must be hybrid
The system is designed around:
- lexical retrieval
- ChromaDB vector retrieval
- metadata filtering
- reranking
- diversity control
- duplicate suppression
- conflict-aware context assembly

### 7. Answers must reflect epistemic status
The assistant should distinguish between:
- well established
- historically documented
- product-specific
- case-specific
- likely but context-dependent
- mixed evidence
- uncertain

---

## What This Project Is

The Oil Painting Research Assistant is a structured knowledge system for questions such as:

- What is the difference between lead white, zinc white, and titanium white?
- Why does burnt umber often dry faster?
- What is smalt, and why can it discolor?
- When would a painter prefer walnut oil over linseed oil?
- What does stand oil do differently from regular linseed oil?
- Why did my paint wrinkle overnight?
- What does “sinking in” mean?
- Would a 15th-century painter likely have used titanium white?
- Was verdigris historically used in oil painting?
- What is the difference between hue, value, and chroma?
- Why do complementary mixtures go muddy?
- How can two paints with the same pigment code still behave differently?

---

## What This Project Is Not

This project is **not**:

- a generic art chatbot
- a style-transfer image generator
- a replacement for conservation treatment expertise
- a brand-marketing recommender disguised as technical guidance
- a system that treats repeated web content as stronger evidence
- a vector-only semantic search demo

---

## Intended Architecture

The system is designed as a **local-first, ChromaDB-based RAG pipeline**.

### Major layers

#### 1. Documentation layer
Defines the conceptual and governance baseline.

Includes:
- foundation docs
- policy docs
- roadmap/versioning docs

#### 2. Schema layer
Defines:
- source records
- chunk records
- provenance records
- duplicate clusters
- conflict records
- review records
- answer labels
- benchmark structures
- controlled vocabularies

#### 3. Corpus layer
Stores:
- raw sources
- normalized text
- chunked text
- metadata sidecars
- registers and logs
- benchmark assets

#### 4. Retrieval layer
Uses:
- lexical retrieval
- ChromaDB vector retrieval
- metadata filtering
- reranking
- diversity controls
- duplicate suppression
- citation packaging

#### 5. Generation layer
Builds:
- source-aware answers
- conflict-aware synthesis
- uncertainty-aware responses
- citation-ready outputs

#### 6. Evaluation layer
Supports:
- benchmark runs
- retrieval traces
- failure logging
- answer inspection
- future scoring and regression testing

---

## Repository Structure

```text
oil_painting_research_assistant/
├── docs/
│   ├── foundation/
│   ├── policies/
│   └── roadmap/
├── schemas/
├── vocab/
├── benchmarks/
├── data/
│   ├── raw/
│   ├── clean/
│   ├── chunks/
│   ├── indexes/
│   ├── register/
│   └── logs/
├── src/
│   └── oil_painting_rag/
└── tests/

Documentation Layout
Foundation documents

These define the conceptual baseline of the project.

Expected core files:

FOUNDATION_PACK_v1.md

source_hierarchy.md

metadata_schema.md

controlled_vocabulary.md

chunking_rules.md

benchmark_template.md

system_prompt_v1.md

Policy documents

These define operational governance.

Expected core files:

source_acquisition_policy.md

metadata_provenance_rules.md

deduplication_policy.md

conflict_resolution_policy.md

review_workflow.md

retrieval_policy_v1.md

answer_labeling_standard.md

file_naming_policy.md

Roadmap documents

These define release and maintenance logic.

Expected core files:

CHANGELOG.md

versioning_policy.md

Structured Resource Layer

The project also relies on machine-readable resources such as:

Schemas

source register schema

chunk schema

field provenance schema

duplicate cluster schema

conflict record schema

review record schema

approval state schema

context package schema

retrieval trace schema

benchmark template schema

answer label schema

Vocabulary and maps

controlled vocabulary

material alias map

product alias map

material ontology

Benchmarks

benchmark template

benchmark gold set

These files are intended to keep the code layer aligned with the documentation layer.

Source Model

The project assumes a ranked source hierarchy.

Tier 1 — Highest trust

Museum conservation, technical bulletins, conservation science, technical examination of artworks.

Tier 2 — Strong reference

Pigment references, structured material references, technical handbooks.

Tier 3 — Practical product data

Manufacturer product pages, technical sheets, SDS/TDS.

Tier 4 — Instructional / interpretive

Serious atelier texts, technical teaching sources, interpretive manuals.

Tier 5 — Supplemental / low trust

Blogs, casual tutorials, forums, social posts.

The system is designed to respect both:

trust order

question-fit

A product page may be the best source for a specific paint’s pigment code, while a conservation bulletin may be the best source for historical degradation behavior.

Retrieval Model

The retrieval layer is designed to be hybrid.

Retrieval flow

query intake

query classification

mode inference

metadata filtering

lexical retrieval

ChromaDB vector retrieval

candidate merge

reranking

diversity enforcement

duplicate suppression

conflict-aware adjustment

context assembly

citation packaging

Supported answer modes

Studio

Conservation

Art History

Color Analysis

Product Comparison

Provenance Model

Important metadata fields should preserve how they were created.

Canonical provenance types include:

extracted

rule_inferred

model_suggested

manual_entered

manual_reviewed

manual_overridden

imported

derived

This distinction is important for:

review

retrieval filtering

trust weighting

debugging

evaluation

Review and Approval Model

The project distinguishes between draft and operational data.

Typical progression:

candidate

registered

captured

normalized

metadata_drafted

review_pending

reviewed_confirmed / reviewed_corrected

approved_for_chunking

chunked

approved_for_indexing

indexed

approved_for_retrieval

approved_for_live_use

This is designed to prevent unreviewed material from silently entering live answer generation.

Benchmarks and Evaluation

The project includes a benchmark layer from the beginning.

Benchmark categories include:

pigments

binders and media

conservation

historical practice

color theory

product comparison

terminology

integrated reasoning

Typical evaluation concerns include:

wrong pigment identity

wrong pigment code

case-study overgeneralization

product/history confusion

weak uncertainty handling

retrieval mismatch

source-tier misuse

citation failure

scope collapse

terminology confusion

The goal is not only to generate answers, but to measure whether those answers are:

accurate

source-fit

useful

appropriately scoped

appropriately uncertain where needed

ChromaDB

ChromaDB is the intended vector database for the project.

Expected role:

persistent local vector storage

chunk-level indexing

metadata-aware filtering

stable chunk_id document IDs

integration with hybrid retrieval

The system is not designed around vector search alone. ChromaDB is one part of the retrieval layer, not the whole retrieval strategy.

Development Direction

The recommended implementation order is:

scaffold the repository

finalize foundation docs

finalize policy docs

create schemas and vocab resources

implement data models

implement storage layer

implement chunking

implement ChromaDB indexing

implement lexical retrieval

implement hybrid retrieval

implement reranking and citation assembly

implement answer generation

implement evaluation harness

add CLI and API

test, revise, and benchmark

Installation

This repository is currently intended as a structured build project.
Installation steps will depend on the implementation stage.

Expected future setup will likely include:

python -m venv .venv
source .venv/bin/activate
pip install -e .

Expected future dependencies include:

chromadb

typer

fastapi

pydantic

rank-bm25

sentence-transformers

pandas

This section should be updated once the code layer is scaffolded and dependency choices are locked.

Configuration

Planned configuration areas include:

data root paths

ChromaDB storage path

embedding backend

generation backend

retrieval mode

review-state filtering

benchmark output paths

logging level

A future .env.example and config.py should define the canonical config surface.

Current Priority

The immediate priority is to keep the project coherent by ensuring that:

documentation comes before implementation

schemas reflect the documentation

code reflects the schemas

retrieval reflects the policies

answers reflect source scope and epistemic status

That order is the main quality-control mechanism of the project.

Contribution Philosophy

Any future work on this repository should preserve:

source hierarchy

provenance awareness

review-state awareness

scoped conflict handling

hybrid retrieval

ChromaDB compatibility

answer labeling discipline

benchmark-driven evaluation

Convenience should not override structure.

Short Project Summary

Oil Painting Research Assistant is a documentation-first, governance-first RAG project for reliable oil painting knowledge.

It is being designed so that future implementation will be:

source-aware

provenance-aware

review-aware

benchmarkable

explainable

maintainable

The goal is not just to retrieve text, but to produce answers that stay faithful to evidence, scope, and uncertainty.
