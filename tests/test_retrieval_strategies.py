from examples.intermediate.retrieval_strategies import (
    BM25,
    AttributedDocument,
    Document,
    filter_documents,
    hybrid_retrieve,
    ranking_metrics,
    reciprocal_rank_fusion,
    static_dense_ranking,
    weighted_reciprocal_rank_fusion,
)


DOCS = [Document("auth", "API keys use the Authorization header."), Document("errors", "Error E401 means unauthorized."), Document("billing", "Invoices are available from billing.")]


def test_bm25_rewards_matching_terms():
    results = BM25(DOCS).search("E401 unauthorized")
    assert results[0][0].doc_id == "errors"
    assert results[0][1] > 0


def test_reciprocal_rank_fusion_rewards_consensus():
    result = reciprocal_rank_fusion([DOCS[0], DOCS[1]], [DOCS[1], DOCS[0]])
    assert result[0][0].doc_id in {"auth", "errors"}
    assert result[0][1] == result[1][1]


def test_fusion_deduplicates_documents():
    result = reciprocal_rank_fusion([DOCS[0], DOCS[1]], [DOCS[0], DOCS[2]])
    assert len(result) == 3
    assert {doc.doc_id for doc, _ in result} == {"auth", "errors", "billing"}


def test_filters_apply_before_dense_or_lexical_candidates_are_fused():
    docs = [
        AttributedDocument("acme", "Error E401 means unauthorized.", {"tenant": "acme"}),
        AttributedDocument("globex", "Error E401 means unauthorized.", {"tenant": "globex"}),
    ]
    result, trace = hybrid_retrieve(
        "E401 unauthorized",
        docs,
        {"acme": 0.7, "globex": 0.99},
        filters={"tenant": "acme"},
    )
    assert [document.doc_id for document, _ in result] == ["acme"]
    assert trace.dense_ids == ("acme",)
    assert "globex" not in trace.fused_ids


def test_weighted_fusion_and_dense_adapter_are_explicit_and_deterministic():
    dense = static_dense_ranking(DOCS, {"billing": 0.9, "errors": 0.2})
    result = weighted_reciprocal_rank_fusion([(dense, 2.0), ([DOCS[1]], 1.0)])
    assert dense[0].doc_id == "billing"
    assert result[0][0].doc_id == "errors"


def test_ranking_metrics_are_computed_from_labelled_retrieval_results():
    metrics = ranking_metrics([[DOCS[1], DOCS[0]], [DOCS[2]]], [{"errors"}, {"billing"}])
    assert metrics.recall_at_k == 1.0
    assert metrics.mean_reciprocal_rank == 1.0
