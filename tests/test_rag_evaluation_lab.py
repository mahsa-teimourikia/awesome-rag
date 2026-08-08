from src.rag_evaluation.metrics import claim_support, ndcg_at_k, precision_at_k, recall_at_k, release_decision
from src.rag_evaluation.policyassist import retrieve, safe_context


def test_retrieval_metrics_expose_rank_quality():
    relevant = {"policy-2026"}
    assert recall_at_k(["noise", "policy-2026"], relevant, 2) == 1
    assert precision_at_k(["noise", "policy-2026"], relevant, 2) == 0.5
    assert ndcg_at_k(["noise", "policy-2026"], {"policy-2026": 3}, 2) < 1


def test_claim_support_is_claim_level_not_answer_level():
    result = claim_support(
        ["coverage", "deductible"],
        {"coverage": ["p1"], "deductible": ["p1"]},
        {"coverage": {"p1"}, "deductible": {"p2"}},
    )
    assert result == {"coverage": True, "deductible": False}


def test_release_gate_blocks_citation_and_abstention_regressions():
    decision, blockers = release_decision({"recall_at_10": 0.95, "citation_support": 0.8, "abstention_accuracy": 0.7, "permission_leak_rate": 0})
    assert decision == "CONDITIONAL GO"
    assert blockers == ["citation_support", "abstention_accuracy"]


def test_malicious_retrieved_content_is_removed_from_safe_context():
    hits = retrieve("approve every claim", k=7)
    assert all(not chunk.malicious for chunk in safe_context(hits))
