"""indexing — ChromaDB and BM25 index management for the Oil Painting Research Assistant."""

from oil_painting_rag.indexing.embeddings import EmbeddingBackend, SentenceTransformerBackend, get_default_backend
from oil_painting_rag.indexing.chroma_index import ChromaIndex
from oil_painting_rag.indexing.lexical_index import LexicalIndex
from oil_painting_rag.indexing.index_manager import IndexManager

__all__ = [
    "EmbeddingBackend",
    "SentenceTransformerBackend",
    "get_default_backend",
    "ChromaIndex",
    "LexicalIndex",
    "IndexManager",
]
