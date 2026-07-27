"""Corrective retrieval with explicit recovery decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from examples.intermediate.query_reranking import retrieve_candidates, rewrite_query
from examples.intermediate.retrieval_strategies import Document, terms

STOPWORDS = {"a", "an", "and", "do", "how", "i", "is", "of", "the", "to", "what"}


class Route(str, Enum):
    ACCEPT = "accept"
    REFORMULATE = "reformulate"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class RetrievalDecision:
    route: Route
    query: str
    candidates: tuple[Document, ...]
    confidence: float
    reason: str


def assess(query: str, documents: list[Document], *, threshold: float = 0.35) -> RetrievalDecision:
    first = retrieve_candidates(query, documents, top_k=3)
    query_terms = set(terms(query)) - STOPWORDS
    confidence = (len(query_terms & set(terms(first[0].document.text))) / max(len(query_terms), 1)) if first else 0.0
    if confidence >= threshold:
        return RetrievalDecision(Route.ACCEPT, query, tuple(item.document for item in first), confidence, "strong-first-stage-evidence")
    variants = rewrite_query(query)[1:]
    recovered = []
    for variant in variants:
        recovered.extend(retrieve_candidates(variant, documents, top_k=2))
    unique = {item.document.doc_id: item.document for item in recovered}
    if unique:
        best = max(recovered, key=lambda item: item.score)
        recovered_confidence = len(query_terms & set(terms(best.document.text))) / max(len(query_terms), 1)
        if recovered_confidence >= threshold:
            return RetrievalDecision(Route.REFORMULATE, variants[0], tuple(unique.values()), recovered_confidence, "recovered-after-query-reformulation")
    return RetrievalDecision(Route.ABSTAIN, query, (), confidence, "insufficient-evidence-after-recovery")
