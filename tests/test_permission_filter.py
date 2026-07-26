from examples.intermediate.permission_filter import SecureDocument, User, authorized_documents, secure_search


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
