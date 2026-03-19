"""
source_models.py — Pydantic v2 model for source-level records.

Field names and enum values must match source_register_schema.json and
controlled_vocabulary.json exactly.
"""

from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class SourceRecord(BaseModel):
    """
    One record per ingested source document.

    Maps to source_register_schema.json.
    Trust tier is propagated to chunk-level ChromaDB metadata at indexing time.
    """

    # Identity
    source_id: str = Field(
        ...,
        description="Unique internal source ID. Format: SRC-{FAMILY_CODE}-{NNN}",
    )
    title: str
    short_title: str

    # Classification
    source_family: str  # controlled_vocabulary.source_family
    source_type: str    # controlled_vocabulary.source_type
    institution_or_publisher: str
    author: Optional[str] = None
    publication_year: Optional[Union[str, int]] = None
    edition_or_version: Optional[str] = None

    # Access
    source_url: Optional[str] = None
    access_type: str    # controlled_vocabulary.access_type

    # Storage
    raw_file_name: str
    raw_file_path: str
    capture_date: str   # ISO 8601
    capture_method: str  # controlled_vocabulary.capture_method

    # Trust / scoring
    trust_tier: Optional[int] = None   # 1–5; null until reviewer assigns
    authority_score: Optional[int] = None   # 0–5
    extractability_score: Optional[int] = None
    coverage_value_score: Optional[int] = None
    density_score: Optional[int] = None
    priority_score: Optional[int] = None

    # Domain
    domain: str             # controlled_vocabulary.domain
    subdomain: Optional[str] = None
    materials_mentioned: list[str] = Field(default_factory=list)
    pigment_codes: list[str] = Field(default_factory=list)
    binder_types: list[str] = Field(default_factory=list)
    historical_period: str = "not_applicable"
    artist_or_school: list[str] = Field(default_factory=list)
    question_types_supported: list[str] = Field(default_factory=list)

    # Pipeline status flags
    raw_captured: bool = False
    normalized_text_created: bool = False
    tables_extracted: str = "not_applicable"  # controlled_vocabulary.tables_extracted
    metadata_attached: bool = False
    qa_reviewed: bool = False
    chunked: bool = False
    indexed: bool = False
    ready_for_use: bool = False

    # Scope / quality
    case_study_vs_general: str = "unknown"  # controlled_vocabulary.case_specificity
    claim_types_present: list[str] = Field(default_factory=list)
    confidence_level: str = "unverified"    # controlled_vocabulary.confidence_level

    # Deduplication
    duplicate_status: str = "unique"          # controlled_vocabulary.duplicate_status
    duplicate_cluster_id: Optional[str] = None
    superseded_by: Optional[str] = None

    # Governance
    limitations_notes: str = ""
    license_or_usage_notes: str = ""
    citation_format: str = ""
    summary: str = ""
    retrieval_notes: str = ""
    internal_notes: Optional[str] = None

    model_config = {"extra": "forbid"}

    @field_validator("trust_tier")
    @classmethod
    def validate_trust_tier(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (1, 2, 3, 4, 5):
            raise ValueError(f"trust_tier must be 1–5, got {v}")
        return v

    @field_validator("authority_score", "extractability_score", "coverage_value_score", "density_score")
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 5):
            raise ValueError(f"Score must be 0–5, got {v}")
        return v

    def to_chroma_propagation(self) -> dict:
        """
        Return fields that are propagated to chunk ChromaDB metadata at indexing.

        Per source_register_schema.json chroma_note.
        """
        return {
            "source_family": self.source_family,
            "source_type": self.source_type,
            "trust_tier": self.trust_tier,
            "citation_format": self.citation_format,
            "source_title": self.short_title,
        }
