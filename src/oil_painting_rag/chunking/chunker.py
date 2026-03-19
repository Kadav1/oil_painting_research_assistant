"""
chunker.py — Semantic prose chunker for the Oil Painting Research Assistant.

Splits normalized markdown text into ChunkRecord objects using:
- Heading boundaries (split on heading changes)
- Sentence windowing within sections (token budget)
- Paragraph boundaries as fallback

Chunk types: prose, glossary, mixed.
Table content is handled by table_chunker.py.
"""

from __future__ import annotations

import re
from typing import Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.source_models import SourceRecord
from oil_painting_rag.utils.hash_utils import make_chunk_id
from oil_painting_rag.utils.text_utils import (
    build_section_path,
    clean_text,
    estimate_tokens,
    heading_lines,
    iter_windows,
    pipe_encode,
    slugify,
    split_sentences,
)

logger = get_logger(__name__)


class ProseChunker:
    """
    Splits normalized markdown text into prose-type ChunkRecords.

    Configuration comes from config.py:
    - CHUNK_MAX_TOKENS: maximum tokens per chunk
    - CHUNK_MIN_TOKENS: minimum tokens to accept a chunk (filter stubs)
    - CHUNK_OVERLAP_SENTENCES: sentence overlap between adjacent windows
    """

    def __init__(
        self,
        max_tokens: int = cfg.CHUNK_MAX_TOKENS,
        min_tokens: int = cfg.CHUNK_MIN_TOKENS,
        overlap_sentences: int = cfg.CHUNK_OVERLAP_SENTENCES,
    ) -> None:
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.overlap_sentences = overlap_sentences

    def chunk_source(
        self,
        source: SourceRecord,
        text: str,
        start_index: int = 0,
    ) -> list[ChunkRecord]:
        """
        Chunk a source's full normalized text into ChunkRecord objects.

        Args:
            source: The parent SourceRecord (for metadata propagation).
            text: The full normalized text/markdown content.
            start_index: Starting chunk_index offset (for mixed chunkers that
                         have already produced table chunks).

        Returns:
            List of ChunkRecord objects with metadata populated.
        """
        text = clean_text(text)
        headings = heading_lines(text)
        sections = self._split_by_headings(text, headings)

        chunks: list[ChunkRecord] = []
        chunk_index = start_index

        for section_start_line, section_heading, section_text in sections:
            chunk_type = self._detect_chunk_type(section_text)
            section_path = build_section_path(headings, section_start_line)

            sentences = split_sentences(section_text)
            if not sentences:
                continue

            for window in iter_windows(sentences, self.max_tokens, self.overlap_sentences):
                chunk_text = " ".join(window)
                token_est = estimate_tokens(chunk_text)

                if token_est < self.min_tokens:
                    logger.debug(
                        "Skipping short chunk (%d tokens) in %s",
                        token_est, source.source_id,
                    )
                    continue

                chunk_id = make_chunk_id(source.source_id, chunk_index)
                chunk_title = self._make_chunk_title(section_heading, chunk_index)

                quality_flags = self._assess_quality(chunk_text, token_est)

                chunk = ChunkRecord(
                    chunk_id=chunk_id,
                    source_id=source.source_id,
                    chunk_index=chunk_index,
                    chunk_title=chunk_title,
                    section_path=section_path,
                    text=chunk_text,
                    token_estimate=token_est,
                    chunk_type=chunk_type,
                    domain=source.domain,
                    subdomain=source.subdomain,
                    materials_mentioned=list(source.materials_mentioned),
                    pigment_codes=list(source.pigment_codes),
                    binder_types=list(source.binder_types),
                    historical_period=source.historical_period,
                    artist_or_school=list(source.artist_or_school),
                    question_types_supported=list(source.question_types_supported),
                    claim_types_present=list(source.claim_types_present),
                    case_specificity=source.case_study_vs_general,
                    citability=self._infer_citability(source),
                    approval_state="not_approved",
                    quality_flags=quality_flags,
                    review_status="draft",
                    duplicate_status="unique",
                    # Propagate from source
                    source_family=source.source_family,
                    source_type=source.source_type,
                    trust_tier=source.trust_tier or 5,
                    source_title=source.short_title,
                    citation_format=source.citation_format,
                )
                chunks.append(chunk)
                chunk_index += 1

        logger.info(
            "Chunked source %s: %d prose chunks", source.source_id, len(chunks)
        )
        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _split_by_headings(
        self,
        text: str,
        headings: list[tuple[int, str, str]],
    ) -> list[tuple[int, str, str]]:
        """
        Split text into (start_line, heading_text, section_content) tuples.

        Each section runs from one heading to the next.
        If no headings exist, treats the whole text as one section.
        """
        lines = text.splitlines()
        if not headings:
            return [(0, "content", text)]

        sections: list[tuple[int, str, str]] = []
        heading_positions = [(ln, title) for ln, _, title in headings]

        for i, (line_no, title) in enumerate(heading_positions):
            # Section content starts after the heading line
            start = line_no + 1
            end = heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(lines)
            section_lines = lines[start:end]
            section_text = "\n".join(section_lines).strip()
            if section_text:
                sections.append((line_no, title, section_text))

        return sections

    def _detect_chunk_type(self, text: str) -> str:
        """Infer chunk type from content patterns."""
        # Glossary detection: lines with "term: definition" pattern
        glossary_lines = sum(
            1 for ln in text.splitlines()
            if re.match(r"^\*{0,2}[A-Z][^:]{1,40}:\*{0,2}\s+\w", ln)
        )
        if glossary_lines > 3:
            return "glossary"
        return "prose"

    def _make_chunk_title(self, heading: str, index: int) -> str:
        """Build a short semantic title for a chunk."""
        if heading and heading.lower() not in ("content", ""):
            return heading[:80]
        return f"chunk_{index:03d}"

    def _infer_citability(self, source: SourceRecord) -> str:
        """Infer citability from source type and trust tier."""
        if source.trust_tier in (1, 2):
            return "directly_citable"
        if source.source_type in ("tds", "sds", "product_catalog"):
            return "directly_citable"
        if source.source_type in ("blog_post", "forum_thread"):
            return "internal_use_only"
        return "paraphrase_only"

    def _assess_quality(self, text: str, tokens: int) -> list[str]:
        """Return quality flags for a chunk."""
        flags: list[str] = []
        if tokens < self.min_tokens * 2:
            flags.append("low_density")
        # Suspect OCR: high ratio of non-ASCII characters
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii / max(len(text), 1) > 0.15:
            flags.append("ocr_suspect")
        return flags
