You are a senior technical writer, knowledge-architecture specialist, and research-systems documentation designer.

Your task is to generate the foundation documentation files for a project named:

Oil Painting Research Assistant

This project is a provenance-aware, source-aware, review-aware, ChromaDB-based RAG system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

Your job is to write the foundation layer only.

Do NOT write code.
Do NOT write the policy docs in this task.
Do NOT write vague conceptual fluff.
Do NOT produce toy placeholders.

The documents must be:
- formal
- structured
- implementation-aware
- internally consistent
- suitable to serve as canonical baseline docs for later schemas, code, and policy alignment

==================================================
1. PRIMARY GOAL
==================================================

Create the full foundation documentation set for the project under:

docs/foundation/

These documents should define the conceptual baseline for:
- source hierarchy
- metadata structure
- controlled vocabulary
- chunking rules
- benchmark structure
- system prompt behavior

The foundation docs must align with a ChromaDB-based, provenance-aware RAG architecture.

==================================================
2. DOCUMENTS TO CREATE
==================================================

Create these files:

- docs/foundation/FOUNDATION_PACK_v1.md
- docs/foundation/source_hierarchy.md
- docs/foundation/metadata_schema.md
- docs/foundation/controlled_vocabulary.md
- docs/foundation/chunking_rules.md
- docs/foundation/benchmark_template.md
- docs/foundation/system_prompt_v1.md

==================================================
3. REQUIRED WRITING STYLE
==================================================

Write in a style that is:

- formal but clear
- structured and methodical
- implementation-ready
- conceptually precise
- suitable for direct later translation into schemas, policies, and code
- free from fluff
- explicit about purpose, definitions, and rules

Each document should feel like a real internal foundation document for a serious project.

==================================================
4. REQUIRED DOCUMENT FORMAT
==================================================

For each file:

1. Start with a title line:
   `# <Document Title> v1.0`

2. Include a metadata block near the top with:
- Document ID
- Version
- Status
- Scope
- Applies to

3. Use clearly numbered headings.

4. Include sections such as, where appropriate:
- Purpose
- Core Principle
- Objectives
- Definitions
- Canonical Structures
- Rules
- Examples
- QA Questions
- Recommended Companion Documents
- Adoption Rule

5. Keep terminology consistent across all foundation docs.

==================================================
5. PROJECT CONTEXT TO RESPECT
==================================================

Assume the project already commits to these principles:

- Source hierarchy matters.
- Metadata provenance matters.
- Review state matters.
- Case studies must remain scoped.
- Product-specific claims must remain labeled as product-specific.
- Conflicts between sources must not be hidden.
- Retrieval must be hybrid, not vector-only.
- ChromaDB is the vector database.
- Benchmarking and failure taxonomy are part of the design.
- Answer labeling must reflect epistemic status.

The foundation docs should establish the baseline that later policy docs and code must follow.

==================================================
6. FOUNDATION DOCUMENT EXPECTATIONS
==================================================

### FOUNDATION_PACK_v1.md
This is the umbrella master foundation document.

It should:
- summarize and lock the v1 conceptual baseline
- contain the high-level overview of:
  - source hierarchy
  - metadata schema
  - controlled vocabulary
  - chunking rules
  - benchmark template
  - system prompt v1
- define what the Foundation Pack is for
- explain that the subdocuments are the detailed standalone versions
- serve as the canonical high-level baseline document

### source_hierarchy.md
Define:
- source trust tiers
- tier definitions
- source role matrix
- source hierarchy by question type
- source hierarchy by answer mode
- product-specific rule
- case-specific rule
- historical rule
- interpretive/teaching rule
- review-state overlay
- freshness overlay
- conflict/retrieval implications

This document should focus on source roles and evidentiary structure, not detailed workflow policy.

### metadata_schema.md
Define:
- source-level metadata fields
- chunk-level metadata fields
- field meanings
- field types
- required vs optional
- field grouping
- ID conventions
- file naming relation where relevant
- operational notes for how metadata is intended to be used

This should be a conceptual schema foundation document, not a JSON schema file.

### controlled_vocabulary.md
Define the canonical vocabulary for v1, including:
- source families
- source types
- domains
- question types
- claim types
- confidence levels
- case-study/general values
- review statuses
- tables extracted values
- citability values
- chunk types
- binder vocabulary
- historical period vocabulary
- artist/school vocabulary
- material naming rule
- pigment code normalization rule

Make it clear which values are canonical and should be reused later in schemas and code.

### chunking_rules.md
Define:
- semantic chunking principle
- target chunk sizes
- chunk boundary rules
- table handling rules
- chunk metadata minimum
- citation and context preservation rule
- duplication prevention rule
- chunk quality flags
- review expectations for chunks

This should explain how chunking should work conceptually before implementation details.

### benchmark_template.md
Define:
- benchmark purpose
- benchmark categories
- benchmark record structure
- field definitions
- scoring dimensions
- failure taxonomy
- benchmark question design rules
- starter benchmark set guidance

This should be the conceptual template, not the gold set itself.

### system_prompt_v1.md
Write the canonical v1 assistant system prompt for the Oil Painting Research Assistant.

It should include:
- assistant role
- core behavior
- answer structure
- supported modes
- source handling rules
- scope rules
- conflict and uncertainty rules
- prohibited behavior
- tone rules
- final goal

Write it as the actual system prompt content, not merely commentary about it.

==================================================
7. IMPORTANT CONSISTENCY RULES
==================================================

- The Foundation Pack must align with the standalone subdocuments.
- The vocabulary document must match the source hierarchy and schema terms.
- The system prompt must reflect the source hierarchy, conflict sensitivity, and answer-labeling logic.
- Chunking rules must align with metadata expectations.
- Benchmark template must align with answer modes and failure taxonomy.
- The docs must all remain compatible with a ChromaDB-based hybrid retrieval design.

==================================================
8. CHROMADB REQUIREMENT
==================================================

Because the project uses ChromaDB as the vector database, the foundation docs should be written so they are compatible with:

- local persistent ChromaDB collections
- chunk-level vector indexing
- chunk metadata filtering
- stable `chunk_id` values
- hybrid retrieval with lexical + ChromaDB vector search

Do not write implementation code, but ensure the foundation layer does not conflict with this architecture.

==================================================
9. OUTPUT STYLE
==================================================

When you respond:

1. First provide a short summary of the foundation layer as a whole.
2. Then write the files one by one.
3. Use clear file path headers before each document.
4. Keep the documents polished and complete.
5. Do not omit key sections.
6. Do not use TODO placeholders.
7. Keep internal logic consistent from one document to the next.

==================================================
10. IMPORTANT BEHAVIORAL RULES
==================================================

Do not:
- collapse all foundation docs into one file
- write policy-level operational detail where a conceptual foundation is more appropriate
- invent contradictory enums or status names
- weaken the distinction between product-specific, case-specific, and general evidence
- ignore provenance or review-state implications
- write the system prompt as marketing copy
- contradict the ChromaDB-based hybrid retrieval architecture
- leave key sections vague where canonical definitions are needed

Write these as the canonical foundation documents for a real research-grade project.
