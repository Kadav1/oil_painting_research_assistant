"""
chunk_models.py — Pydantic v2 model for chunk-level records.

Field names and enum values must match chunk_schema.json and
controlled_vocabulary.json exactly. chunk_id is the ChromaDB document ID.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from oil_painting_rag.utils.text_utils import pipe_encode, pipe_decode


class ChunkRecord(BaseModel):
    """
    One record per retrievable chunk.

    Maps to chunk_schema.json.
    chunk_id is the stable ChromaDB document ID — never regenerated.
    """

    # Identity
    chunk_id: str = Field(
        ...,
        description="Unique chunk ID. Format: CHK-{source_id}-{NNN}. ChromaDB doc ID.",
    )
    source_id: str
    chunk_index: int

    # Content
    chunk_title: str
    section_path: str
    page_range: Optional[str] = None
    text: str
    token_estimate: int

    # Classification
    chunk_type: str        # controlled_vocabulary.chunk_type
    domain: str            # controlled_vocabulary.domain
    subdomain: Optional[str] = None
    materials_mentioned: list[str] = Field(default_factory=list)
    pigment_codes: list[str] = Field(default_factory=list)
    binder_types: list[str] = Field(default_factory=list)
    historical_period: str = "not_applicable"
    artist_or_school: list[str] = Field(default_factory=list)
    question_types_supported: list[str] = Field(default_factory=list)
    claim_types_present: list[str] = Field(default_factory=list)

    # Scope / quality
    case_specificity: str = "unknown"   # controlled_vocabulary.case_specificity
    citability: str = "paraphrase_only"  # controlled_vocabulary.citability
    approval_state: str = "not_approved"  # controlled_vocabulary.approval_state
    retrieval_weight_hint: Optional[int] = None   # 0–5
    quality_flags: list[str] = Field(default_factory=list)
    restriction_flags: list[str] = Field(default_factory=list)

    # Review
    review_status: str = "draft"     # controlled_vocabulary.review_status

    # Deduplication
    duplicate_status: str = "unique"          # controlled_vocabulary.duplicate_status
    duplicate_cluster_id: Optional[str] = None

    # Propagated from parent source at indexing time
    source_family: str = ""
    source_type: str = ""
    trust_tier: int = 5          # default lowest until propagated
    source_title: str = ""
    citation_format: str = ""

    model_config = {"extra": "forbid"}

    @field_validator("retrieval_weight_hint")
    @classmethod
    def validate_weight_hint(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 5):
            raise ValueError(f"retrieval_weight_hint must be 0–5, got {v}")
        return v

    def to_chroma_metadata(self) -> dict[str, Any]:
        """
        Return the metadata dict for storage in ChromaDB.

        ChromaDB accepts only str, int, float, bool.
        List fields are pipe-encoded. None values use empty string.
        Per chunk_schema.json retrieval_critical_fields and chroma_note.
        """
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "chunk_index": self.chunk_index,
            "chunk_title": self.chunk_title,
            "section_path": self.section_path,
            "page_range": self.page_range or "",
            "token_estimate": self.token_estimate,
            "chunk_type": self.chunk_type,
            "domain": self.domain,
            "subdomain": self.subdomain or "",
            "materials_mentioned": pipe_encode(self.materials_mentioned),
            "pigment_codes": pipe_encode(self.pigment_codes),
            "binder_types": pipe_encode(self.binder_types),
            "historical_period": self.historical_period,
            "artist_or_school": pipe_encode(self.artist_or_school),
            "question_types_supported": pipe_encode(self.question_types_supported),
            "claim_types_present": pipe_encode(self.claim_types_present),
            "case_specificity": self.case_specificity,
            "citability": self.citability,
            "approval_state": self.approval_state,
            "retrieval_weight_hint": self.retrieval_weight_hint if self.retrieval_weight_hint is not None else -1,
            "quality_flags": pipe_encode(self.quality_flags),
            "restriction_flags": pipe_encode(self.restriction_flags),
            "review_status": self.review_status,
            "duplicate_status": self.duplicate_status,
            "duplicate_cluster_id": self.duplicate_cluster_id or "",
            "source_family": self.source_family,
            "source_type": self.source_type,
            "trust_tier": self.trust_tier,
            "source_title": self.source_title,
            "citation_format": self.citation_format,
        }

    @classmethod
    def from_chroma_metadata(cls, chunk_id: str, text: str, meta: dict[str, Any]) -> "ChunkRecord":
        """
        Reconstruct a ChunkRecord from ChromaDB metadata + document text.

        Decodes pipe-encoded list fields back to Python lists.
        """
        weight = meta.get("retrieval_weight_hint", -1)
        return cls(
            chunk_id=chunk_id,
            source_id=meta.get("source_id", ""),
            chunk_index=int(meta.get("chunk_index", 0)),
            chunk_title=meta.get("chunk_title", ""),
            section_path=meta.get("section_path", ""),
            page_range=meta.get("page_range") or None,
            text=text,
            token_estimate=int(meta.get("token_estimate", 0)),
            chunk_type=meta.get("chunk_type", "prose"),
            domain=meta.get("domain", "mixed"),
            subdomain=meta.get("subdomain") or None,
            materials_mentioned=pipe_decode(meta.get("materials_mentioned", "")),
            pigment_codes=pipe_decode(meta.get("pigment_codes", "")),
            binder_types=pipe_decode(meta.get("binder_types", "")),
            historical_period=meta.get("historical_period", "not_applicable"),
            artist_or_school=pipe_decode(meta.get("artist_or_school", "")),
            question_types_supported=pipe_decode(meta.get("question_types_supported", "")),
            claim_types_present=pipe_decode(meta.get("claim_types_present", "")),
            case_specificity=meta.get("case_specificity", "unknown"),
            citability=meta.get("citability", "paraphrase_only"),
            approval_state=meta.get("approval_state", "not_approved"),
            retrieval_weight_hint=weight if weight >= 0 else None,
            quality_flags=pipe_decode(meta.get("quality_flags", "")),
            restriction_flags=pipe_decode(meta.get("restriction_flags", "")),
            review_status=meta.get("review_status", "draft"),
            duplicate_status=meta.get("duplicate_status", "unique"),
            duplicate_cluster_id=meta.get("duplicate_cluster_id") or None,
            source_family=meta.get("source_family", ""),
            source_type=meta.get("source_type", ""),
            trust_tier=int(meta.get("trust_tier", 5)),
            source_title=meta.get("source_title", ""),
            citation_format=meta.get("citation_format", ""),
        )
