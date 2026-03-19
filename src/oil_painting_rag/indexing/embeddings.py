"""
embeddings.py — Pluggable embedding backend for the Oil Painting Research Assistant.

Default backend: sentence-transformers (local, no external API calls).
Backend is swappable via config.EMBEDDING_MODEL.

Design: EmbeddingBackend abstract interface + SentenceTransformerBackend concrete.
The indexing layer depends only on the interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional

import numpy as np

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger

logger = get_logger(__name__)


class EmbeddingBackend(ABC):
    """Abstract interface for embedding backends."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for a list of texts."""

    @abstractmethod
    def embed_one(self, text: str) -> list[float]:
        """Return the embedding for a single text."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""


class SentenceTransformerBackend(EmbeddingBackend):
    """
    Embedding backend using sentence-transformers (local, CPU or GPU).

    Model is lazily loaded on first use.
    """

    def __init__(
        self,
        model_name: str = cfg.EMBEDDING_MODEL,
        device: str = cfg.EMBEDDING_DEVICE,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._model = None  # lazy load

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s (device=%s)", self._model_name, self._device)
            # Try local cache first; fall back to network download if not cached.
            try:
                self._model = SentenceTransformer(
                    self._model_name, device=self._device, local_files_only=True
                )
            except Exception:
                self._model = SentenceTransformer(self._model_name, device=self._device)
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            ) from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Returns list of float vectors."""
        self._load()
        if not texts:
            return []
        vectors = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    def embed_one(self, text: str) -> list[float]:
        """Embed a single text string."""
        self._load()
        vector = self._model.encode([text], convert_to_numpy=True, show_progress_bar=False)
        return vector[0].tolist()

    @property
    def dimension(self) -> int:
        self._load()
        return self._model.get_sentence_embedding_dimension()


@lru_cache(maxsize=1)
def get_default_backend() -> EmbeddingBackend:
    """Return the cached default embedding backend instance."""
    return SentenceTransformerBackend(
        model_name=cfg.EMBEDDING_MODEL,
        device=cfg.EMBEDDING_DEVICE,
    )
