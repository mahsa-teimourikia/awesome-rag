from src.adaptive_rag.router import adaptive_answer, choose_k, classify_query


def test_router_distinguishes_general_private_and_multistep_queries():
    assert classify_query("What is HTTP?").strategy == "no_retrieval"
    assert classify_query("What is our current parental-leave policy?").strategy == "single_rag"
    assert classify_query("Compare our 2024 and 2026 parental-leave policies").strategy == "iterative_rag"


def test_adaptive_depth_increases_for_comparative_questions():
    assert choose_k("What is the policy limit?") == 2
    assert choose_k("Compare all policy sections and appendix") == 10


def test_adaptive_loop_stops_when_evidence_is_sufficient():
    output = adaptive_answer("What is our current policy?", lambda query, k: ["authoritative policy"])
    assert output["status"] == "answer_grounded"
    assert output["queries"] == ["What is our current policy?"]


def test_adaptive_loop_abstains_after_its_budget():
    output = adaptive_answer("Compare our 2024 and 2026 policy changed", lambda query, k: ["stale excerpt"])
    assert output["status"] == "abstain_or_escalate"
    assert len(output["queries"]) <= output["route"].max_steps
