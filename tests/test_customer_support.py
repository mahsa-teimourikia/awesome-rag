import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("customer_support_app", Path(__file__).parents[1] / "use-cases/customer-support/app.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)
support_answer = module.support_answer


def test_public_support_question_returns_citation():
    result = support_answer("acme", "How do I rotate an API key?")
    assert "public-keys" in result
    assert "Sources:" in result


def test_sensitive_request_escalates():
    result = support_answer("acme", "Please refund my last invoice")
    assert "human-review-required" in result


def test_unknown_question_escalates_for_more_context():
    result = support_answer("acme", "What is the weather on Mars?")
    assert "insufficient-evidence" in result
