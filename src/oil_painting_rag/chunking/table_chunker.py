"""
table_chunker.py — Table extraction and chunking for the Oil Painting Research Assistant.

Detects Markdown tables in normalized text, extracts them as structured data,
and creates table-type ChunkRecords.
"""

from __future__ import annotations

import re
from typing import Any, Optional

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.chunk_models import ChunkRecord
from oil_painting_rag.models.source_models import SourceRecord
from oil_painting_rag.utils.hash_utils import make_chunk_id
from oil_painting_rag.utils.text_utils import (
    build_section_path,
    estimate_tokens,
    heading_lines,
)

logger = get_logger(__name__)

# Pattern to detect Markdown table rows (lines with | separators)
_TABLE_ROW_RE = re.compile(r"^\|.+\|$")
# Pattern to detect separator rows (|---|---|)
_TABLE_SEP_RE = re.compile(r"^\|[-: |]+\|$")


class TableChunker:
    """
    Extracts and chunks Markdown tables from normalized source text.

    Each detected table becomes one table-type ChunkRecord.
    """

    def chunk_tables(
        self,
        source: SourceRecord,
        text: str,
        start_index: int = 0,
    ) -> list[ChunkRecord]:
        """
        Extract all Markdown tables from text and create ChunkRecords.

        Returns list of table ChunkRecords, or empty list if no tables found.
        """
        lines = text.splitlines()
        headings = heading_lines(text)
        tables = self._find_tables(lines)

        chunks: list[ChunkRecord] = []
        for i, (start_line, end_line, table_lines) in enumerate(tables):
            chunk_index = start_index + i
            chunk_id = make_chunk_id(source.source_id, chunk_index)
            section_path = build_section_path(headings, start_line)

            table_text = "\n".join(table_lines)
            token_est = estimate_tokens(table_text)

            # Parse headers for chunk title
            headers = self._parse_headers(table_lines)
            chunk_title = self._make_table_title(headers, source.short_title, i)

            quality_flags: list[str] = []
            if self._is_messy_table(table_lines):
                quality_flags.append("table_messy")

            chunk = ChunkRecord(
                chunk_id=chunk_id,
                source_id=source.source_id,
                chunk_index=chunk_index,
                chunk_title=chunk_title,
                section_path=section_path,
                text=table_text,
                token_estimate=token_est,
                chunk_type="table",
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
                citability="paraphrase_only",
                approval_state="not_approved",
                quality_flags=quality_flags,
                review_status="draft",
                duplicate_status="unique",
                source_family=source.source_family,
                source_type=source.source_type,
                trust_tier=source.trust_tier or 5,
                source_title=source.short_title,
                citation_format=source.citation_format,
            )
            chunks.append(chunk)

        if chunks:
            logger.info(
                "Extracted %d table chunks from source %s", len(chunks), source.source_id
            )
        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_tables(
        self,
        lines: list[str],
    ) -> list[tuple[int, int, list[str]]]:
        """
        Find all Markdown table blocks in the line list.

        Returns list of (start_line, end_line, table_lines).
        """
        results: list[tuple[int, int, list[str]]] = []
        i = 0
        while i < len(lines):
            if _TABLE_ROW_RE.match(lines[i].strip()):
                # Found a table row — scan forward to find the full table
                start = i
                table_lines: list[str] = []
                while i < len(lines) and _TABLE_ROW_RE.match(lines[i].strip()):
                    table_lines.append(lines[i])
                    i += 1
                # Only include if it has a separator row (proper Markdown table)
                if any(_TABLE_SEP_RE.match(ln.strip()) for ln in table_lines):
                    results.append((start, i - 1, table_lines))
            else:
                i += 1
        return results

    def _parse_headers(self, table_lines: list[str]) -> list[str]:
        """Extract column headers from a Markdown table."""
        if not table_lines:
            return []
        header_line = table_lines[0]
        cols = [c.strip() for c in header_line.split("|") if c.strip()]
        return cols

    def _make_table_title(
        self,
        headers: list[str],
        source_title: str,
        table_index: int,
    ) -> str:
        """Build a descriptive title for a table chunk."""
        if headers:
            preview = ", ".join(headers[:3])
            return f"Table: {preview}"
        return f"{source_title} — table {table_index + 1}"

    def _is_messy_table(self, table_lines: list[str]) -> bool:
        """Detect tables with inconsistent column counts."""
        col_counts = set()
        for ln in table_lines:
            if _TABLE_SEP_RE.match(ln.strip()):
                continue
            cols = ln.split("|")
            col_counts.add(len(cols))
        return len(col_counts) > 2  # allow header + data to differ slightly
