Additional ChromaDB rules:

- Use ChromaDB as the primary vector storage layer.
- Use `chunk_id` as the Chroma document ID.
- Store enough metadata in Chroma to support query-time filtering.
- Add an index manager that can:
  - create collections
  - upsert chunks
  - delete chunks
  - delete by source_id
  - rebuild collections from local chunk files
  - inspect collection counts
- Separate live-approved indexing from testing/draft indexing where practical.
- Document any metadata encoding compromises required by ChromaDB.
- Do not replace ChromaDB with Qdrant, FAISS, Weaviate, or another vector store.
