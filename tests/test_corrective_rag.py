from examples.advanced.corrective_rag import CorrectionPolicy, Document, Route, corrective_retrieve, lexical_retriever, assess, trace_rows


DOCS = [Document("rotation", "Rotate an API key by creating and deploying a replacement."), Document("health", "The health endpoint checks service availability.")]


def test_strong_evidence_is_accepted():
    result = assess("How do I rotate an API key?", DOCS)
    assert result.route == Route.ACCEPT
    assert result.candidates


def test_unknown_question_abstains():
    result = assess("How do I order lunch?", DOCS)
    assert result.route == Route.ABSTAIN
    assert result.candidates == ()


def test_reformulation_route_is_available_for_recovered_evidence():
    result = assess("Explain API credential replacement", DOCS, threshold=0.9)
    assert result.route in {Route.REFORMULATE, Route.ABSTAIN}


def test_alternate_retriever_is_bounded_and_traced():
    result = corrective_retrieve(
        "How do I rotate an API key?",
        DOCS,
        policy=CorrectionPolicy(max_attempts=4),
        primary_retriever=lambda query, documents: [],
        alternate_retriever=lexical_retriever,
    )
    assert result.route == Route.ALTERNATE
    assert result.answerable
    assert [row["stage"] for row in trace_rows(result)] == ["primary", "rewrite-1", "rewrite-2", "alternate"]


def test_abstention_preserves_bounded_attempt_trace():
    policy = CorrectionPolicy(max_rewrites=1, max_attempts=2)
    result = corrective_retrieve("How do I order lunch?", DOCS, policy=policy)
    assert result.route == Route.ABSTAIN
    assert not result.answerable
    assert 1 <= len(result.attempts) <= policy.max_attempts
