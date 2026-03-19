"""
index_manager.py — High-level index management for the Oil Painting Research Assistant.

Provides a unified interface over ChromaDB and BM25 indexes.
Responsibilities:
- Upsert chunks into both indexes
- Delete chunks by chunk_id or source_id
- Rebuild all indexes from chunk files on disk
- Partial incremental updates
- Status inspection
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.chunking.chunk_validators import validate_chunk_list
from oil_painting_rag.indexing.chroma_index import ChromaIndex
from oil_painting_rag.indexing.embeddings import EmbeddingBackend
from oil_painting_rag.indexing.lexical_index import LexicalIndex
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.storage.filesystem_store import FilesystemStore
from oil_painting_rag.storage.register_store import RegisterStore

logger = get_logger(__name__)


class IndexManager:
    """
    Coordinates ChromaDB and BM25 index operations.

    All index writes go through this manager — not directly through
    ChromaIndex or LexicalIndex.
    """

    def __init__(
        self,
        chroma_dir: Path = cfg.CHROMA_DIR,
        embedding_backend: Optional[EmbeddingBackend] = None,
    ) -> None:
        self._chroma = ChromaIndex(chroma_dir=chroma_dir, embedding_backend=embedding_backend)
        self._lexical = LexicalIndex()
        self._fs = FilesystemStore()
        self._register = RegisterStore()

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    def upsert_chunk(self, chunk: ChunkRecord) -> bool:
        """
        Upsert a single chunk into both indexes.

        Validates the chunk first; skips and logs if validation fails.
        Returns True if indexed, False if skipped.
        """
        issues = validate_chunk_list([chunk])[1]
        critical = [i for i in issues if "text is empty" in i or "source_id is missing" in i]
        if critical:
            logger.warning("Skipping invalid chunk %s: %s", chunk.chunk_id, critical)
            return False

        # ChromaDB (handles approval_state gating internally)
        self._chroma.upsert_chunk(chunk)

        # BM25 — index all non-rejected chunks (retrieval gating is in the retrieval layer)
        if chunk.approval_state not in ("not_approved",):
            self._lexical.add_chunk(chunk.chunk_id, chunk.text)

        return True

    def upsert_chunks(self, chunks: list[ChunkRecord]) -> int:
        """Upsert a batch of chunks. Returns count indexed."""
        valid, issues = validate_chunk_list(chunks)
        if issues:
            logger.warning("Chunk validation: %d issue(s)", len(issues))

        indexed = 0
        for chunk in valid:
            if self.upsert_chunk(chunk):
                indexed += 1
        logger.info("IndexManager: upserted %d / %d chunks", indexed, len(chunks))
        return indexed

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete_chunk(self, chunk_id: str) -> None:
        """Delete a chunk from both indexes."""
        self._chroma.delete_chunk(chunk_id)
        self._lexical.remove_chunk(chunk_id)
        logger.debug("Deleted chunk %s from all indexes", chunk_id)

    def delete_source(self, source_id: str) -> int:
        """Delete all chunks for a source from both indexes."""
        chroma_count = self._chroma.delete_chunks_by_source(source_id)
        lexical_count = self._lexical.remove_source(source_id)
        logger.info(
            "Deleted source %s: ~%d from Chroma, %d from BM25",
            source_id, chroma_count, lexical_count,
        )
        return max(chroma_count, lexical_count)

    # ------------------------------------------------------------------
    # Rebuild
    # ------------------------------------------------------------------

    def rebuild_from_files(self, source_id: Optional[str] = None) -> int:
        """
        Rebuild both indexes from chunk files on disk.

        If source_id is given, rebuilds only that source's chunks.
        Otherwise rebuilds the entire corpus.
        Returns count of chunks indexed.
        """
        if source_id:
            # Clear this source's entries first
            self.delete_source(source_id)
            chunk_ids = self._fs.chunk_ids_for_source(source_id)
        else:
            # Full rebuild: reset all collections, then re-index everything
            logger.info("Starting full index rebuild from disk")
            self._chroma.reset_all_collections()
            # BM25 will be rebuilt via build() below
            chunk_ids = self._all_chunk_ids_on_disk()

        chunks = self._load_chunks_from_files(chunk_ids)
        if not chunks:
            logger.warning("No chunks found to index")
            return 0

        # For full rebuild, also rebuild BM25 from scratch (more efficient)
        if not source_id:
            corpus = [(c.chunk_id, c.text) for c in chunks
                      if c.approval_state not in ("not_approved",)]
            self._lexical.build(corpus)
            # ChromaDB upsert
            return self._chroma.upsert_chunks(chunks)

        return self.upsert_chunks(chunks)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def status(self) -> dict[str, object]:
        """Return index status summary."""
        return {
            "chroma_counts": self._chroma.collection_counts(),
            "bm25_size": self._lexical.size(),
        }

    def peek(self, collection_name: str = cfg.CHROMA_COLLECTION_RETRIEVAL, n: int = 5) -> list[dict]:
        return self._chroma.peek_collection(collection_name, n=n)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _all_chunk_ids_on_disk(self) -> list[str]:
        """Collect all chunk_ids found in the chunk metadata directory."""
        metadata_dir = cfg.CHUNKS_METADATA_DIR
        if not metadata_dir.exists():
            return []
        return [f.stem for f in sorted(metadata_dir.glob("CHK-*.json"))]

    def _load_chunks_from_files(self, chunk_ids: list[str]) -> list[ChunkRecord]:
        """Load ChunkRecord objects from filesystem chunk files."""
        chunks: list[ChunkRecord] = []
        for cid in chunk_ids:
            text = self._fs.load_chunk_text(cid)
            meta = self._fs.load_chunk_metadata(cid)
            if text is None or meta is None:
                logger.debug("Missing file for chunk %s — skipping", cid)
                continue
            try:
                chunk = ChunkRecord.from_chroma_metadata(cid, text, meta)
                chunks.append(chunk)
            except Exception as exc:
                logger.warning("Could not load chunk %s: %s", cid, exc)
        return chunks

    # ------------------------------------------------------------------
    # Expose underlying indexes for retrieval layer
    # ------------------------------------------------------------------

    @property
    def chroma(self) -> ChromaIndex:
        return self._chroma

    @property
    def lexical(self) -> LexicalIndex:
        return self._lexical
