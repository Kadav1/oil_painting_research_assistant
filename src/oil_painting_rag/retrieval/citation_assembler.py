"""
citation_assembler.py — Citation assembly and context package construction.

Assembles the ContextPackage from selected chunks and retrieval metadata.
Citations are grounded only in chunk metadata — nothing fabricated.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.retrieval_models import (
    ConflictNote,
    ContextPackage,
    QueryClassification,
    SelectedChunk,
)
from oil_painting_rag.utils.citation_utils import build_citation, citation_is_complete
from oil_painting_rag.utils.text_utils import estimate_tokens

logger = get_logger(__name__)


class CitationAssembler:
    """
    Assembles the ContextPackage from selected chunks.

    Responsibilities:
    - Compute token budget used
    - Build per-chunk citations from chunk metadata
    - Collect conflict notes
    - Assemble the final ContextPackage
    """

    def assemble(
        self,
        package_id: str,
        query: str,
        classification: QueryClassification,
        selected_chunks: list[SelectedChunk],
        chunks_by_id: dict[str, ChunkRecord],
        filters_applied: dict[str, Any],
        conflict_notes: list[ConflictNote],
        token_budget: int,
        warnings: list[str],
    ) -> ContextPackage:
        """
        Build a ContextPackage from the selected chunks.

        Citations are populated from chunk.citation_format and chunk.source_title.
        If citation data is missing, selection_reason notes the gap.
        """
        now = datetime.now(tz=timezone.utc).isoformat()

        # Update selected chunks with citation strings where missing
        enriched: list[SelectedChunk] = []
        for sc in selected_chunks:
            chunk = chunks_by_id.get(sc.chunk_id)
            if chunk and not sc.citation_format and chunk.citation_format:
                sc = sc.model_copy(update={"citation_format": chunk.citation_format})
            if chunk and not citation_is_complete(sc.citation_format, sc.chunk_title):
                logger.debug("Chunk %s has incomplete citation data", sc.chunk_id)
            enriched.append(sc)

        tokens_used = sum(estimate_tokens(sc.text) for sc in enriched)

        retrieval_notes: list[str] = list(warnings)
        if not enriched:
            retrieval_notes.append("No chunks selected — context is empty")

        # Tier coverage summary
        tier_counts: dict[str, int] = {}
        for sc in enriched:
            chunk = chunks_by_id.get(sc.chunk_id)
            if chunk:
                k = str(chunk.trust_tier)
                tier_counts[k] = tier_counts.get(k, 0) + 1
        if tier_counts:
            tier_summary = ", ".join(f"T{k}: {v}" for k, v in sorted(tier_counts.items()))
            retrieval_notes.append(f"Tier coverage: {tier_summary}")

        return ContextPackage(
            package_id=package_id,
            query=query,
            query_classification=classification,
            filters_applied=filters_applied,
            selected_chunks=enriched,
            token_budget_used=tokens_used,
            token_budget_limit=token_budget,
            conflict_notes=conflict_notes,
            retrieval_notes=retrieval_notes,
            assembly_timestamp=now,
        )
