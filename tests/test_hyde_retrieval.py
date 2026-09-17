from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "curriculum" / "advanced" / "07-hyde-retrieval" / "lab.py"
SPEC = spec_from_file_location("hyde_lab", MODULE_PATH)
assert SPEC and SPEC.loader
hyde_lab = module_from_spec(SPEC)
sys.modules[SPEC.name] = hyde_lab
SPEC.loader.exec_module(hyde_lab)


def test_mechanism_fixture_closes_the_transparent_semantic_gap() -> None:
    query = "Why does the app log me out overnight?"
    original = hyde_lab.retrieve(
        query,
        strategy="original",
        top_k=1,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )
    transformed = hyde_lab.retrieve(
        query,
        strategy="hyde",
        top_k=1,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )

    assert original.evidence_ids != ("auth-token-lifecycle",)
    assert transformed.evidence_ids == ("auth-token-lifecycle",)


def test_dense_index_uses_query_and_document_representations() -> None:
    documents = tuple(
        document
        for document in hyde_lab.CORPUS
        if document.doc_id in {"application-logging", "auth-token-lifecycle"}
    )

    def semantic_encoder(texts, representation):
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "refresh token" in lowered or "identity-provider" in lowered:
                vectors.append((1.0, 0.0))
            elif "logged out" in lowered and representation == "query":
                vectors.append((0.0, 1.0))
            elif "logging" in lowered or "overnight" in lowered:
                vectors.append((0.0, 1.0))
            else:
                vectors.append((0.5, 0.5))
        return vectors

    index = hyde_lab.DenseIndex(documents, encoder=semantic_encoder)
    original = hyde_lab.retrieve(
        "Why does the app log me out overnight?",
        strategy="original",
        top_k=1,
        index=index,
    )
    transformed = hyde_lab.retrieve(
        "Why does the app log me out overnight?",
        strategy="hyde",
        top_k=1,
        index=index,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )

    assert original.index_backend == "dense"
    assert original.evidence_ids == ("application-logging",)
    assert transformed.evidence_ids == ("auth-token-lifecycle",)


def test_evaluation_dataset_has_representative_three_case_slices() -> None:
    counts = {}
    for case in hyde_lab.EVALUATION_CASES:
        counts[case.query_type] = counts.get(case.query_type, 0) + 1

    assert len(hyde_lab.EVALUATION_CASES) == 36
    assert len(counts) == 12
    assert set(counts.values()) == {3}
    assert {"no_answer", "adversarial_query", "ambiguous_entity"} <= set(counts)


def test_no_answer_recall_is_undefined_and_excluded_from_aggregation() -> None:
    assert hyde_lab.recall_at_k(("auth-token-lifecycle",), frozenset()) is None
    rows = hyde_lab.evaluate("original", top_k=1)
    report = hyde_lab.summarize(rows)

    assert report["evaluated_cases"] == 36
    assert report["defined_recall_cases"] == 30
    assert report["no_answer_accuracy"] is not None


def test_authorization_filters_tenant_classification_and_status_before_retrieval() -> None:
    allowed = hyde_lab.authorized_documents(hyde_lab.CORPUS, hyde_lab.DEFAULT_ACCESS)
    allowed_ids = {document.doc_id for document in allowed}

    assert "tenant-b-auth-match" not in allowed_ids
    assert "restricted-auth-match" not in allowed_ids
    assert "retired-auth-match" not in allowed_ids

    trace = hyde_lab.retrieve(
        "Why does the app log me out overnight?",
        strategy="hyde_plus_original",
        top_k=50,
        hypothesis_count=2,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )
    assert trace.unauthorized_candidate_count == 0
    assert not {
        "tenant-b-auth-match",
        "restricted-auth-match",
        "retired-auth-match",
    } & set(trace.evidence_ids)


def test_retrieve_rejects_a_prebuilt_index_with_forbidden_documents() -> None:
    unsafe = hyde_lab.TfidfIndex(hyde_lab.CORPUS)

    with pytest.raises(ValueError, match="outside the access scope"):
        hyde_lab.retrieve("OIDC recovery", index=unsafe)


def test_hypotheses_never_enter_the_evidence_ledger() -> None:
    trace = hyde_lab.retrieve(
        "Why is my cloud bill suddenly higher?",
        strategy="hyde_plus_original",
        top_k=5,
        hypothesis_count=2,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )
    real_ids = {document.doc_id for document in hyde_lab.CORPUS}

    assert trace.hypotheses
    assert set(trace.evidence_ids) <= real_ids
    assert not set(trace.hypotheses) & set(trace.evidence_ids)


def test_router_is_evaluated_separately_and_protects_high_risk_queries() -> None:
    report = hyde_lab.summarize_router(hyde_lab.evaluate_router())

    assert report["evaluated_routes"] == 36
    assert report["route_accuracy"] >= 0.9
    assert report["high_risk_query_to_hyde_rate"] == 0.0
    assert report["hyde_false_positive_rate"] == 0.0


def test_conditional_policy_uses_less_generation_and_retrieval_work() -> None:
    universal = hyde_lab.summarize(
        hyde_lab.evaluate("hyde_plus_original", top_k=1, hypothesis_count=3)
    )
    conditional = hyde_lab.summarize(
        hyde_lab.evaluate("conditional", top_k=1, hypothesis_count=3)
    )

    assert conditional["generation_call_proxy"] < universal["generation_call_proxy"]
    assert conditional["retrieval_legs"] < universal["retrieval_legs"]
    assert conditional["unauthorized_candidate_documents"] == 0


def test_original_plus_hyde_reports_candidate_fusion_and_reranking_work() -> None:
    trace = hyde_lab.retrieve(
        "Why does the app log me out overnight?",
        strategy="hyde_plus_original",
        top_k=3,
        hypothesis_count=3,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )

    assert trace.generator_call_proxy == 3
    assert trace.retrieval_legs == 4
    assert trace.fusion_operations == 1
    assert trace.reranked_candidates >= len(trace.results)


def test_multi_hypothesis_diversity_measures_duplicate_perspectives() -> None:
    index = hyde_lab.build_index()
    hypotheses = (
        "An identity policy explains refresh token expiry.",
        "An identity policy explains refresh token expiry.",
        "A session lifecycle guide covers reauthentication after inactivity.",
    )
    report = hyde_lab.analyze_hypothesis_diversity(hypotheses, index=index)

    assert report.hypothesis_count == 3
    assert report.unique_hypothesis_count == 2
    assert 0.0 <= report.mean_lexical_overlap <= 1.0
    assert 0.0 <= report.mean_retrieval_overlap <= 1.0


def test_zx47_drift_is_a_measured_baseline_regression() -> None:
    case = tuple(
        case for case in hyde_lab.MECHANISM_CASES if case.case_id == "mechanism-zx47"
    )
    original = hyde_lab.evaluate(
        "original",
        cases=case,
        top_k=1,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )
    drifted = hyde_lab.evaluate(
        "hyde",
        cases=case,
        top_k=1,
        generator=hyde_lab.generate_mechanism_hypotheses,
    )
    report = hyde_lab.drift_metrics(original, drifted)

    assert original[0].retrieved_ids == ("zx-47-controller",)
    assert drifted[0].retrieved_ids == ("pharma-safety",)
    assert report["hypothesis_drift_rate"] == 1.0
    assert report["baseline_regression_rate"] == 1.0
