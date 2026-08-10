from examples.intermediate.query_reranking import (
    Document,
    pipeline,
    recall_at_k,
    reciprocal_rank,
    rerank,
    retrieve_candidates,
    rewrite_query,
)


DOCS = [
    Document("rotation", "Create a replacement API key, deploy, verify traffic, and revoke the old key."),
    Document("health", "The health endpoint checks service availability."),
    Document("billing", "Invoices are available from the billing endpoint."),
]


def test_query_rewriter_is_bounded_deterministic_and_keeps_original():
    variants = rewrite_query("  replace a credential  ")
    assert variants[0] == "replace a credential"
    assert any("api key" in variant for variant in variants)
    assert len(variants) == len(set(variants))
    assert len(variants) <= 4


def test_candidate_retrieval_tracks_variants_and_is_bounded():
    candidates, trace = retrieve_candidates("How do I replace a credential?", DOCS, candidate_budget=2)
    rotation = next(item for item in candidates if item.document.doc_id == "rotation")

    assert rotation.source_queries
    assert trace.variants[0] == "How do I replace a credential?"
    assert trace.candidate_count <= 2


def test_reranker_returns_bounded_ordered_results():
    candidates, _ = retrieve_candidates("How do I rotate an API key?", DOCS)
    reranked = rerank("How do I rotate an API key?", candidates, top_k=2)
    assert 1 <= len(reranked) <= 2
    assert all(left.score >= right.score for left, right in zip(reranked, reranked[1:]))


def test_pipeline_trace_and_ranking_metrics_are_inspectable():
    ranking, trace = pipeline("How do I replace a credential?", DOCS, final_k=2)
    relevant = {"rotation"}

    assert trace.candidate_count >= trace.rerank_count
    assert recall_at_k(ranking, relevant, k=2) == 1.0
    assert reciprocal_rank(ranking, relevant) == 1.0
