"""
diversity.py — Diversity control and deduplication for retrieval results.

Prevents:
- One source flooding the context window (max chunks per source_id)
- Duplicate clusters dominating context (suppress non-canonical duplicates)
- Repetitive product boilerplate dominating results
- Token budget overrun

Per spec: chunk_ids from confirmed_duplicate clusters are suppressed in favor
of the canonical member.
"""

from __future__ import annotations

from typing import Any

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.retrieval_models import SelectedChunk
from oil_painting_rag.policies.retrieval_policy import chunk_passes_gate
from oil_painting_rag.utils.text_utils import estimate_tokens

logger = get_logger(__name__)


class DiversityFilter:
    """
    Selects a diverse, token-budget-aware subset from the reranked pool.

    Selection order: highest rerank_score first, subject to:
    - Approval state gate enforcement (final check)
    - Max chunks per source_id
    - Duplicate cluster suppression
    - Token budget
    """

    def __init__(
        self,
        max_chunks_per_source: int = cfg.MAX_CHUNKS_PER_SOURCE,
    ) -> None:
        self.max_chunks_per_source = max_chunks_per_source

    def select(
        self,
        reranked: list[dict[str, Any]],
        chunks: list[ChunkRecord],
        top_k: int = cfg.RETRIEVAL_TOP_K,
        token_budget: int = cfg.RETRIEVAL_TOKEN_BUDGET,
        approval_gate: str = cfg.DEFAULT_RETRIEVAL_GATE,
    ) -> tuple[list[SelectedChunk], list[dict[str, Any]]]:
        """
        Select up to top_k diverse chunks within the token budget.

        Returns (selected_chunks, excluded_list).
        excluded_list entries: {chunk_id, reason}
        """
        chunks_by_id: dict[str, ChunkRecord] = {c.chunk_id: c for c in chunks}
        selected: list[SelectedChunk] = []
        excluded: list[dict[str, Any]] = []

        source_counts: dict[str, int] = {}
        seen_cluster_ids: set[str] = set()
        tokens_used = 0

        for item in reranked:
            cid = item["chunk_id"]
            chunk = chunks_by_id.get(cid)
            if chunk is None:
                continue

            # Gate: approval state (final enforcement)
            if not chunk_passes_gate(chunk.approval_state, approval_gate):
                excluded.append({"chunk_id": cid, "reason": "approval_gate"})
                continue

            # Gate: duplicate suppression
            if chunk.duplicate_status in ("confirmed_duplicate", "superseded"):
                excluded.append({"chunk_id": cid, "reason": "duplicate_suppressed"})
                continue

            # Gate: duplicate cluster (keep only one from each cluster)
            if chunk.duplicate_cluster_id:
                if chunk.duplicate_cluster_id in seen_cluster_ids:
                    excluded.append({"chunk_id": cid, "reason": "duplicate_suppressed"})
                    continue

            # Gate: max chunks per source
            source_count = source_counts.get(chunk.source_id, 0)
            if source_count >= self.max_chunks_per_source:
                excluded.append({"chunk_id": cid, "reason": "diversity_cap"})
                continue

            # Gate: token budget
            chunk_tokens = estimate_tokens(chunk.text)
            if tokens_used + chunk_tokens > token_budget and selected:
                excluded.append({"chunk_id": cid, "reason": "token_budget_exceeded"})
                continue

            # Accept
            if chunk.duplicate_cluster_id:
                seen_cluster_ids.add(chunk.duplicate_cluster_id)
            source_counts[chunk.source_id] = source_count + 1
            tokens_used += chunk_tokens

            reason = self._selection_reason(item, chunk)
            selected.append(SelectedChunk(
                chunk_id=cid,
                source_id=chunk.source_id,
                chunk_title=chunk.chunk_title,
                text=chunk.text,
                trust_tier=chunk.trust_tier,
                domain=chunk.domain,
                case_specificity=chunk.case_specificity,
                citability=chunk.citability,
                citation_format=chunk.citation_format,
                rerank_score=item.get("rerank_score"),
                selection_reason=reason,
            ))

            if len(selected) >= top_k:
                break

        logger.debug(
            "Diversity: selected %d, excluded %d, tokens=%d",
            len(selected), len(excluded), tokens_used,
        )
        return selected, excluded

    def _selection_reason(self, item: dict, chunk: ChunkRecord) -> str:
        """Build a human-readable reason for why this chunk was selected."""
        reasons: list[str] = []
        score = item.get("rerank_score", 0.0)
        if score > 0.7:
            reasons.append("top_reranked")
        if chunk.trust_tier == 1:
            reasons.append("tier_1_source")
        if chunk.case_specificity == "broadly_applicable":
            reasons.append("broadly_applicable")
        return ",".join(reasons) if reasons else "ranked_selection"
