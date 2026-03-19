"""
hybrid_retriever.py — Full hybrid retrieval pipeline for the Oil Painting Research Assistant.

Pipeline (mandatory — no shortcuts):
  1. Query classification
  2. Filter construction (approval gate + domain)
  3. ChromaDB vector search
  4. BM25 lexical search
  5. RRF merge
  6. Metadata-complete chunk loading
  7. Multi-factor reranking
  8. Diversity + deduplication
  9. Context package assembly

Vector-only retrieval is NOT acceptable. BM25 leg is always executed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.indexing.chroma_index import ChromaIndex
from oil_painting_rag.indexing.index_manager import IndexManager
from oil_painting_rag.indexing.lexical_index import LexicalIndex
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.retrieval_models import (
    ContextPackage,
    LexicalCandidate,
    MergedCandidate,
    QueryClassification,
    RetrievalRequest,
    RetrievalTrace,
    VectorCandidate,
)
from oil_painting_rag.policies.retrieval_policy import (
    chunk_passes_gate,
    validate_retrieval_gate,
)
from oil_painting_rag.retrieval.citation_assembler import CitationAssembler
from oil_painting_rag.retrieval.classifier import classify_query
from oil_painting_rag.retrieval.diversity import DiversityFilter
from oil_painting_rag.retrieval.filters import build_retrieval_filters
from oil_painting_rag.retrieval.reranker import Reranker
from oil_painting_rag.storage.metadata_store import MetadataStore
from oil_painting_rag.utils.hash_utils import make_package_id, make_trace_id

logger = get_logger(__name__)


class HybridRetriever:
    """
    Executes the full hybrid retrieval pipeline for one query.

    Requires both ChromaDB vector search and BM25 lexical search.
    Enforces approval_state gating on every result.
    """

    def __init__(self, index_manager: IndexManager) -> None:
        self._index = index_manager
        self._chroma: ChromaIndex = index_manager.chroma
        self._lexical: LexicalIndex = index_manager.lexical
        self._reranker = Reranker()
        self._diversity = DiversityFilter()
        self._citations = CitationAssembler()
        self._meta_store = MetadataStore()

    def retrieve(
        self,
        request: RetrievalRequest,
        classification: Optional[QueryClassification] = None,
    ) -> ContextPackage:
        """
        Execute the full hybrid retrieval pipeline.

        Returns a ContextPackage ready for the generation layer.
        """
        validate_retrieval_gate(request.approval_gate)

        # Step 1: Classify query
        classification = classification or classify_query(request.query)
        warnings: list[str] = []

        # Step 2: Build ChromaDB filter
        chroma_filter = build_retrieval_filters(
            classification,
            approval_gate=request.approval_gate,
            extra_filters=request.filters or {},
        )

        # Determine collection based on gate
        collection_name = self._collection_for_gate(request.approval_gate)

        # Step 3: Vector search (ChromaDB)
        vector_raw = self._chroma.query_collection(
            collection_name=collection_name,
            query_text=request.query,
            n_results=cfg.VECTOR_CANDIDATE_COUNT,
            where=chroma_filter or None,
        )
        vector_candidates = [
            VectorCandidate(
                chunk_id=r["chunk_id"],
                cosine_distance=r["cosine_distance"],
                rank=i,
            )
            for i, r in enumerate(vector_raw)
        ]

        if not vector_candidates:
            warnings.append("Vector search returned no candidates")

        # Step 4: Lexical search (BM25)
        # Get chunk IDs from ChromaDB collection to constrain BM25 to same gate
        allowed_ids = self._get_allowed_chunk_ids(collection_name, chroma_filter)
        lexical_raw = self._lexical.query(
            request.query,
            n_results=cfg.LEXICAL_CANDIDATE_COUNT,
            allowed_chunk_ids=allowed_ids if allowed_ids else None,
        )
        lexical_candidates = [
            LexicalCandidate(chunk_id=cid, bm25_score=score, rank=i)
            for i, (cid, score) in enumerate(lexical_raw)
        ]

        if not lexical_candidates:
            warnings.append("Lexical search returned no candidates")

        # Step 5: RRF merge
        merged = self._rrf_merge(vector_candidates, lexical_candidates)

        # Step 6: Load chunk metadata for all merged candidates
        chunks = self._load_chunks(
            merged, vector_raw, collection_name
        )

        # Step 7: Rerank
        reranked = self._reranker.rerank(
            query=request.query,
            chunks=chunks,
            merged_pool=merged,
            classification=classification,
        )

        # Step 8: Diversity + deduplication
        selected, excluded = self._diversity.select(
            reranked=reranked,
            chunks=chunks,
            top_k=request.top_k,
            token_budget=request.token_budget,
            approval_gate=request.approval_gate,
        )

        if not selected:
            warnings.append("No chunks passed diversity selection")

        # Step 9: Check for conflict disclosures
        selected_chunk_ids = [c.chunk_id for c in selected]
        all_conflicts = self._meta_store.load_all_conflicts()
        conflict_notes = self._get_conflict_notes(selected_chunk_ids, all_conflicts)

        # Step 10: Assemble context package
        package_id = make_package_id()
        package = self._citations.assemble(
            package_id=package_id,
            query=request.query,
            classification=classification,
            selected_chunks=selected,
            chunks_by_id={c.chunk_id: c for c in chunks},
            filters_applied=chroma_filter,
            conflict_notes=conflict_notes,
            token_budget=request.token_budget,
            warnings=warnings,
        )

        # Optionally write retrieval trace
        if request.enable_trace:
            trace = self._build_trace(
                query=request.query,
                classification=classification,
                filters=chroma_filter,
                vector_candidates=vector_candidates,
                lexical_candidates=lexical_candidates,
                merged=merged,
                reranked=reranked,
                selected=selected,
                excluded=excluded,
                conflict_notes=conflict_notes,
                package_id=package_id,
                warnings=warnings,
                chunks_by_id={c.chunk_id: c for c in chunks},
            )
            self._meta_store.save_trace(trace.model_dump())
            package.retrieval_trace_id = trace.trace_id

        return package

    # ------------------------------------------------------------------
    # RRF merge
    # ------------------------------------------------------------------

    def _rrf_merge(
        self,
        vector: list[VectorCandidate],
        lexical: list[LexicalCandidate],
        k: int = cfg.RRF_K,
    ) -> list[MergedCandidate]:
        """
        Reciprocal Rank Fusion of vector and lexical candidates.

        score = 1/(k + rank_vector) + 1/(k + rank_lexical)
        """
        scores: dict[str, float] = {}
        sources: dict[str, list[str]] = {}

        for cand in vector:
            cid = cand.chunk_id
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + cand.rank + 1)
            sources.setdefault(cid, []).append("vector")

        for cand in lexical:
            cid = cand.chunk_id
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + cand.rank + 1)
            sources.setdefault(cid, []).append("lexical")

        merged = [
            MergedCandidate(chunk_id=cid, merge_score=score, sources=sources[cid])
            for cid, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]
        return merged

    # ------------------------------------------------------------------
    # Chunk loading
    # ------------------------------------------------------------------

    def _load_chunks(
        self,
        merged: list[MergedCandidate],
        vector_raw: list[dict],
        collection_name: str,
    ) -> list[ChunkRecord]:
        """
        Load ChunkRecord objects from ChromaDB metadata for merged candidates.

        Falls back to querying ChromaDB by ID for chunks not in vector_raw.
        """
        # Build map from vector results
        vector_map: dict[str, dict] = {r["chunk_id"]: r for r in vector_raw}
        chunks: list[ChunkRecord] = []

        for candidate in merged:
            cid = candidate.chunk_id
            if cid in vector_map:
                r = vector_map[cid]
                try:
                    chunk = ChunkRecord.from_chroma_metadata(
                        cid, r.get("document", ""), r.get("metadata", {})
                    )
                    chunks.append(chunk)
                except Exception as exc:
                    logger.warning("Could not reconstruct chunk %s: %s", cid, exc)
            else:
                # Chunk came from lexical but not vector — fetch from Chroma
                try:
                    col = self._chroma._get_or_create(collection_name)
                    result = col.get(ids=[cid], include=["metadatas", "documents"])
                    ids = result.get("ids", [])
                    if ids:
                        meta = result["metadatas"][0]
                        doc = result["documents"][0]
                        chunk = ChunkRecord.from_chroma_metadata(cid, doc, meta)
                        chunks.append(chunk)
                except Exception as exc:
                    logger.debug("Could not fetch lexical-only chunk %s: %s", cid, exc)

        return chunks

    def _get_allowed_chunk_ids(
        self,
        collection_name: str,
        chroma_filter: dict,
    ) -> set[str]:
        """Get all chunk IDs from the collection matching the filter (for BM25 constraint)."""
        try:
            col = self._chroma._get_or_create(collection_name)
            kwargs: dict = {"include": []}
            if chroma_filter:
                kwargs["where"] = chroma_filter
            result = col.get(**kwargs)
            return set(result.get("ids", []))
        except Exception as exc:
            logger.debug("Could not fetch allowed IDs: %s", exc)
            return set()

    def _collection_for_gate(self, gate: str) -> str:
        if gate == "live_allowed":
            return cfg.CHROMA_COLLECTION_LIVE
        if gate == "testing_only":
            return cfg.CHROMA_COLLECTION_DRAFT
        return cfg.CHROMA_COLLECTION_RETRIEVAL

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def _get_conflict_notes(
        self,
        chunk_ids: list[str],
        all_conflicts: list[dict],
    ):
        from oil_painting_rag.policies.conflict_policy import find_active_conflicts
        return find_active_conflicts(chunk_ids, all_conflicts)

    # ------------------------------------------------------------------
    # Trace building
    # ------------------------------------------------------------------

    def _build_trace(
        self,
        query: str,
        classification: QueryClassification,
        filters: dict,
        vector_candidates: list[VectorCandidate],
        lexical_candidates: list[LexicalCandidate],
        merged: list[MergedCandidate],
        reranked: list,
        selected: list,
        excluded: list,
        conflict_notes: list,
        package_id: str,
        warnings: list[str],
        chunks_by_id: dict,
    ) -> RetrievalTrace:
        from oil_painting_rag.models.retrieval_models import RerankedResult, ExcludedCandidate
        now = datetime.now(tz=timezone.utc).isoformat()

        reranked_results = []
        for i, item in enumerate(reranked):
            chunk = chunks_by_id.get(item["chunk_id"])
            reranked_results.append(RerankedResult(
                chunk_id=item["chunk_id"],
                rerank_score=item.get("rerank_score", 0.0),
                trust_tier=chunk.trust_tier if chunk else 5,
                domain=chunk.domain if chunk else "mixed",
                case_specificity=chunk.case_specificity if chunk else "unknown",
                rank_after_rerank=i,
            ))

        selected_context = [
            {"chunk_id": c.chunk_id, "selection_reason": c.selection_reason, "token_estimate": c.text and len(c.text.split()) or 0}
            for c in selected
        ]

        tier_coverage: dict[str, int] = {}
        for c in selected:
            chunk = chunks_by_id.get(c.chunk_id)
            if chunk:
                tier_key = str(chunk.trust_tier)
                tier_coverage[tier_key] = tier_coverage.get(tier_key, 0) + 1

        excluded_list = [
            ExcludedCandidate(chunk_id=e["chunk_id"], exclusion_reason=e["reason"])
            for e in excluded
        ]

        return RetrievalTrace(
            trace_id=make_trace_id(),
            query=query,
            query_classification=classification,
            filters_applied=filters,
            lexical_candidates=lexical_candidates,
            vector_candidates=vector_candidates,
            merged_candidate_pool=merged,
            reranked_results=reranked_results,
            selected_context_chunks=selected_context,
            excluded_candidates=excluded_list,
            conflict_notes=conflict_notes,
            tier_coverage=tier_coverage,
            trace_timestamp=now,
            context_package_id=package_id,
            pipeline_warnings=warnings,
        )
