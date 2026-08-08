from pathlib import Path

from examples.beginner.citations import AbstentionPolicy, answer_with_citations, audit_answer, citations_are_retrieved, render_markdown
from examples.beginner.first_local_rag import load_chunks


ROOT = Path(__file__).parents[1]


def test_grounded_answer_has_structured_retrieved_citations():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = answer_with_citations("What is an abstention?", chunks)
    assert not result.abstained
    assert result.citations
    assert citations_are_retrieved(result, chunks)
    assert "Sources:" in render_markdown(result)


def test_unsupported_question_abstains_with_reason():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = answer_with_citations("What is the capital of France?", chunks)
    assert result.abstained
    assert result.reason == "insufficient-evidence"
    assert result.citations == ()


def test_high_threshold_can_abstain_on_weak_evidence():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = answer_with_citations("What is an abstention?", chunks, min_score=1.01)
    assert result.abstained


def test_policy_can_abstain_when_evidence_is_ambiguous():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = answer_with_citations(
        "What must an answer distinguish?",
        chunks,
        policy=AbstentionPolicy(min_score=0.1, min_margin=0.9),
    )
    assert result.abstained
    assert result.reason == "ambiguous-evidence"


def test_audit_keeps_provenance_checks_separate_from_rendering():
    chunks = load_chunks(ROOT / "examples" / "data" / "beginner-docs")
    result = answer_with_citations("What should support do for a confirmed payment incident?", chunks)
    audit = audit_answer(result, chunks)
    assert audit.citations_retrieved
    assert audit.decision == "answer"
