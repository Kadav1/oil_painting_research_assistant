"""
lexical_index.py — BM25 lexical index for the Oil Painting Research Assistant.

Uses rank-bm25 (BM25Okapi). Index is persisted to disk via pickle.
Provides: build, query, incremental add/remove, persistence.

The lexical index is mandatory for hybrid retrieval — vector-only
retrieval is not acceptable per project spec.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)

_INDEX_FILE = cfg.LEXICAL_DIR / "bm25_index.pkl"
_CORPUS_FILE = cfg.LEXICAL_DIR / "bm25_corpus.pkl"


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer."""
    return text.lower().split()


class LexicalIndex:
    """
    BM25-based lexical index over all indexed chunk texts.

    The index maps chunk_id → BM25 ranked score for a query.
    Index is persisted to data/indexes/lexical/ for reuse across sessions.
    """

    def __init__(self, index_path: Path = _INDEX_FILE, corpus_path: Path = _CORPUS_FILE) -> None:
        self._index_path = index_path
        self._corpus_path = corpus_path
        self._bm25 = None
        self._chunk_ids: list[str] = []
        self._corpus: list[list[str]] = []   # tokenized texts

        # Ensure directory exists
        cfg.LEXICAL_DIR.mkdir(parents=True, exist_ok=True)

        # Try loading persisted index
        self._load()

    # ------------------------------------------------------------------
    # Build / rebuild
    # ------------------------------------------------------------------

    def build(self, chunks: list[tuple[str, str]]) -> None:
        """
        Build (or rebuild) the BM25 index from a list of (chunk_id, text) pairs.

        Replaces any existing index entirely.
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError as exc:
            raise ImportError(
                "rank-bm25 is required for lexical indexing. "
                "Install with: pip install rank-bm25"
            ) from exc

        if not chunks:
            logger.warning("build() called with empty chunks list — index will be empty")
            self._chunk_ids = []
            self._corpus = []
            self._bm25 = None
            return

        self._chunk_ids = [cid for cid, _ in chunks]
        self._corpus = [_tokenize(text) for _, text in chunks]
        self._bm25 = BM25Okapi(self._corpus)
        self._save()
        logger.info("Built BM25 index: %d chunks", len(self._chunk_ids))

    def add_chunk(self, chunk_id: str, text: str) -> None:
        """
        Add a single chunk to the index.

        Note: BM25Okapi requires a full rebuild for accurate scoring.
        This performs an incremental add + rebuild.
        """
        if chunk_id in self._chunk_ids:
            # Update existing entry
            idx = self._chunk_ids.index(chunk_id)
            self._corpus[idx] = _tokenize(text)
        else:
            self._chunk_ids.append(chunk_id)
            self._corpus.append(_tokenize(text))
        self._rebuild_from_corpus()
        self._save()

    def remove_chunk(self, chunk_id: str) -> None:
        """Remove a chunk from the index."""
        if chunk_id not in self._chunk_ids:
            return
        idx = self._chunk_ids.index(chunk_id)
        self._chunk_ids.pop(idx)
        self._corpus.pop(idx)
        self._rebuild_from_corpus()
        self._save()

    def remove_source(self, source_id: str) -> int:
        """Remove all chunks belonging to a source_id. Returns count removed."""
        prefix = f"CHK-{source_id}-"
        to_remove = [cid for cid in self._chunk_ids if cid.startswith(prefix)]
        for cid in to_remove:
            idx = self._chunk_ids.index(cid)
            self._chunk_ids.pop(idx)
            self._corpus.pop(idx)
        if to_remove:
            self._rebuild_from_corpus()
            self._save()
        return len(to_remove)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        query_text: str,
        n_results: int = cfg.LEXICAL_CANDIDATE_COUNT,
        allowed_chunk_ids: Optional[set[str]] = None,
    ) -> list[tuple[str, float]]:
        """
        Query the BM25 index.

        Args:
            query_text: The query string.
            n_results: Number of top results to return.
            allowed_chunk_ids: If provided, only return results for these IDs.

        Returns:
            List of (chunk_id, bm25_score) sorted by score descending.
        """
        if self._bm25 is None or not self._chunk_ids:
            logger.debug("BM25 index is empty or not built")
            return []

        tokens = _tokenize(query_text)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)

        # Pair with chunk IDs and filter
        scored = [
            (self._chunk_ids[i], float(scores[i]))
            for i in range(len(self._chunk_ids))
            if (allowed_chunk_ids is None or self._chunk_ids[i] in allowed_chunk_ids)
            and scores[i] > 0.0
        ]

        # Sort by score descending, take top n
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n_results]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        with self._index_path.open("wb") as fh:
            pickle.dump(self._bm25, fh)
        with self._corpus_path.open("wb") as fh:
            pickle.dump((self._chunk_ids, self._corpus), fh)

    def _load(self) -> None:
        if not self._index_path.exists() or not self._corpus_path.exists():
            return
        try:
            with self._index_path.open("rb") as fh:
                self._bm25 = pickle.load(fh)
            with self._corpus_path.open("rb") as fh:
                self._chunk_ids, self._corpus = pickle.load(fh)
            logger.info("Loaded BM25 index: %d chunks", len(self._chunk_ids))
        except Exception as exc:
            logger.warning("Could not load BM25 index: %s — starting fresh", exc)
            self._bm25 = None
            self._chunk_ids = []
            self._corpus = []

    def _rebuild_from_corpus(self) -> None:
        """Rebuild BM25 from current corpus (needed after add/remove)."""
        if not self._corpus:
            self._bm25 = None
            return
        try:
            from rank_bm25 import BM25Okapi
            self._bm25 = BM25Okapi(self._corpus)
        except ImportError:
            logger.error("rank-bm25 not available — lexical index disabled")
            self._bm25 = None

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return the number of indexed chunks."""
        return len(self._chunk_ids)

    def chunk_ids(self) -> list[str]:
        """Return all indexed chunk IDs."""
        return list(self._chunk_ids)
