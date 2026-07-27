from examples.intermediate.query_reranking import Document, rerank, retrieve_candidates, rewrite_query


DOCS = [Document("rotation", "Create a replacement API key, deploy, verify, and revoke the old key."), Document("health", "The health endpoint checks availability."), Document("billing", "Invoices are available from billing.")]


def test_query_rewriter_is_deterministic_and_keeps_original():
    variants = rewrite_query("  rotate my key  ")
    assert variants[0] == "rotate my key"
    assert len(variants) == len(set(variants))


def test_candidate_retrieval_tracks_query_variants():
    candidates = retrieve_candidates("How do I rotate an API key?", DOCS)
    rotation = next(item for item in candidates if item.document.doc_id == "rotation")
    assert rotation.source_queries


def test_reranker_returns_bounded_ordered_results():
    reranked = rerank("How do I rotate an API key?", retrieve_candidates("How do I rotate an API key?", DOCS), top_k=2)
    assert 1 <= len(reranked) <= 2
    assert all(left.score >= right.score for left, right in zip(reranked, reranked[1:]))
