"""Metadata filtering before retrieval for multi-tenant RAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.rag_core.retrieval import BM25, Document


@dataclass(frozen=True)
class User:
    user_id: str
    tenant_id: str
    allowed_tags: frozenset[str] = field(default_factory=frozenset)
    clearance: str = "internal"


@dataclass(frozen=True)
class SecureDocument(Document):
    tenant_id: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)
    classification: str = "internal"
    expires_on: date | None = None
    version: str = "1"


@dataclass(frozen=True)
class AccessDecision:
    doc_id: str
    allowed: bool
    reason: str


@dataclass(frozen=True)
class AuthorizationTrace:
    user_id: str
    tenant_id: str
    decisions: tuple[AccessDecision, ...]

    @property
    def allowed_ids(self) -> tuple[str, ...]:
        return tuple(decision.doc_id for decision in self.decisions if decision.allowed)


def access_decision(user: User, document: SecureDocument, *, today: date | None = None) -> AccessDecision:
    """Evaluate a deterministic tenant/tag/freshness policy for one document."""

    today = today or date.today()
    if document.tenant_id != user.tenant_id:
        return AccessDecision(document.doc_id, False, "cross-tenant")
    if not document.tags <= user.allowed_tags:
        return AccessDecision(document.doc_id, False, "missing-required-tag")
    if document.expires_on and document.expires_on < today:
        return AccessDecision(document.doc_id, False, "expired-source")
    return AccessDecision(document.doc_id, True, "allowed")


def authorize(user: User, documents: list[SecureDocument], *, today: date | None = None) -> AuthorizationTrace:
    """Return an auditable allow/deny result before a retriever is constructed."""

    return AuthorizationTrace(user.user_id, user.tenant_id, tuple(access_decision(user, doc, today=today) for doc in documents))


def authorized_documents(user: User, documents: list[SecureDocument], *, today: date | None = None) -> list[SecureDocument]:
    """Filter by authorization before constructing a retriever."""
    allowed_ids = set(authorize(user, documents, today=today).allowed_ids)
    return [doc for doc in documents if doc.doc_id in allowed_ids]


def secure_search(user: User, query: str, documents: list[SecureDocument], top_k: int = 3, *, today: date | None = None) -> list[tuple[SecureDocument, float]]:
    allowed = authorized_documents(user, documents, today=today)
    return BM25(allowed).search(query, top_k=top_k)
