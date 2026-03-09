You are a senior technical writer, governance documentation specialist, and research-systems architect.

Your task is to generate the policy documentation files for a project named:

Oil Painting Research Assistant

This project is a provenance-aware, source-aware, review-aware, ChromaDB-based RAG system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

Your job is to write the policy layer only.

Do NOT write code.
Do NOT write the foundation docs in this task.
Do NOT write generic documentation fluff.
Do NOT produce toy placeholders.

The documents must be:
- formal
- structured
- implementation-aware
- operational
- internally consistent
- suitable to serve as canonical internal governance docs

==================================================
1. PRIMARY GOAL
==================================================

Create the full policy documentation set for the project under:

docs/policies/

These documents should define the operational rules for:
- source intake
- metadata provenance
- deduplication
- conflict handling
- review gates
- retrieval behavior
- answer-status labeling
- file naming conventions

The policy docs must align with a ChromaDB-based RAG architecture and with a provenance-aware corpus design.

==================================================
2. DOCUMENTS TO CREATE
==================================================

Create these files:

- docs/policies/source_acquisition_policy.md
- docs/policies/metadata_provenance_rules.md
- docs/policies/deduplication_policy.md
- docs/policies/conflict_resolution_policy.md
- docs/policies/review_workflow.md
- docs/policies/retrieval_policy_v1.md
- docs/policies/answer_labeling_standard.md
- docs/policies/file_naming_policy.md

==================================================
3. REQUIRED WRITING STYLE
==================================================

Write in a style that is:

- formal but clear
- precise
- policy-oriented
- structured and methodical
- suitable for implementation and future auditing
- free from fluff
- explicit about rules, scope, and intent

Each document should feel like a real internal governance document for a serious project.

==================================================
4. REQUIRED DOCUMENT FORMAT
==================================================

For each file:

1. Start with a title line:
   `# <Document Title> v1.0`

2. Include a standard metadata block near the top with:
- Document ID
- Version
- Status
- Scope
- Applies to

3. Use clearly numbered headings.

4. Include sections as appropriate such as:
- Purpose
- Core Principle
- Objectives
- Definitions
- Rules
- Workflow or Operational Guidance
- Non-Negotiable Rules
- QA Questions
- Recommended Companion Documents
- Adoption Rule

5. Keep terminology consistent across all files.

==================================================
5. PROJECT CONTEXT TO RESPECT
==================================================

Assume the project already has these conceptual commitments:

- Source hierarchy matters.
- Metadata provenance matters.
- Review state matters.
- Case studies must remain scoped.
- Product-specific claims must remain labeled.
- Conflicts between sources must not be hidden.
- Retrieval must be hybrid, not vector-only.
- ChromaDB is the vector database.
- Benchmarking and failure taxonomy are part of the project.
- Answer labeling must reflect epistemic status.

The policy documents must reinforce this architecture.

==================================================
6. POLICY DOCUMENT EXPECTATIONS
==================================================

### source_acquisition_policy.md
Define:
- what source families are allowed
- what is restricted or out of scope
- trust hierarchy for intake
- admission criteria
- source selection priorities
- intake scoring logic
- intake workflow
- admission status types
- family-specific intake rules
- rejection and deferment rules
- raw storage and freshness rules
- human review requirement

### metadata_provenance_rules.md
Define:
- provenance model
- provenance types
- provenance methods
- confidence levels
- review status values
- override status values
- field classes
- which fields may be extracted, inferred, model-suggested, or manually governed
- per-field provenance structure
- review events
- operational use rules for reviewed vs unreviewed metadata

### deduplication_policy.md
Define:
- duplicate levels
- exact vs format vs version vs near duplicate
- source-level duplicate categories
- chunk-level duplicate categories
- detection signals
- canonical source selection
- supersession rules
- mirror/rehost rules
- product page duplication rules
- table duplication rules
- duplicate clusters
- retrieval-time redundancy control
- deletion vs suppression logic

### conflict_resolution_policy.md
Define:
- conflict types
- conflict priority principle
- resolution order
- prefer-one / keep-both / scope-split logic
- question-type-specific conflict rules
- metadata conflict rules
- answer-time disclosure rules
- conflict labels
- retrieval-time conflict handling
- citation rules in conflicted answers

### review_workflow.md
Define:
- artifact classes under review
- roles
- workflow stages
- review gates
- gate-specific reviewer checks
- approval levels
- review actions
- review record requirements
- deferment rules
- rejection rules
- revision loop
- escalation rules
- state transition logic
- log files

### retrieval_policy_v1.md
Define:
- retrieval purpose and scope
- canonical retrieval pipeline
- query classification
- mode inference
- metadata filtering
- corpus eligibility rules
- hybrid retrieval rules
- lexical retrieval role
- vector retrieval role
- candidate pool construction
- reranking
- trust-tier weighting
- review-state weighting
- freshness logic
- case-specificity rules
- duplicate suppression
- diversity rules
- conflict-aware retrieval
- context assembly
- citation-readiness rules
- retrieval logging
- retrieval failure conditions

### answer_labeling_standard.md
Define:
- why answer labels exist
- canonical label set
- label definitions
- label selection rules
- label priority rules
- labeling by source pattern
- labeling by question type
- global vs local labeling
- relationship to citations
- relationship to conflicts
- relationship to provenance and review state
- writing guidance for explicit label use
- prohibited labeling behavior

### file_naming_policy.md
Define:
- general naming rules
- allowed characters
- case rules
- date format rules
- version format rules
- naming families for:
  - policy docs
  - foundation docs
  - schema files
  - vocabulary files
  - benchmark files
  - source files
  - chunk files
  - register/log files
  - conflict/review/duplicate records
- source ID rules
- chunk ID rules
- raw/clean/chunk filename patterns
- temporary/experimental file rules
- archive naming rules
- stem construction rules
- filename QA questions

==================================================
7. IMPORTANT CONSISTENCY RULES
==================================================

- The docs must agree on terminology.
- Source hierarchy logic must align with retrieval and conflict rules.
- Metadata provenance rules must align with review workflow.
- Answer labeling must align with conflict handling and provenance.
- File naming must align with source IDs and chunk IDs used elsewhere.
- Retrieval policy must explicitly support ChromaDB-based vector retrieval plus lexical retrieval.
- Policies must be operational and stricter than high-level foundation summaries.

==================================================
8. CHROMADB REQUIREMENT
==================================================

Because the project uses ChromaDB as the vector database, retrieval policy and related docs should be compatible with:

- persistent local ChromaDB storage
- collection-based chunk indexing
- stable `chunk_id` document IDs
- metadata filtering in vector retrieval
- local-first operation

Do not write code, but write the policies so they fit this architecture.

==================================================
9. OUTPUT STYLE
==================================================

When you respond:

1. First provide a short summary of the policy layer as a whole.
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
- collapse all policies into one document
- write generic best-practice boilerplate
- invent contradictory enums or status names
- weaken the distinction between reviewed and unreviewed data
- ignore case-specific or product-specific scope
- hide meaningful conflict
- write the retrieval policy as if the system were vector-only
- ignore the ChromaDB-based architecture
- treat policy documents as casual prose

Write these as the canonical internal policy documents for a real research-grade project.
