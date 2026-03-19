"""
answerer.py — Answer generation for the Oil Painting Research Assistant.

Responsibilities:
- Select the primary answer mode from query classification
- Build system and user prompts
- Call the configured LLM backend
- Assemble AnswerResult with citations, conflict disclosures, and labels
- Log retrieval failures when the context is empty

LLM backends supported:
  "openai"  — OpenAI-compatible chat completions API (default)
  "echo"    — Returns the user prompt verbatim; for testing without an LLM
"""

from __future__ import annotations

from typing import Any, Optional, Protocol

import oil_painting_rag.config as cfg
from oil_painting_rag.generation.mode_router import select_mode
from oil_painting_rag.generation.prompt_builder import PromptBuilder
from oil_painting_rag.logging_utils import get_logger
from oil_painting_rag.models.retrieval_models import AnswerLabel, AnswerResult, ContextPackage
from oil_painting_rag.utils.citation_utils import format_citation_list

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# LLM backend protocol
# ---------------------------------------------------------------------------

class LLMBackend(Protocol):
    """Minimal interface for an LLM text-generation backend."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the assistant's reply text."""
        ...


# ---------------------------------------------------------------------------
# Built-in backends
# ---------------------------------------------------------------------------

class OpenAIBackend:
    """
    OpenAI-compatible chat completions backend.

    Works with any server that implements the OpenAI chat completions API
    (openai.com, local models via LiteLLM, Ollama, etc.).
    """

    def __init__(
        self,
        model: str = cfg.LLM_MODEL,
        api_key: Optional[str] = cfg.LLM_API_KEY,
        base_url: Optional[str] = cfg.LLM_BASE_URL,
        max_tokens: int = cfg.LLM_MAX_TOKENS,
        temperature: float = cfg.LLM_TEMPERATURE,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import openai
            except ImportError as exc:
                raise ImportError(
                    "openai package is required for OpenAIBackend. "
                    "Install it with: pip install openai"
                ) from exc
            kwargs: dict[str, Any] = {"api_key": self.api_key or "not-set"}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""


class EchoBackend:
    """
    Echo backend for testing — returns the user prompt unchanged.

    Useful for unit tests and pipeline integration tests that do not
    require a live LLM.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str:  # noqa: ARG002
        return user_prompt


def _build_default_backend() -> LLMBackend:
    """Instantiate the backend configured by LLM_BACKEND env variable."""
    backend_name = cfg.LLM_BACKEND.lower()
    if backend_name == "echo":
        return EchoBackend()
    # Default: openai-compatible
    return OpenAIBackend()


# ---------------------------------------------------------------------------
# Answerer
# ---------------------------------------------------------------------------

class Answerer:
    """
    Orchestrates the full generation step: mode selection → prompts → LLM → AnswerResult.

    Usage::

        answerer = Answerer()
        result = answerer.answer(query="...", context=package)
    """

    def __init__(self, backend: Optional[LLMBackend] = None) -> None:
        self._backend: LLMBackend = backend or _build_default_backend()
        self._builder = PromptBuilder()

    def answer(
        self,
        query: str,
        context: ContextPackage,
    ) -> AnswerResult:
        """
        Generate an answer for the given query and context package.

        Steps:
        1. Select primary answer mode
        2. Build system + user prompts
        3. Call LLM backend
        4. Collect citations from selected chunks
        5. Collect conflict disclosures
        6. Infer answer labels from chunk metadata
        7. Return AnswerResult
        """
        # Step 1: mode
        mode = select_mode(context.query_classification)
        logger.debug("Answer mode selected: %s", mode)

        # Step 2: prompts
        system_prompt = self._builder.build_system_prompt(mode)
        user_prompt = self._builder.build_user_prompt(query, context)

        # Step 3: LLM call
        if not context.selected_chunks:
            logger.warning(
                "Empty context for query %r — calling LLM with no source material",
                query[:80],
            )
        try:
            answer_text = self._backend.complete(system_prompt, user_prompt)
        except Exception as exc:
            logger.error("LLM backend error: %s", exc)
            answer_text = (
                "An error occurred while generating the answer. "
                "Please try again or check the backend configuration."
            )

        # Step 4: citations
        citation_strings = [
            sc.citation_format
            for sc in context.selected_chunks
            if sc.citation_format and sc.citability not in ("internal_use_only", "not_citable")
        ]
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_citations: list[str] = []
        for c in citation_strings:
            if c not in seen:
                seen.add(c)
                unique_citations.append(c)

        # Step 5: conflict disclosures
        conflict_disclosures: list[str] = []
        for note in context.conflict_notes:
            if note.requires_disclosure:
                if note.summary:
                    conflict_disclosures.append(note.summary)
                else:
                    conflict_disclosures.append(
                        f"Conflicting sources on topic: {note.topic}"
                    )

        # Step 6: infer answer labels from chunk metadata
        answer_labels = self._infer_labels(context)

        # Step 7: uncertainty notes
        uncertainty_notes: list[str] = []
        has_uncertain = any(lb.label == "uncertain" for lb in answer_labels)
        has_mixed = any(lb.label == "mixed_evidence" for lb in answer_labels)
        if not context.selected_chunks:
            uncertainty_notes.append(
                "No source material was retrieved — answer is not grounded."
            )
        if has_uncertain:
            uncertainty_notes.append(
                "Evidence is limited or absent for part of this answer."
            )
        if has_mixed:
            uncertainty_notes.append(
                "Sources disagree on one or more points — see conflict disclosures."
            )

        return AnswerResult(
            query=query,
            answer_text=answer_text,
            answer_mode=mode,
            answer_labels=answer_labels,
            citations=unique_citations,
            conflict_disclosures=conflict_disclosures,
            uncertainty_notes=uncertainty_notes,
            context_package_id=context.package_id,
            trace_id=context.retrieval_trace_id,
        )

    # ------------------------------------------------------------------
    # Label inference
    # ------------------------------------------------------------------

    def _infer_labels(self, context: ContextPackage) -> list[AnswerLabel]:
        """
        Infer answer labels from the selected chunk metadata.

        Logic:
        - conflict_notes present → mixed_evidence
        - no chunks → uncertain
        - chunk has case_specificity == "case_specific" → case_specific
        - chunk from trust_tier 3 (manufacturer) → product_specific
        - chunk from trust_tier 4 (historical) → historically_documented
        - if only tier-1/2 chunks with no conflicts → well_established
        - chunk from trust_tier 5 (teaching) → interpretive
        """
        if not context.selected_chunks:
            return [
                AnswerLabel(
                    label="uncertain",
                    scope_level="unknown",
                    display_phrase="uncertain — limited evidence available",
                )
            ]

        labels: list[AnswerLabel] = []

        if context.conflict_notes and any(n.requires_disclosure for n in context.conflict_notes):
            labels.append(AnswerLabel(
                label="mixed_evidence",
                scope_level="conflicted",
                display_phrase="sources disagree on this point",
            ))

        tiers = {sc.trust_tier for sc in context.selected_chunks}
        case_specificities = {sc.case_specificity for sc in context.selected_chunks}

        if "case_specific" in case_specificities:
            labels.append(AnswerLabel(
                label="case_specific",
                scope_level="case",
                display_phrase="this was found in a specific case",
            ))

        if 3 in tiers:
            labels.append(AnswerLabel(
                label="product_specific",
                scope_level="product",
                display_phrase="per manufacturer technical data",
            ))

        if 4 in tiers:
            labels.append(AnswerLabel(
                label="historically_documented",
                scope_level="historical",
                display_phrase="documented in historical sources",
            ))

        if 5 in tiers:
            labels.append(AnswerLabel(
                label="interpretive",
                scope_level="judgment",
                display_phrase="this is a widely held teaching convention",
            ))

        # Well-established: only tier 1/2, no conflicts, no case_specific, no mixed
        high_trust_only = tiers.issubset({1, 2})
        no_conflicts = not any(n.requires_disclosure for n in context.conflict_notes)
        no_case_specific = "case_specific" not in case_specificities
        if high_trust_only and no_conflicts and no_case_specific and not labels:
            labels.append(AnswerLabel(
                label="well_established",
                scope_level="general",
                display_phrase="well-documented in conservation literature",
            ))

        return labels if labels else [
            AnswerLabel(
                label="likely_but_context_dependent",
                scope_level="conditional",
                display_phrase="likely, but depends on context",
            )
        ]
