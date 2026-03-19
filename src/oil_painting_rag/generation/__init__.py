"""generation — Answer generation pipeline for the Oil Painting Research Assistant."""

from oil_painting_rag.generation.answerer import Answerer, EchoBackend, OpenAIBackend
from oil_painting_rag.generation.mode_router import select_mode, ALL_MODES
from oil_painting_rag.generation.prompt_builder import PromptBuilder

__all__ = [
    "Answerer",
    "EchoBackend",
    "OpenAIBackend",
    "select_mode",
    "ALL_MODES",
    "PromptBuilder",
]
