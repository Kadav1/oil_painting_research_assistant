You are a senior Python engineer and RAG architect.

Help me build the Oil Painting Research Assistant RAG system in phases.

This is a provenance-aware, source-aware, hybrid retrieval system for oil painting knowledge:
- pigments
- binders/media
- conservation
- historical practice
- color theory
- manufacturer product data

Important constraints:
- ChromaDB must be the vector database
- source hierarchy must be respected
- metadata provenance must be preserved
- hybrid retrieval only, not vector-only
- case studies must remain scoped
- product-specific data must remain labeled
- citations must be real and traceable
- evaluation must be included
- code must be modular and production-minded

We will build in phases.

Phase order:
1. data models
2. storage and metadata layer
3. chunking layer
4. ChromaDB vector indexing
5. lexical indexing
6. hybrid retrieval
7. reranking + diversity
8. answer generation + citation assembly
9. evaluation harness
10. CLI/API
11. tests and README

For every phase:
- first explain the design briefly
- then output the files for that phase
- keep filenames clear
- ensure compatibility with previous phases
- do not generate placeholder architecture without useful code

Start with Phase 1 only:
Create the data models for:
- source metadata
- chunk metadata
- provenance records
- retrieval request/response models
- benchmark models
- enums for source family, source type, domain, question type, claim type, confidence, review status, citability, case specificity, approval level, and mode routing.
