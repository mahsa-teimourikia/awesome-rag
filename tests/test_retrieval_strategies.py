from examples.intermediate.retrieval_strategies import BM25, Document, reciprocal_rank_fusion


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
