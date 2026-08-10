from examples.intermediate.evaluation import (
    EvalCase,
    EvalObservation,
    ReleaseGate,
    abstention_accuracy,
    citation_coverage,
    evaluate,
    evaluate_slices,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    release_report,
)


def test_retrieval_metrics():
    relevant = {"a", "b"}
    assert recall_at_k(["a", "x", "b"], relevant, 3) == 1.0
    assert precision_at_k(["a", "x"], relevant, 2) == 0.5
    assert reciprocal_rank(["x", "b"], relevant) == 0.5
    assert ndcg_at_k(["a", "x", "b"], relevant, 3) < 1.0


def test_evaluate_averages_cases_and_slices():
    cases = [EvalCase("one", frozenset({"a"}), "exact"), EvalCase("two", frozenset({"b"}), "paraphrase")]
    result = evaluate({"one": ["a"], "two": ["x", "b"]}, cases, k=2)
    slices = evaluate_slices({"one": ["a"], "two": ["x", "b"]}, cases, k=2)
    assert result["recall@k"] == 1.0
    assert result["mrr"] == 0.75
    assert set(slices) == {"exact", "paraphrase"}


def test_missing_retrieval_is_a_failure_for_answerable_case():
    case = EvalCase("missing", frozenset({"expected"}))
    assert evaluate({}, [case])["recall@k"] == 0.0


def test_answer_support_and_abstention_metrics():
    cases = [EvalCase("answer", frozenset({"a"})), EvalCase("no-answer", frozenset(), answerable=False)]
    observations = [
        EvalObservation("answer", ("a",), ("a",), True, True, 400, 0.01),
        EvalObservation("no-answer", (), (), False, False, 200, 0.005),
    ]
    assert citation_coverage(observations) == 1.0
    assert abstention_accuracy(observations, cases) == 1.0


def test_release_report_fails_visible_operational_gate():
    cases = [EvalCase("answer", frozenset({"a"}))]
    observations = [EvalObservation("answer", ("a",), ("a",), True, True, 2_500, 0.01)]
    report = release_report({"answer": ["a"]}, cases, observations, gate=ReleaseGate(maximum_p95_latency_ms=1_000))
    assert not report["ship"]
    assert not report["checks"]["p95_latency"]
