from examples.intermediate.evaluation import EvalCase, evaluate, precision_at_k, recall_at_k, reciprocal_rank


def test_retrieval_metrics():
    relevant = {"a", "b"}
    assert recall_at_k(["a", "x", "b"], relevant, 3) == 1.0
    assert precision_at_k(["a", "x"], relevant, 2) == 0.5
    assert reciprocal_rank(["x", "b"], relevant) == 0.5


def test_evaluate_averages_cases():
    cases = [EvalCase("one", frozenset({"a"})), EvalCase("two", frozenset({"b"}))]
    result = evaluate({"one": ["a"], "two": ["x", "b"]}, cases, k=2)
    assert result["recall@k"] == 1.0
    assert result["mrr"] == 0.75


def test_missing_retrieval_is_a_failure_for_answerable_case():
    case = EvalCase("missing", frozenset({"expected"}))
    assert evaluate({}, [case])["recall@k"] == 0.0
