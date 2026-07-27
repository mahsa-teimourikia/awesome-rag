from examples.advanced.corrective_rag import Document, Route, assess


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
