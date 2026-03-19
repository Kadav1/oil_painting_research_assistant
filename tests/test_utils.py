"""
test_utils.py — Unit tests for utility functions.
"""

import pytest


# ---------------------------------------------------------------------------
# hash_utils
# ---------------------------------------------------------------------------

class TestHashUtils:
    def test_make_chunk_id_format(self):
        from oil_painting_rag.utils.hash_utils import make_chunk_id
        cid = make_chunk_id("SRC001", 0)
        assert cid.startswith("CHK-SRC001-")
        assert cid == "CHK-SRC001-000"

    def test_make_chunk_id_padding(self):
        from oil_painting_rag.utils.hash_utils import make_chunk_id
        assert make_chunk_id("SRC001", 7) == "CHK-SRC001-007"
        assert make_chunk_id("SRC001", 42) == "CHK-SRC001-042"
        assert make_chunk_id("SRC001", 999) == "CHK-SRC001-999"

    def test_make_trace_id_not_empty(self):
        from oil_painting_rag.utils.hash_utils import make_trace_id
        t1 = make_trace_id()
        t2 = make_trace_id()
        assert t1 != t2
        assert len(t1) > 5

    def test_content_hash_deterministic(self):
        from oil_painting_rag.utils.hash_utils import content_hash
        assert content_hash("hello") == content_hash("hello")
        assert content_hash("hello") != content_hash("world")

    def test_sha256_hex_length(self):
        from oil_painting_rag.utils.hash_utils import sha256_hex
        h = sha256_hex("test input")
        assert len(h) == 64


# ---------------------------------------------------------------------------
# text_utils
# ---------------------------------------------------------------------------

class TestTextUtils:
    def test_estimate_tokens_rough(self):
        from oil_painting_rag.utils.text_utils import estimate_tokens
        # ~4 chars per token rule-of-thumb
        n = estimate_tokens("Lead white is a basic lead carbonate.")
        assert n > 0
        assert isinstance(n, int)

    def test_pipe_encode_decode_roundtrip(self):
        from oil_painting_rag.utils.text_utils import pipe_decode, pipe_encode
        values = ["lead white", "titanium white", "zinc white"]
        encoded = pipe_encode(values)
        assert isinstance(encoded, str)
        assert "|" in encoded or len(values) == 1
        decoded = pipe_decode(encoded)
        assert decoded == values

    def test_pipe_encode_empty_list(self):
        from oil_painting_rag.utils.text_utils import pipe_decode, pipe_encode
        assert pipe_encode([]) == ""
        assert pipe_decode("") == []

    def test_pipe_encode_single_value(self):
        from oil_painting_rag.utils.text_utils import pipe_decode, pipe_encode
        assert pipe_encode(["only_one"]) == "only_one"
        assert pipe_decode("only_one") == ["only_one"]

    def test_split_sentences(self):
        from oil_painting_rag.utils.text_utils import split_sentences
        text = "Lead white is warm. Zinc white is cool. Titanium white is neutral."
        sentences = split_sentences(text)
        assert len(sentences) == 3

    def test_split_sentences_empty(self):
        from oil_painting_rag.utils.text_utils import split_sentences
        assert split_sentences("") == []


# ---------------------------------------------------------------------------
# citation_utils
# ---------------------------------------------------------------------------

class TestCitationUtils:
    def test_citation_is_complete_with_format(self):
        from oil_painting_rag.utils.citation_utils import citation_is_complete
        assert citation_is_complete("Mayer, R. (1991). The Artist's Handbook.", "Chapter 3") is True

    def test_citation_is_complete_without_format(self):
        from oil_painting_rag.utils.citation_utils import citation_is_complete
        # First arg is citation_format, second is source_title
        assert citation_is_complete("", "") is False
        assert citation_is_complete(None, None) is False
        # source_title alone is sufficient
        assert citation_is_complete("", "Chapter 3") is True

    def test_build_citation(self):
        from oil_painting_rag.utils.citation_utils import build_citation
        citation = build_citation(
            source_title="The Artist's Handbook",
            citation_format="Mayer (1991)",
        )
        assert "Mayer" in citation

    def test_format_citation_list(self):
        from oil_painting_rag.utils.citation_utils import format_citation_list
        citations = ["Mayer (1991)", "Doerner (1934)", "Mayer (1991)"]
        formatted = format_citation_list(citations)
        # Should deduplicate
        assert formatted.count("Mayer") == 1


# ---------------------------------------------------------------------------
# enum_utils
# ---------------------------------------------------------------------------

class TestEnumUtils:
    def test_approval_states_not_empty(self):
        from oil_painting_rag.utils.enum_utils import approval_states
        states = approval_states()
        assert len(states) > 0
        assert "retrieval_allowed" in states

    def test_validate_enum_valid_value(self):
        from oil_painting_rag.utils.enum_utils import is_valid_enum
        assert is_valid_enum("approval_state", "retrieval_allowed") is True

    def test_validate_enum_invalid_value(self):
        from oil_painting_rag.utils.enum_utils import is_valid_enum
        assert is_valid_enum("approval_state", "not_a_real_state") is False
