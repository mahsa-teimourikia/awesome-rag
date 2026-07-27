"""Query expansion and second-stage reranking primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .retrieval_strategies import BM25, Document, terms


@dataclass(frozen=True)
class RankedDocument:
    document: Document
    score: float
    source_queries: tuple[str, ...]


def rewrite_query(query: str) -> list[str]:
    """Create deterministic variants; a production system may use an LLM with validation."""
    normalized = re.sub(r"\s+", " ", query.strip())
    variants = [normalized]
    if normalized:
        variants.append(f"key concepts: {normalized}")
        variants.append(f"specific evidence for: {normalized}")
    return list(dict.fromkeys(variants))


def retrieve_candidates(query: str, documents: list[Document], *, top_k: int = 5) -> list[RankedDocument]:
    candidates: dict[str, RankedDocument] = {}
    for variant in rewrite_query(query):
        for document, score in BM25(documents).search(variant, top_k=top_k):
            current = candidates.get(document.doc_id)
            sources = (current.source_queries if current else ()) + (variant,)
            candidates[document.doc_id] = RankedDocument(document, max(score, current.score if current else 0.0), tuple(dict.fromkeys(sources)))
    return list(candidates.values())


def rerank(query: str, candidates: list[RankedDocument], *, top_k: int = 3) -> list[RankedDocument]:
    query_terms = set(terms(query))
    rescored = []
    for candidate in candidates:
        document_terms = set(terms(candidate.document.text))
        overlap = len(query_terms & document_terms) / max(len(query_terms), 1)
        rescored.append(RankedDocument(candidate.document, 0.7 * overlap + 0.3 * candidate.score, candidate.source_queries))
    return sorted(rescored, key=lambda item: (-item.score, item.document.doc_id))[:top_k]
