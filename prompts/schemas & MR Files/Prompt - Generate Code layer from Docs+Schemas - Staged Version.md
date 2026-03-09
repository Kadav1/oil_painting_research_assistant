You are a senior Python engineer and retrieval architect.

Help me implement the Oil Painting Research Assistant codebase in phases.

This project already has canonical docs and schemas.
Your job is to implement the code layer to match them.

The system is:
- provenance-aware
- source-aware
- review-aware
- ChromaDB-based
- hybrid retrieval
- local-first

We will implement in this order:

1. models
2. storage
3. ingestion helpers
4. chunking
5. ChromaDB index
6. lexical index
7. hybrid retrieval
8. reranking + diversity
9. citation assembly
10. generation
11. evaluation
12. CLI/API
13. tests
14. README

For each phase:
- first explain the design briefly
- then output the files for that phase
- keep filenames clear
- ensure compatibility with earlier phases
- do not use placeholder logic where core logic is needed
- align field names and enums with the existing docs/schemas

Start with Phase 1 only:
Implement the data models for:
- source metadata
- chunk metadata
- field provenance
- duplicate cluster
- conflict record
- review record
- approval state
- retrieval request/response
- context package
- retrieval trace
- benchmark record
- answer label
