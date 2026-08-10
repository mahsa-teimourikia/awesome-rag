"""Customer-support RAG use case assembled from intermediate primitives."""

from __future__ import annotations

import sys
import re
from pathlib import Path

from examples.beginner.citations import Citation, CitedAnswer, render_markdown
from examples.intermediate.permission_filter import SecureDocument, User, authorized_documents
from examples.intermediate.query_reranking import rerank, retrieve_candidates
from examples.intermediate.retrieval_strategies import Document


DOCS = [
    SecureDocument("public-keys", "Create a replacement API key, deploy it, verify traffic, then revoke the old key.", "public", frozenset()),
    SecureDocument("public-health", "Use GET /health to check service availability without authentication.", "public", frozenset()),
    SecureDocument("acme-plan", "Acme Pro accounts include priority support and monthly usage summaries.", "acme", frozenset({"support"})),
    SecureDocument("globex-plan", "Globex accounts include standard support and annual usage summaries.", "globex", frozenset({"support"})),
]
SENSITIVE = ("refund", "cancel", "cancellation", "chargeback")
STOPWORDS = {"a", "an", "and", "are", "do", "how", "i", "is", "of", "on", "the", "what", "with"}


def support_answer(tenant_id: str, query: str) -> str:
    if any(word in query.lower() for word in SENSITIVE):
        return "This request needs a support specialist. I have not taken any account action.\n\nReason: `human-review-required`"
    user = User(f"support-{tenant_id}", tenant_id, frozenset({"support"}))
    allowed = authorized_documents(user, DOCS) + [doc for doc in DOCS if doc.tenant_id == "public"]
    candidates, _ = retrieve_candidates(query, [Document(doc.doc_id, doc.text) for doc in allowed])
    ranked = rerank(query, candidates, top_k=3)
    query_terms = set(re.findall(r"[a-z0-9]+", query.lower())) - STOPWORDS
    evidence_terms = set(re.findall(r"[a-z0-9]+", ranked[0].document.text.lower())) if ranked else set()
    if not ranked or ranked[0].score < 0.25 or not query_terms.intersection(evidence_terms):
        return "I need more context before drafting a reliable answer.\n\nReason: `insufficient-evidence`"
    citations = tuple(Citation(item.document.doc_id, f"{item.document.doc_id}.md", item.score) for item in ranked)
    return render_markdown(CitedAnswer(ranked[0].document.text, citations, False, "grounded-evidence"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python app.py <tenant> <question>")
    print(support_answer(sys.argv[1], sys.argv[2]))
