from examples.intermediate.research_synthesis import (
    Document,
    citation_coverage,
    make_claims,
    research_queries,
    retrieve_unique,
    synthesis_outline,
    trace_evidence,
)


DOCS = [
    Document("a", "Hybrid retrieval preserves lexical and dense signals."),
    Document("b", "Reranking improves relevance at additional latency."),
    Document("c", "Reranking can increase operational cost and risk timeout failures."),
]


def test_research_queries_include_multiple_framings():
    queries = research_queries("How should retrieval be combined?")
    assert len(queries) == 4
    assert "limitations" in queries[2]
    assert "trade-offs" in queries[-1]


def test_multi_query_retrieval_deduplicates_sources_and_traces_them():
    evidence = retrieve_unique("How should retrieval be combined?", DOCS)
    trace = trace_evidence("How should retrieval be combined?", DOCS)
    assert len({doc.doc_id for doc in evidence}) == len(evidence)
    assert set(trace.source_ids) == {doc.doc_id for doc in evidence}


def test_claims_keep_sources_and_separate_limitations():
    claims = make_claims("How should retrieval be combined?", DOCS)
    outline = synthesis_outline(claims)
    assert claims and all(claim.source_ids for claim in claims)
    assert outline["limitation"]
    assert citation_coverage(claims) == 1.0
