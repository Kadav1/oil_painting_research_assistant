"""
test_retrieval.py — Unit tests for retrieval components.

Tests: classifier, Reranker, DiversityFilter, CitationAssembler, PromptBuilder, Scorer.
"""

import pytest


# ---------------------------------------------------------------------------
# Query classifier
# ---------------------------------------------------------------------------

class TestClassifier:
    def test_studio_query(self):
        from oil_painting_rag.retrieval.classifier import classify_query
        result = classify_query("How do I mix lead white for underpainting?")
        assert "Studio" in result.inferred_modes or "studio" in result.inferred_modes

    def test_conservation_query(self):
        from oil_painting_rag.retrieval.classifier import classify_query
        result = classify_query("Does titanium white cause blanching or yellowing over time?")
        assert len(result.inferred_modes) >= 1

    def test_product_query(self):
        from oil_painting_rag.retrieval.classifier import classify_query
        result = classify_query("What is the pigment load in Williamsburg lead white?")
        # Should infer product comparison or studio
        assert len(result.inferred_modes) >= 1

    def test_classification_has_domains(self):
        from oil_painting_rag.retrieval.classifier import classify_query
        result = classify_query("What is the difference between PW6 and PW4 titanium white?")
        assert isinstance(result.inferred_domains, list)
        assert isinstance(result.inferred_question_types, list)


# ---------------------------------------------------------------------------
# Reranker
# ---------------------------------------------------------------------------

class TestReranker:
    def _make_chunk(self, chunk_id="CHK-001", trust_tier=2, domain="pigments", approval_state="retrieval_allowed"):
        from oil_painting_rag.models.chunk_models import ChunkRecord
        return ChunkRecord(
            chunk_id=chunk_id,
            source_id="SRC001",
            chunk_index=0,
            section_path="",
            chunk_title="Test Chunk",
            text="Lead white is a basic lead carbonate.",
            token_estimate=8,
            chunk_type="prose",
            domain=domain,
            trust_tier=trust_tier,
            approval_state=approval_state,
            source_family="pigment_reference",
            source_type="technical_handbook",
            review_status="approved",
            citability="directly_citable",
            case_specificity="broadly_applicable",
        )

    def _make_merged(self, chunk_id, score=0.5, sources=None):
        from oil_painting_rag.models.retrieval_models import MergedCandidate
        return MergedCandidate(
            chunk_id=chunk_id,
            merge_score=score,
            sources=sources or ["vector", "lexical"],
        )

    def _make_classification(self, modes=None, domains=None, qtypes=None):
        from oil_painting_rag.models.retrieval_models import QueryClassification
        return QueryClassification(
            inferred_modes=modes or ["Studio"],
            inferred_domains=domains or ["pigments"],
            inferred_question_types=qtypes or ["material_identification"],
        )

    def test_returns_sorted_results(self):
        from oil_painting_rag.retrieval.reranker import Reranker
        reranker = Reranker()
        chunks = [self._make_chunk("CHK-001"), self._make_chunk("CHK-002", trust_tier=1)]
        merged = [self._make_merged("CHK-001", 0.5), self._make_merged("CHK-002", 0.8)]
        classification = self._make_classification()

        results = reranker.rerank("lead white", chunks, merged, classification)
        assert len(results) == 2
        assert results[0]["rerank_score"] >= results[1]["rerank_score"]

    def test_higher_tier_scores_higher(self):
        from oil_painting_rag.retrieval.reranker import Reranker
        reranker = Reranker()
        chunk_tier1 = self._make_chunk("CHK-001", trust_tier=1)
        chunk_tier4 = self._make_chunk("CHK-002", trust_tier=4)
        merged = [self._make_merged("CHK-001", 0.5), self._make_merged("CHK-002", 0.5)]
        classification = self._make_classification()

        results = reranker.rerank("test query", [chunk_tier1, chunk_tier4], merged, classification)
        scores_by_id = {r["chunk_id"]: r["rerank_score"] for r in results}
        assert scores_by_id["CHK-001"] > scores_by_id["CHK-002"]

    def test_empty_chunks_returns_empty(self):
        from oil_painting_rag.retrieval.reranker import Reranker
        reranker = Reranker()
        results = reranker.rerank("test", [], [], self._make_classification())
        assert results == []


# ---------------------------------------------------------------------------
# DiversityFilter
# ---------------------------------------------------------------------------

class TestDiversityFilter:
    def _make_chunk(self, chunk_id, source_id="SRC001", trust_tier=2, duplicate_status="unique"):
        from oil_painting_rag.models.chunk_models import ChunkRecord
        return ChunkRecord(
            chunk_id=chunk_id,
            source_id=source_id,
            chunk_index=0,
            section_path="",
            chunk_title="Test",
            text="Lead white is a basic lead carbonate. " * 5,
            token_estimate=40,
            chunk_type="prose",
            domain="pigments",
            trust_tier=trust_tier,
            approval_state="retrieval_allowed",
            source_family="pigment_reference",
            source_type="technical_handbook",
            duplicate_status=duplicate_status,
        )

    def _make_reranked(self, chunk_id, score=0.8):
        return {"chunk_id": chunk_id, "rerank_score": score}

    def test_selects_top_k(self):
        from oil_painting_rag.retrieval.diversity import DiversityFilter
        df = DiversityFilter(max_chunks_per_source=5)
        chunks = [self._make_chunk(f"CHK-00{i}") for i in range(5)]
        reranked = [self._make_reranked(f"CHK-00{i}", 0.9 - i * 0.1) for i in range(5)]
        selected, excluded = df.select(reranked, chunks, top_k=3, token_budget=10000)
        assert len(selected) <= 3

    def test_enforces_source_cap(self):
        from oil_painting_rag.retrieval.diversity import DiversityFilter
        df = DiversityFilter(max_chunks_per_source=2)
        # All from same source
        chunks = [self._make_chunk(f"CHK-00{i}", source_id="SRC001") for i in range(5)]
        reranked = [self._make_reranked(f"CHK-00{i}", 0.9 - i * 0.1) for i in range(5)]
        selected, excluded = df.select(reranked, chunks, top_k=10, token_budget=10000)
        assert len(selected) <= 2

    def test_suppresses_confirmed_duplicate(self):
        from oil_painting_rag.retrieval.diversity import DiversityFilter
        df = DiversityFilter()
        chunks = [
            self._make_chunk("CHK-001"),
            self._make_chunk("CHK-002", duplicate_status="confirmed_duplicate"),
        ]
        reranked = [
            self._make_reranked("CHK-001", 0.9),
            self._make_reranked("CHK-002", 0.8),
        ]
        selected, excluded = df.select(reranked, chunks, top_k=10, token_budget=10000)
        selected_ids = {s.chunk_id for s in selected}
        assert "CHK-002" not in selected_ids

    def test_token_budget_enforced(self):
        from oil_painting_rag.retrieval.diversity import DiversityFilter
        df = DiversityFilter()
        # Each chunk has ~30 tokens ("Lead white..." * 5 → ~35 words)
        chunks = [self._make_chunk(f"CHK-00{i}") for i in range(5)]
        reranked = [self._make_reranked(f"CHK-00{i}", 0.9 - i * 0.1) for i in range(5)]
        # Tiny budget
        selected, excluded = df.select(reranked, chunks, top_k=10, token_budget=50)
        # Should select at most 1-2 chunks
        assert len(selected) <= 3


# ---------------------------------------------------------------------------
# CitationAssembler
# ---------------------------------------------------------------------------

class TestCitationAssembler:
    def _make_selected_chunk(self, chunk_id="CHK-001"):
        from oil_painting_rag.models.retrieval_models import SelectedChunk
        return SelectedChunk(
            chunk_id=chunk_id,
            source_id="SRC001",
            chunk_title="Lead White",
            text="Lead white is a basic lead carbonate.",
            trust_tier=2,
            domain="pigments",
            case_specificity="broadly_applicable",
            citability="directly_citable",
            citation_format="Mayer, R. (1991). The Artist's Handbook.",
        )

    def test_assembles_package(self):
        from oil_painting_rag.models.chunk_models import ChunkRecord
        from oil_painting_rag.models.retrieval_models import QueryClassification
        from oil_painting_rag.retrieval.citation_assembler import CitationAssembler

        assembler = CitationAssembler()
        chunks_by_id = {
            "CHK-001": ChunkRecord(
                chunk_id="CHK-001",
                source_id="SRC001",
                chunk_index=0,
                section_path="",
                chunk_title="Lead White",
                text="Lead white is a basic lead carbonate.",
                token_estimate=8,
                chunk_type="prose",
                domain="pigments",
                trust_tier=2,
                approval_state="retrieval_allowed",
                source_family="pigment_reference",
                source_type="technical_handbook",
                citation_format="Mayer (1991)",
            )
        }
        selected = [self._make_selected_chunk()]
        classification = QueryClassification(inferred_modes=["Studio"])

        package = assembler.assemble(
            package_id="PKG-001",
            query="What is lead white?",
            classification=classification,
            selected_chunks=selected,
            chunks_by_id=chunks_by_id,
            filters_applied={},
            conflict_notes=[],
            token_budget=3000,
            warnings=[],
        )
        assert package.package_id == "PKG-001"
        assert len(package.selected_chunks) == 1
        assert package.token_budget_used >= 0


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class TestScorer:
    def _make_record(self, must_not_say=None, must_include=None):
        from oil_painting_rag.models.benchmark_models import BenchmarkRecord
        return BenchmarkRecord(
            benchmark_id="BMK-PIG-001",
            category="pigments",
            question="What is titanium white?",
            difficulty="basic",
            status="approved",
            must_not_say=must_not_say or [],
            must_include=must_include or [],
        )

    def _make_answer(self, text="Titanium white (PW6) is bright and opaque."):
        from oil_painting_rag.models.retrieval_models import AnswerResult
        return AnswerResult(
            query="What is titanium white?",
            answer_text=text,
            answer_mode="Studio",
        )

    def test_no_violations_returns_empty_tags(self):
        from oil_painting_rag.evaluation.scorer import Scorer, FAILURE_MUST_NOT_SAY_VIOLATION
        scorer = Scorer()
        record = self._make_record()
        answer = self._make_answer()
        result = scorer.score_answer(record, answer)
        assert FAILURE_MUST_NOT_SAY_VIOLATION not in result.failure_tags

    def test_must_not_say_violation_detected(self):
        from oil_painting_rag.evaluation.scorer import Scorer, FAILURE_MUST_NOT_SAY_VIOLATION
        scorer = Scorer()
        record = self._make_record(must_not_say=["titanium white is always safe"])
        answer = self._make_answer(
            "Titanium white is always safe to use in any quantity."
        )
        result = scorer.score_answer(record, answer)
        assert FAILURE_MUST_NOT_SAY_VIOLATION in result.failure_tags

    def test_must_include_miss_noted(self):
        from oil_painting_rag.evaluation.scorer import Scorer
        scorer = Scorer()
        record = self._make_record(must_include=["PW6", "rutile"])
        answer = self._make_answer("Titanium white is a bright modern white.")  # missing PW6, rutile
        result = scorer.score_answer(record, answer)
        assert "MISSING" in result.evaluator_notes


# ---------------------------------------------------------------------------
# Mode router
# ---------------------------------------------------------------------------

class TestModeRouter:
    def test_single_mode(self):
        from oil_painting_rag.generation.mode_router import select_mode
        from oil_painting_rag.models.retrieval_models import QueryClassification
        cl = QueryClassification(inferred_modes=["Conservation"])
        assert select_mode(cl) == "Conservation"

    def test_no_mode_defaults_to_studio(self):
        from oil_painting_rag.generation.mode_router import select_mode
        from oil_painting_rag.models.retrieval_models import QueryClassification
        cl = QueryClassification(inferred_modes=[])
        assert select_mode(cl) == "Studio"

    def test_priority_conservation_over_studio(self):
        from oil_painting_rag.generation.mode_router import select_mode
        from oil_painting_rag.models.retrieval_models import QueryClassification
        cl = QueryClassification(inferred_modes=["Studio", "Conservation"])
        assert select_mode(cl) == "Conservation"


# ---------------------------------------------------------------------------
# PromptBuilder
# ---------------------------------------------------------------------------

class TestPromptBuilder:
    def _make_empty_context(self):
        from oil_painting_rag.models.retrieval_models import ContextPackage, QueryClassification
        return ContextPackage(
            package_id="PKG-001",
            query="test",
            query_classification=QueryClassification(),
        )

    def test_system_prompt_contains_v1_text(self):
        from oil_painting_rag.generation.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("Studio")
        assert "Oil Painting Research Assistant" in prompt
        assert "Prohibited Behavior" in prompt

    def test_mode_emphasis_appended(self):
        from oil_painting_rag.generation.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("Conservation")
        assert "Mode Emphasis" in prompt or "Tier 1" in prompt

    def test_user_prompt_contains_question(self):
        from oil_painting_rag.generation.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        context = self._make_empty_context()
        prompt = builder.build_user_prompt("What is lead white?", context)
        assert "What is lead white?" in prompt

    def test_user_prompt_no_context_notes_missing(self):
        from oil_painting_rag.generation.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        context = self._make_empty_context()
        prompt = builder.build_user_prompt("test", context)
        assert "No source material" in prompt
