"""
text_utils.py — Text normalization, token estimation, and sentence utilities.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterator


# Approximate multiplier: tokens ≈ words * 1.33 for English prose
_TOKENS_PER_WORD: float = 1.33


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a text string.

    Uses a simple word-count heuristic (words * 1.33).
    Suitable for chunking budgets; not exact for billing.
    """
    if not text:
        return 0
    words = text.split()
    return max(1, int(len(words) * _TOKENS_PER_WORD))


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters to a single space and strip."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC form."""
    return unicodedata.normalize("NFC", text)


def clean_text(text: str) -> str:
    """
    Apply standard cleaning: Unicode normalization + whitespace normalization.

    Preserves line breaks so markdown heading structure is intact.
    Only collapses horizontal whitespace (spaces/tabs) within lines.
    """
    text = normalize_unicode(text)
    # Collapse horizontal whitespace within lines; preserve newlines
    text = re.sub(r"[^\S\n]+", " ", text)
    text = text.strip()
    return text


def strip_markdown_headers(text: str) -> str:
    """Remove Markdown heading markers (# ## ###) from lines."""
    return re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)


def split_sentences(text: str) -> list[str]:
    """
    Split text into sentences using simple punctuation rules.

    Not a full NLP sentence tokenizer — sufficient for chunking heuristics.
    """
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    """Split text on blank lines (paragraph boundaries)."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def heading_lines(text: str) -> list[tuple[int, str, str]]:
    """
    Extract Markdown headings from text.

    Returns list of (line_number, level_string, heading_text).
    level_string is '#', '##', etc.
    """
    results: list[tuple[int, str, str]] = []
    for i, line in enumerate(text.splitlines()):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            results.append((i, m.group(1), m.group(2).strip()))
    return results


def build_section_path(headings: list[tuple[int, str, str]], current_line: int) -> str:
    """
    Build a dot-separated section path from the heading hierarchy up to current_line.

    Returns something like '3.2.pigment_handling'.
    """
    active: dict[int, str] = {}
    for line_no, level, title in headings:
        if line_no > current_line:
            break
        depth = len(level)
        active[depth] = slugify(title)
        for d in list(active.keys()):
            if d > depth:
                del active[d]

    if not active:
        return ""
    return ".".join(active[d] for d in sorted(active.keys()))


def slugify(text: str) -> str:
    """Convert a heading string to a lowercase slug suitable for section paths."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def pipe_encode(values: list[str]) -> str:
    """
    Encode a list of strings as a pipe-delimited string for ChromaDB metadata.

    ChromaDB only accepts str/int/float/bool — lists must be pipe-encoded.
    Empty string is stored as empty string; decode returns [].
    """
    return "|".join(v for v in values if v)


def pipe_decode(value: str) -> list[str]:
    """Decode a pipe-delimited string back to a list of strings."""
    if not value:
        return []
    return [v for v in value.split("|") if v]


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text to max_chars, appending '…' if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def iter_windows(
    sentences: list[str],
    max_tokens: int,
    overlap: int = 1,
) -> Iterator[list[str]]:
    """
    Yield overlapping windows of sentences respecting a token budget.

    Useful for prose chunking with soft sentence overlap.
    """
    i = 0
    while i < len(sentences):
        window: list[str] = []
        tokens = 0
        j = i
        while j < len(sentences):
            t = estimate_tokens(sentences[j])
            if tokens + t > max_tokens and window:
                break
            window.append(sentences[j])
            tokens += t
            j += 1
        if window:
            yield window
        i = max(i + 1, j - overlap)
