from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from examples.beginner.first_local_rag import (
    EvaluationCase,
    answer,
    audit_corpus,
    build_context,
    build_context_pack,
    evaluate_baseline,
    load_chunks,
    retrieve,
    retrieve_bm25,
    retrieve_with_trace,
    run_local_rag,
    retrieve_authorized,
    summarize_retrieval_metrics,
)


ROOT = Path(__file__).parents[1]


def test_fixture_loads_with_source_ids():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    assert len(chunks) >= 5
    assert all(chunk.chunk_id and chunk.source for chunk in chunks)


def test_retrieval_returns_relevant_evidence():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    results = retrieve("What is an abstention?", chunks)
    assert results
    assert "abstention" in results[0][0].text.lower()


def test_answer_abstains_without_evidence():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    assert answer("What is the capital of France?", chunks).startswith("I don't have enough evidence")


def test_trace_makes_lexical_evidence_and_context_inspectable():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    hits = retrieve_with_trace("Who may restart production services?", chunks)
    assert hits[0].rank == 1
    assert "restart" in hits[0].matched_terms
    context = build_context(hits, max_characters=400)
    assert hits[0].chunk.chunk_id in context
    assert hits[0].chunk.source in context


def test_golden_set_separates_retrieval_and_abstention_results():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    report = evaluate_baseline([
        EvaluationCase("Who may restart production services?", ("harborline-support-7",)),
        EvaluationCase("What is the capital of France?", (), should_abstain=True),
    ], chunks)
    assert report[0]["retrieval_hit"]
    assert report[1]["abstention_correct"]


def test_local_pipeline_keeps_decision_context_and_citations_together():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = run_local_rag("Who may restart production services?", chunks, max_characters=300)
    assert result.decision == "answer"
    assert result.hits
    assert result.context
    assert result.citations
    assert all(hit.chunk.chunk_id in result.context for hit in result.hits if hit.chunk.chunk_id in result.context)


def test_local_pipeline_abstains_without_evidence_and_reports_policy():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = run_local_rag("What is the capital of France?", chunks, min_score=0.20)
    assert result.decision == "abstain"
    assert not result.citations
    assert result.retrieval_threshold == 0.20


def test_corpus_audit_context_pack_and_bm25_are_inspectable():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    audit = audit_corpus(chunks)
    hits = retrieve_bm25("Who may restart production services?", chunks)
    pack = build_context_pack(hits, max_characters=260)
    assert audit.ready
    assert audit.document_count >= 2
    assert hits and hits[0].rank == 1
    assert "restart" in hits[0].matched_terms
    assert pack.retained_ids and pack.citations


def test_authorization_precedes_ranking_and_context_keeps_provenance():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    hits = retrieve_authorized(
        "Who may restart production services?",
        chunks,
        allowed_sources={"harborline-support.md"},
    )
    pack = build_context_pack(hits, max_characters=250)
    assert hits
    assert all(hit.chunk.source == "harborline-support.md" for hit in hits)
    assert pack.retained_ids
    assert all(identifier in pack.text for identifier in pack.retained_ids)
    assert pack.citations


def test_golden_set_metrics_are_retrieval_metrics_not_answer_claims():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    report = evaluate_baseline([
        EvaluationCase("Who may restart production services?", ("harborline-support-7",)),
        EvaluationCase("What is the capital of France?", (), should_abstain=True),
    ], chunks)
    metrics = summarize_retrieval_metrics(report)
    assert metrics.recall_at_k == 1.0
    assert 0 < metrics.precision_at_k <= 1.0
    assert metrics.mean_reciprocal_rank > 0
    assert metrics.abstention_accuracy == 1.0


def test_bm25_trace_keeps_chunk_identity_and_query_matches_visible():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    hits = retrieve_bm25("Who may restart production services?", chunks)
    assert hits
    assert hits[0].rank == 1
    assert "restart" in hits[0].matched_terms
    assert hits[0].chunk.chunk_id
