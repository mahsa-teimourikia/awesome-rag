from examples.intermediate.research_synthesis import Document, make_claims, research_queries, retrieve_unique


DOCS = [Document("a", "Hybrid retrieval preserves lexical and dense signals."), Document("b", "Reranking improves relevance at additional latency."), Document("c", "Reranking can increase operational cost.")]


def test_research_queries_include_multiple_framings():
    queries = research_queries("How should retrieval be combined?")
    assert len(queries) == 3
    assert "limitations" in queries[-1]


def test_multi_query_retrieval_deduplicates_sources():
    evidence = retrieve_unique("How should retrieval be combined?", DOCS)
    assert len({doc.doc_id for doc in evidence}) == len(evidence)


def test_claims_keep_source_ids():
    claims = make_claims("How should retrieval be combined?", DOCS)
    assert claims
    assert all(claim.source_ids for claim in claims)
