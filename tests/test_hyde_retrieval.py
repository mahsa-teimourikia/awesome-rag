from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "curriculum" / "advanced" / "07-hyde-retrieval" / "lab.py"
SPEC = spec_from_file_location("hyde_lab", MODULE_PATH)
assert SPEC and SPEC.loader
hyde_lab = module_from_spec(SPEC)
sys.modules[SPEC.name] = hyde_lab
SPEC.loader.exec_module(hyde_lab)


def test_hyde_closes_the_semantic_gap() -> None:
    query = "Why does the app log me out overnight?"
    original = hyde_lab.retrieve(query, strategy="original", top_k=1)
    transformed = hyde_lab.retrieve(query, strategy="hyde", top_k=1)

    assert original.evidence_ids != ("auth-token-lifecycle",)
    assert transformed.evidence_ids == ("auth-token-lifecycle",)


def test_conditional_route_preserves_exact_identifier() -> None:
    trace = hyde_lab.retrieve("What is ZX-47?", strategy="conditional", top_k=1)

    assert trace.strategy == "original"
    assert trace.evidence_ids == ("zx-47-controller",)
    assert trace.hypotheses == ()


def test_hypotheses_never_enter_evidence_ledger() -> None:
    trace = hyde_lab.retrieve(
        "Why is my cloud bill suddenly higher?",
        strategy="hyde_plus_original",
        top_k=5,
        hypothesis_count=2,
    )
    real_ids = {document.doc_id for document in hyde_lab.CORPUS}

    assert trace.hypotheses
    assert set(trace.evidence_ids) <= real_ids
    assert not set(trace.hypotheses) & set(trace.evidence_ids)


def test_authorization_runs_before_hyde_retrieval() -> None:
    trace = hyde_lab.retrieve(
        "Why does the app log me out overnight?",
        strategy="hyde_plus_original",
        top_k=20,
        hypothesis_count=2,
        tenant="harborline",
    )

    assert "tenant-b-secret" not in trace.evidence_ids


def test_conditional_policy_improves_fixture_recall_with_less_generation() -> None:
    universal = hyde_lab.summarize(hyde_lab.evaluate("hyde", top_k=1))
    conditional = hyde_lab.summarize(hyde_lab.evaluate("conditional", top_k=1))

    assert conditional["mean_recall_at_k"] >= universal["mean_recall_at_k"]
    assert conditional["total_hypotheses"] < universal["total_hypotheses"]
