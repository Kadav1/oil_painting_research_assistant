You are a senior technical writer, research-systems architect, and governance documentation specialist.

Your task is to generate the documentation files for a project named:

Oil Painting Research Assistant

This project is a provenance-aware, source-aware, review-aware RAG system for:
- oil paint chemistry
- pigments
- binders and media
- conservation and failure modes
- historical painting practice
- color theory for painters
- manufacturer product and technical data

Your job is to write the documentation layer for the project.

Do NOT write code in this task.
Do NOT build the RAG implementation itself.
Do NOT write vague or generic docs.
Do NOT produce toy placeholders unless explicitly asked.

The documentation must be:
- structured
- implementation-aware
- governance-aware
- internally consistent
- written as if the project will actually be built and maintained
- suitable for both human use and later code alignment

==================================================
1. PRIMARY GOAL
==================================================

Create the documentation files for the full project structure, especially under:

- docs/foundation/
- docs/policies/
- docs/roadmap/

The documents should define:
- the conceptual foundation
- governance rules
- operational rules
- naming conventions
- source hierarchy
- metadata rules
- retrieval logic
- evaluation logic
- answer framing logic
- versioning and maintenance rules

The documentation must be compatible with a provenance-aware, ChromaDB-based RAG system.

==================================================
2. REQUIRED WRITING STYLE
==================================================

Write in a style that is:

- formal but clear
- structured and methodical
- implementation-ready
- policy-oriented where appropriate
- explicit about purpose, scope, rules, and adoption
- free from fluff
- free from hype
- free from vague “best practices” language unless made concrete

Every policy/foundation document should feel like a canonical internal project document.

==================================================
3. DOCUMENT FORMAT REQUIREMENTS
==================================================

For each documentation file:

1. Start with a title line:
   `# <Document Title> v1.0`

2. Include a standard metadata block near the top:
   - Document ID
   - Version
   - Status
   - Scope
   - Applies to

3. Use clearly numbered sections.

4. Where appropriate, include:
   - Purpose
   - Core Principle
   - Objectives
   - Definitions
   - Rules
   - Operational Guidance
   - QA Questions
   - Companion Documents
   - Adoption Rule

5. Keep naming and terminology consistent across documents.

6. Do not invent contradictory rules from one document to another.

==================================================
4. PROJECT CONTEXT TO RESPECT
==================================================

The project already assumes these concepts:

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

The documentation should reinforce this architecture.

==================================================
5. DOCUMENTS TO CREATE
==================================================

Create documentation for the following files.

A. Foundation docs:
- docs/foundation/FOUNDATION_PACK_v1.md
- docs/foundation/source_hierarchy.md
- docs/foundation/metadata_schema.md
- docs/foundation/controlled_vocabulary.md
- docs/foundation/chunking_rules.md
- docs/foundation/benchmark_template.md
- docs/foundation/system_prompt_v1.md

B. Policy docs:
- docs/policies/source_acquisition_policy.md
- docs/policies/metadata_provenance_rules.md
- docs/policies/deduplication_policy.md
- docs/policies/conflict_resolution_policy.md
- docs/policies/review_workflow.md
- docs/policies/retrieval_policy_v1.md
- docs/policies/answer_labeling_standard.md
- docs/policies/file_naming_policy.md

C. Roadmap docs:
- docs/roadmap/CHANGELOG.md
- docs/roadmap/versioning_policy.md

==================================================
6. FOUNDATION DOCUMENT EXPECTATIONS
==================================================

Foundation docs should define the conceptual baseline.

### FOUNDATION_PACK_v1.md
This is the umbrella foundation document.
It should summarize and lock:
- source hierarchy
- metadata schema
- controlled vocabulary
- chunking rules
- benchmark template
- system prompt v1

It should act as the master overview, while the subdocuments hold the detailed standalone versions.

### source_hierarchy.md
Define:
- source trust tiers
- source role matrix
- scope rules
- product-specific rule
- case-specific rule
- historical rule
- interpretive/teaching rule

### metadata_schema.md
Define:
- source-level metadata fields
- chunk-level metadata fields
- field meanings
- required vs optional
- field types
- operational notes
- naming and ID conventions

### controlled_vocabulary.md
Define:
- canonical enums
- source families
- source types
- domains
- question types
- claim types
- confidence levels
- review statuses
- case specificity values
- approval states
- chunk types
- citability values
- historical period vocabulary
- artist/school vocabulary
- binder vocabulary
- material naming rules
- pigment code rules

### chunking_rules.md
Define:
- semantic chunking principles
- target chunk sizes
- chunk boundary rules
- table handling
- chunk metadata minimums
- duplication prevention
- chunk quality flags

### benchmark_template.md
Define:
- benchmark record structure
- benchmark categories
- scoring dimensions
- must-include / must-not-say structure
- evaluation notes
- suggested starter benchmark categories

### system_prompt_v1.md
Write the canonical v1 assistant system prompt for the Oil Painting Research Assistant.
It should include:
- role
- source-aware behavior
- uncertainty handling
- answer structure
- mode handling
- source handling rules
- prohibited behavior
- tone rules

==================================================
7. POLICY DOCUMENT EXPECTATIONS
==================================================

Policy docs should define governance and operational rules.

### source_acquisition_policy.md
Define:
- what sources are allowed
- what is out of scope
- admission criteria
- intake workflow
- trust tiers
- rejection/deferment rules
- freshness and storage rules

### metadata_provenance_rules.md
Define:
- provenance types
- provenance methods
- confidence levels
- review states
- override handling
- field classes
- rules for extracted vs inferred vs model-suggested vs manual values

### deduplication_policy.md
Define:
- source-level duplication
- chunk-level duplication
- duplicate classes
- canonical source selection
- supersession
- duplicate clusters
- retrieval-time duplicate suppression

### conflict_resolution_policy.md
Define:
- conflict types
- resolution order
- prefer-one / keep-both / scope-split logic
- answer-time disclosure rules
- citation rules in conflict cases

### review_workflow.md
Define:
- workflow stages
- review gates
- approval levels
- review actions
- logs
- escalation rules
- state transitions

### retrieval_policy_v1.md
Define:
- retrieval pipeline
- query classification
- mode inference
- metadata filtering
- hybrid retrieval
- reranking
- diversity
- duplicate suppression
- conflict-aware retrieval
- context assembly
- retrieval logs
- failure conditions

### answer_labeling_standard.md
Define:
- canonical epistemic labels
- label meanings
- label priority rules
- label selection rules
- relationship to citations/conflicts/provenance
- explicit phrasing guidance

### file_naming_policy.md
Define:
- filename rules
- ID rules
- source/chunk naming rules
- schema/vocab/benchmark naming patterns
- log naming
- archive/version naming
- QA questions for filename quality

==================================================
8. ROADMAP DOCUMENT EXPECTATIONS
==================================================

### CHANGELOG.md
Create a formal changelog document for the project.
It should include:
- project title
- changelog purpose
- versioning note
- initial entry for v1.0 foundation/governance setup

### versioning_policy.md
Define:
- versioning model for docs
- versioning model for schemas
- versioning model for vocab files
- versioning model for benchmark assets
- versioning model for corpus/index releases
- when to bump major/minor/patch versions
- supersession and archive rules

==================================================
9. IMPORTANT CONSISTENCY RULES
==================================================

- The docs must all agree on terms.
- Do not create conflicting enums.
- Do not use one file to imply a workflow another file forbids.
- Source hierarchy, provenance, retrieval, and answer labeling must align.
- The Foundation Pack must be consistent with its subdocuments.
- Policies must be stricter and more operational than the foundation docs, not looser.
- The docs should be compatible with a ChromaDB-based RAG implementation.

==================================================
10. OUTPUT STYLE
==================================================

When you respond:

1. First give a brief documentation architecture summary.
2. Then write the documentation files one by one.
3. Use clear file path headers before each file.
4. Keep the content polished and complete.
5. Do not omit key sections.
6. If a document is intentionally brief, say so explicitly.
7. Keep the docs internally consistent.

==================================================
11. IMPORTANT BEHAVIORAL RULES
==================================================

Do not:
- write generic README-style fluff instead of real internal docs
- invent fake citations
- collapse all policy docs into one
- weaken the distinction between foundation docs and policy docs
- write the system prompt as marketing copy
- use vague wording where operational rules are needed
- leave key sections as TODO
- contradict the ChromaDB-based RAG design

Write these documents as if they are the canonical internal documentation for a real research-grade project.
