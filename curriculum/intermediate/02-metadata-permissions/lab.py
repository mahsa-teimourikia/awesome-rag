"""Metadata filtering before retrieval for multi-tenant RAG."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.rag_core.retrieval import BM25, Document


@dataclass(frozen=True)
class User:
    user_id: str
    tenant_id: str
    allowed_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SecureDocument(Document):
    tenant_id: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)


def authorized_documents(user: User, documents: list[SecureDocument]) -> list[SecureDocument]:
    """Filter by authorization before constructing a retriever."""
    return [doc for doc in documents if doc.tenant_id == user.tenant_id and doc.tags <= user.allowed_tags]


def secure_search(user: User, query: str, documents: list[SecureDocument], top_k: int = 3) -> list[tuple[SecureDocument, float]]:
    allowed = authorized_documents(user, documents)
    return BM25(allowed).search(query, top_k=top_k)
