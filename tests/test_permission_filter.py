from datetime import date

from examples.intermediate.permission_filter import (
    SecureDocument,
    User,
    access_decision,
    authorize,
    authorized_documents,
    secure_search,
)


DOCS = [
    SecureDocument("acme", "Acme private runbook", "acme", frozenset({"support"})),
    SecureDocument("globex", "Globex private runbook", "globex", frozenset({"support"})),
    SecureDocument("hr", "Acme payroll", "acme", frozenset({"hr"})),
]


def test_authorization_filters_tenant_and_tags_before_retrieval():
    user = User("u1", "acme", frozenset({"support"}))
    assert [doc.doc_id for doc in authorized_documents(user, DOCS)] == ["acme"]


def test_cross_tenant_exact_match_never_returns():
    user = User("u1", "acme", frozenset({"support"}))
    result = secure_search(user, "Globex private runbook", DOCS)
    assert all(doc.doc_id != "globex" for doc, _ in result)


def test_allowed_document_can_be_retrieved():
    user = User("u1", "acme", frozenset({"support"}))
    result = secure_search(user, "private runbook", DOCS)
    assert result[0][0].doc_id == "acme"


def test_trace_records_reason_codes_without_exposing_document_text():
    user = User("u1", "acme", frozenset({"support"}))
    trace = authorize(user, DOCS)

    assert trace.allowed_ids == ("acme",)
    assert {decision.doc_id: decision.reason for decision in trace.decisions} == {
        "acme": "allowed",
        "globex": "cross-tenant",
        "hr": "missing-required-tag",
    }


def test_expired_document_is_removed_before_search():
    expired = SecureDocument(
        "expired",
        "Legacy Acme private runbook",
        "acme",
        frozenset({"support"}),
        expires_on=date(2026, 1, 1),
    )
    user = User("u1", "acme", frozenset({"support"}))

    decision = access_decision(user, expired, today=date(2026, 8, 9))
    result = secure_search(user, "Legacy Acme private runbook", [expired], today=date(2026, 8, 9))

    assert decision.reason == "expired-source"
    assert result == []
