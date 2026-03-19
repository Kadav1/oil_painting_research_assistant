"""
prompt_builder.py — Prompt construction for the Oil Painting Research Assistant.

Builds:
  - The system prompt (canonical v1 text + optional mode emphasis note)
  - The user prompt (query + formatted context chunks + conflict disclosures)

The system prompt text is canonical and must not be modified at runtime.
Mode-specific guidance is appended as an addendum, not as a modification.
"""

from __future__ import annotations

from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.retrieval_models import ContextPackage, SelectedChunk
from oil_painting_rag.generation.mode_router import mode_emphasis_note

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Canonical v1 system prompt (from docs/foundation/system_prompt_v1.md §6)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_V1 = """\
You are the Oil Painting Research Assistant.

Your role is to answer questions about oil painting using a disciplined retrieval-based method grounded in curated source material.

Your knowledge base includes:
- museum conservation and technical bulletins
- pigment reference sources
- manufacturer technical and product data
- color-theory references
- art-history and atelier sources
- scientific papers where relevant

Your job is not to sound authoritative.
Your job is to be accurate, source-aware, and useful.

## Core Behavior

When answering, you must:

1. Prefer higher-trust sources over lower-trust sources.
2. Distinguish clearly between:
   - conservation evidence
   - general technical reference
   - product-specific information
   - historical documentation
   - teaching or interpretive explanation
3. Avoid flattening case studies into universal rules.
4. Avoid treating brand-specific product behavior as a universal material law.
5. Say explicitly when evidence is mixed, limited, or context-dependent.
6. Never invent pigment codes, dates, authors, materials, or historical claims.
7. Preserve uncertainty where appropriate instead of pretending certainty.
8. Be practically useful: explain what the information means for a painter, researcher, or conservator-level reader.
9. Do not give invasive restoration instructions as casual advice.
10. When a question is product-specific, prioritize product data and clearly label it as modern brand information.
11. When a question is historical, prioritize conservation and historical sources over modern teaching advice.
12. When a question is about color, explain in painterly terms while preserving technical clarity.

## Answer Structure

When possible, organize answers in this order:

A. Direct answer
B. Why it works this way
C. What kind of source supports this
D. Limits / uncertainty
E. Practical takeaway

## Modes

You may implicitly shift emphasis depending on the question:

- Studio Mode: practical handling and painting decisions
- Conservation Mode: degradation, risk, archival concerns
- Art History Mode: historical plausibility and documented practice
- Color Analysis Mode: hue, value, chroma, mixture behavior
- Product Comparison Mode: compare modern paints and brands

## Source Handling Rules

If evidence comes from a case study:
- say that it is observed in a specific case
- do not automatically generalize it

If evidence comes from a manufacturer:
- label it as product-specific
- do not confuse it with universal chemistry

If evidence comes from teaching or atelier material:
- treat it as interpretive unless corroborated

## Prohibited Behavior

Do not:
- hallucinate citations
- invent technical certainty
- collapse distinct materials into one
- confuse pigment identity with product marketing names
- give definitive historical claims without source support
- overstate conservation advice beyond the evidence

## Tone

Use clear, precise, grounded language.
Be technical when needed, but never vague for the sake of sounding intelligent.
Do not use inflated language.
Do not dramatize uncertainty; state it cleanly.

## Final Goal

Your goal is to produce answers that are:
- accurate
- well-scoped
- source-aware
- practically useful
- explicit about uncertainty\
"""


class PromptBuilder:
    """
    Builds system and user prompts from a ContextPackage.

    The system prompt is the canonical v1 text with an optional mode emphasis
    addendum. The user prompt wraps the query in a structured context block
    containing formatted chunks and any conflict disclosures.
    """

    def build_system_prompt(self, mode: str) -> str:
        """
        Return the canonical v1 system prompt, optionally appended with
        a mode-specific emphasis note.
        """
        emphasis = mode_emphasis_note(mode)
        if emphasis:
            return _SYSTEM_PROMPT_V1 + f"\n\n## Current Mode Emphasis\n\n{emphasis}"
        return _SYSTEM_PROMPT_V1

    def build_user_prompt(
        self,
        query: str,
        context: ContextPackage,
    ) -> str:
        """
        Build the user-facing prompt from the query and assembled context.

        Structure:
        1. CONTEXT block — formatted source chunks with citations
        2. CONFLICT DISCLOSURES (if any)
        3. QUESTION
        """
        parts: list[str] = []

        # --- Context chunks ---
        if context.selected_chunks:
            parts.append("## Context\n")
            for i, chunk in enumerate(context.selected_chunks, 1):
                parts.append(self._format_chunk(i, chunk))
        else:
            parts.append(
                "## Context\n\n"
                "[No source material was retrieved for this query. "
                "Answer only what you can ground in the above general guidance. "
                "Do not invent facts.]\n"
            )

        # --- Conflict disclosures ---
        disclosures: list[str] = []
        for note in context.conflict_notes:
            if note.requires_disclosure and note.summary:
                disclosures.append(f"- {note.summary}")
            elif note.requires_disclosure:
                disclosures.append(
                    f"- Sources conflict on topic: {note.topic}. "
                    "Present both positions and disclose the disagreement."
                )
        if disclosures:
            parts.append("## Conflict Disclosures\n")
            parts.append(
                "The following conflicts exist in the retrieved evidence. "
                "You must disclose them in your answer:\n"
            )
            parts.extend(disclosures)
            parts.append("")

        # --- Retrieval notes (non-empty context warnings) ---
        notes = [n for n in context.retrieval_notes if "empty" in n.lower() or "no chunks" in n.lower()]
        if notes:
            parts.append("## Retrieval Notice\n")
            for note in notes:
                parts.append(f"- {note}")
            parts.append("")

        # --- Question ---
        parts.append(f"## Question\n\n{query}")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _format_chunk(self, index: int, chunk: SelectedChunk) -> str:
        """Format a single context chunk as a numbered source block."""
        lines: list[str] = []
        lines.append(f"### Source {index}: {chunk.chunk_title}")

        # Trust tier label
        tier_label = self._tier_label(chunk.trust_tier)
        lines.append(f"*{tier_label} | Domain: {chunk.domain}*")

        if chunk.citation_format:
            lines.append(f"*Citation: {chunk.citation_format}*")

        lines.append("")
        lines.append(chunk.text.strip())

        # Case specificity warning
        if chunk.case_specificity == "case_specific":
            lines.append(
                "\n> *Note: This evidence is case-specific — "
                "do not generalize without additional corroboration.*"
            )

        # Citability warning
        if chunk.citability in ("internal_use_only", "not_citable"):
            lines.append(
                "\n> *Note: This source is for internal research use only — "
                "do not cite it directly in answers to end users.*"
            )

        lines.append("")
        return "\n".join(lines)

    def _tier_label(self, tier: int) -> str:
        """Return a human-readable tier label."""
        labels = {
            1: "Tier 1 — Museum Conservation",
            2: "Tier 2 — Pigment Reference",
            3: "Tier 3 — Manufacturer",
            4: "Tier 4 — Historical Practice",
            5: "Tier 5 — Color Theory / Teaching",
        }
        return labels.get(tier, f"Tier {tier}")
