"""
chroma_index.py — ChromaDB vector index for the Oil Painting Research Assistant.

Uses chromadb.PersistentClient with storage at config.CHROMA_DIR.
Uses chunk_id as the ChromaDB document ID (stable, never regenerated).
Maintains 3 collections: chunks_live, chunks_retrieval, chunks_draft.

Per approval_state_schema.json chromadb_collection_names:
  chunks_live      — live_allowed only
  chunks_retrieval — retrieval_allowed + live_allowed
  chunks_draft     — testing_only + retrieval_allowed + live_allowed

Metadata encoding note:
  ChromaDB only accepts str, int, float, bool.
  List fields (materials_mentioned, pigment_codes, etc.) are pipe-encoded strings.
  Decode on retrieval via text_utils.pipe_decode().
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import chromadb
from chromadb import Collection

import oil_painting_rag.config as cfg
from oil_painting_rag.indexing.embeddings import EmbeddingBackend, get_default_backend
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord

logger = get_logger(__name__)

# ChromaDB collection names (canonical)
_COLLECTION_LIVE = cfg.CHROMA_COLLECTION_LIVE          # "chunks_live"
_COLLECTION_RETRIEVAL = cfg.CHROMA_COLLECTION_RETRIEVAL # "chunks_retrieval"
_COLLECTION_DRAFT = cfg.CHROMA_COLLECTION_DRAFT         # "chunks_draft"

# Approval states indexed into each collection
_LIVE_STATES = set(cfg.LIVE_APPROVAL_STATES)
_RETRIEVAL_STATES = set(cfg.RETRIEVAL_APPROVAL_STATES)
_DRAFT_STATES = set(cfg.DRAFT_APPROVAL_STATES)


class ChromaIndex:
    """
    Manages all ChromaDB collections for chunk vector storage.

    Each collection uses the same embedding function.
    chunk_id is the Chroma document ID — never use any other ID.
    """

    def __init__(
        self,
        chroma_dir: Path = cfg.CHROMA_DIR,
        embedding_backend: Optional[EmbeddingBackend] = None,
    ) -> None:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(chroma_dir))
        self._backend = embedding_backend or get_default_backend()
        self._collections: dict[str, Collection] = {}

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------

    def _get_or_create(self, name: str) -> Collection:
        """Get or create a named collection (no embedding function — we embed externally)."""
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]

    def collection_live(self) -> Collection:
        return self._get_or_create(_COLLECTION_LIVE)

    def collection_retrieval(self) -> Collection:
        return self._get_or_create(_COLLECTION_RETRIEVAL)

    def collection_draft(self) -> Collection:
        return self._get_or_create(_COLLECTION_DRAFT)

    def _target_collections(self, approval_state: str) -> list[Collection]:
        """Return the collections a chunk with this approval_state should be indexed into."""
        targets: list[Collection] = []
        if approval_state in _LIVE_STATES:
            targets.append(self.collection_live())
        if approval_state in _RETRIEVAL_STATES:
            targets.append(self.collection_retrieval())
        if approval_state in _DRAFT_STATES:
            targets.append(self.collection_draft())
        return targets

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    def upsert_chunk(self, chunk: ChunkRecord) -> None:
        """
        Upsert one chunk into all appropriate collections.

        Embeddings are computed here and stored in ChromaDB.
        chunks with approval_state 'not_approved' or 'internal_draft_only'
        are NOT indexed (per approval_state_schema.json may_be_indexed).
        """
        if chunk.approval_state in ("not_approved", "internal_draft_only"):
            logger.debug(
                "Skipping %s: approval_state=%s not indexable",
                chunk.chunk_id, chunk.approval_state,
            )
            return

        collections = self._target_collections(chunk.approval_state)
        if not collections:
            logger.debug("No target collections for %s (state=%s)", chunk.chunk_id, chunk.approval_state)
            return

        embedding = self._backend.embed_one(chunk.text)
        metadata = chunk.to_chroma_metadata()

        for col in collections:
            col.upsert(
                ids=[chunk.chunk_id],
                embeddings=[embedding],
                documents=[chunk.text],
                metadatas=[metadata],
            )
        logger.debug("Upserted %s into %d collection(s)", chunk.chunk_id, len(collections))

    def upsert_chunks(self, chunks: list[ChunkRecord]) -> int:
        """Batch upsert. Returns count of chunks actually indexed."""
        indexed = 0
        for chunk in chunks:
            self.upsert_chunk(chunk)
            if chunk.approval_state not in ("not_approved", "internal_draft_only"):
                indexed += 1
        logger.info("Upserted %d / %d chunks", indexed, len(chunks))
        return indexed

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete_chunk(self, chunk_id: str) -> None:
        """Delete a chunk from all collections by chunk_id."""
        for col in [self.collection_live(), self.collection_retrieval(), self.collection_draft()]:
            try:
                col.delete(ids=[chunk_id])
            except Exception as exc:
                logger.debug("delete_chunk %s from %s: %s", chunk_id, col.name, exc)

    def delete_chunks_by_source(self, source_id: str) -> int:
        """
        Delete all chunks belonging to a source_id from all collections.

        Uses metadata filter where source_id == source_id.
        Returns approximate count deleted (from retrieval collection).
        """
        deleted_count = 0
        for col in [self.collection_live(), self.collection_retrieval(), self.collection_draft()]:
            try:
                results = col.get(where={"source_id": source_id}, include=[])
                ids = results.get("ids", [])
                if ids:
                    col.delete(ids=ids)
                    deleted_count = max(deleted_count, len(ids))
            except Exception as exc:
                logger.warning("delete_chunks_by_source %s from %s: %s", source_id, col.name, exc)
        logger.info("Deleted chunks for source %s from all collections", source_id)
        return deleted_count

    # ------------------------------------------------------------------
    # Query / search
    # ------------------------------------------------------------------

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = cfg.VECTOR_CANDIDATE_COUNT,
        where: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Perform a similarity search on the named collection.

        Returns list of dicts with chunk_id, cosine_distance, metadata, document.
        """
        col = self._get_or_create(collection_name)
        query_embedding = self._backend.embed_one(query_text)

        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, max(1, col.count())),
            "include": ["distances", "metadatas", "documents"],
        }
        if where:
            kwargs["where"] = where

        try:
            results = col.query(**kwargs)
        except Exception as exc:
            logger.warning("Chroma query failed on %s: %s", collection_name, exc)
            return []

        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        documents = results.get("documents", [[]])[0]

        return [
            {
                "chunk_id": cid,
                "cosine_distance": dist,
                "metadata": meta,
                "document": doc,
            }
            for cid, dist, meta, doc in zip(ids, distances, metadatas, documents)
        ]

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def collection_counts(self) -> dict[str, int]:
        """Return item counts for all three collections."""
        return {
            _COLLECTION_LIVE: self.collection_live().count(),
            _COLLECTION_RETRIEVAL: self.collection_retrieval().count(),
            _COLLECTION_DRAFT: self.collection_draft().count(),
        }

    def peek_collection(
        self, collection_name: str, n: int = 5
    ) -> list[dict[str, Any]]:
        """Return the first n records from a collection for inspection."""
        col = self._get_or_create(collection_name)
        result = col.peek(limit=n)
        ids = result.get("ids", [])
        metas = result.get("metadatas", [])
        docs = result.get("documents", [])
        return [
            {"chunk_id": cid, "metadata": m, "document": d}
            for cid, m, d in zip(ids, metas, docs)
        ]

    def reset_collection(self, collection_name: str) -> None:
        """Delete all records from a collection (non-destructive to disk — just clears data)."""
        col = self._get_or_create(collection_name)
        # Delete by getting all IDs first
        result = col.get(include=[])
        ids = result.get("ids", [])
        if ids:
            col.delete(ids=ids)
        logger.info("Reset collection %s (%d records removed)", collection_name, len(ids))

    def reset_all_collections(self) -> None:
        """Clear all three collections."""
        for name in [_COLLECTION_LIVE, _COLLECTION_RETRIEVAL, _COLLECTION_DRAFT]:
            self.reset_collection(name)
