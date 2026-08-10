"""Inspectable query planning, fusion, reranking, and evaluation primitives.

The implementation is deliberately deterministic so the accompanying notebook
can be executed without credentials.  Production adapters can replace the
rewrite and scoring functions, but should preserve the same bounded candidate
set, trace fields, and evaluation contracts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.rag_core.retrieval import BM25, Document, reciprocal_rank_fusion, terms


SYNONYMS = {
    "credential": ("api key", "token", "secret"),
    "credentials": ("api key", "token", "secret"),
    "replace": ("rotate", "renew"),
    "replacement": ("rotate", "renew"),
    "slow": ("latency", "timeout"),
    "europe": ("eu", "european"),
}


@dataclass(frozen=True)
class RankedDocument:
    document: Document
    score: float
    source_queries: tuple[str, ...]
    first_stage_rank: int


@dataclass(frozen=True)
class RetrievalTrace:
    query: str
    variants: tuple[str, ...]
    candidate_count: int
    rerank_count: int


def rewrite_query(query: str, *, max_variants: int = 4) -> list[str]:
    """Create bounded, inspectable query variants while retaining the original.

    A model-based rewriter should return structured variants, be rate/budget
    bounded, and be evaluated against a golden set.  It must never replace the
    original query silently: exact identifiers and user constraints are often
    critical retrieval signals.
    """

    normalized = re.sub(r"\s+", " ", query.strip())
    if not normalized:
        return []
    # Keep the two baseline variants used by earlier course examples.  They are
    # intentionally simple and make recovery paths reproducible; synonym views
    # are additive rather than silently replacing them.
    variants = [normalized, f"key concepts: {normalized}", f"specific evidence for: {normalized}"]
    lowered = normalized.lower()
    for term, replacements in SYNONYMS.items():
        if term in lowered:
            for replacement in replacements:
                variants.append(re.sub(rf"\b{re.escape(term)}\b", replacement, normalized, flags=re.IGNORECASE))
    return list(dict.fromkeys(variants))[:max_variants]


def retrieve_candidates(
    query: str,
    documents: list[Document],
    *,
    top_k_per_variant: int = 5,
    candidate_budget: int = 12,
) -> tuple[list[RankedDocument], RetrievalTrace]:
    """Retrieve each query view, fuse rankings, and retain provenance.

    Reciprocal-rank fusion is robust when score scales differ across variants:
    it combines ranks rather than pretending BM25 scores are directly
    comparable.  Candidate depth is explicit because downstream cross-encoder
    work grows with the number of query-document pairs.
    """

    variants = rewrite_query(query)
    rankings: list[list[Document]] = []
    provenance: dict[str, list[str]] = {}
    first_ranks: dict[str, int] = {}
    bm25 = BM25(documents)
    for variant in variants:
        hits = bm25.search(variant, top_k=top_k_per_variant)
        ranking = [document for document, _ in hits]
        rankings.append(ranking)
        for rank, document in enumerate(ranking, start=1):
            provenance.setdefault(document.doc_id, []).append(variant)
            first_ranks[document.doc_id] = min(first_ranks.get(document.doc_id, rank), rank)

    fused = reciprocal_rank_fusion(*rankings, top_k=candidate_budget)
    candidates = [
        RankedDocument(document, score, tuple(provenance[document.doc_id]), first_ranks[document.doc_id])
        for document, score in fused
    ]
    trace = RetrievalTrace(query, tuple(variants), len(candidates), 0)
    return candidates, trace


def _cross_encoder_proxy(query: str, document: Document) -> float:
    """A transparent local proxy for a cross-encoder relevance score.

    Real cross-encoders jointly attend to query and document.  This proxy keeps
    the lab deterministic while demonstrating why a second stage may reorder
    candidates using phrase overlap and coverage rather than only first-stage
    ranking.  Do not use it as a production relevance model.
    """

    query_terms = set(terms(query))
    document_terms = set(terms(document.text))
    coverage = len(query_terms & document_terms) / max(len(query_terms), 1)
    query_tokens = terms(query)
    document_text = " ".join(terms(document.text))
    # A matching identifier or short phrase is strong evidence even when a
    # conversational query contains many stop words the document does not.
    phrase_bonus = 0.20 if any(" ".join(query_tokens[i : i + 2]) in document_text for i in range(len(query_tokens) - 1)) else 0.0
    return min(1.0, coverage + phrase_bonus)


def rerank(query: str, candidates: list[RankedDocument], *, top_k: int = 3) -> list[RankedDocument]:
    """Rerank a bounded candidate set using the original user question."""

    rescored = [
        RankedDocument(
            candidate.document,
            0.85 * _cross_encoder_proxy(query, candidate.document) + 0.15 * candidate.score,
            candidate.source_queries,
            candidate.first_stage_rank,
        )
        for candidate in candidates
    ]
    return sorted(rescored, key=lambda item: (-item.score, item.document.doc_id))[:top_k]


def pipeline(
    query: str,
    documents: list[Document],
    *,
    top_k_per_variant: int = 5,
    candidate_budget: int = 12,
    final_k: int = 3,
) -> tuple[list[RankedDocument], RetrievalTrace]:
    """Run the bounded two-stage pipeline and return its trace."""

    candidates, trace = retrieve_candidates(
        query, documents, top_k_per_variant=top_k_per_variant, candidate_budget=candidate_budget
    )
    return rerank(query, candidates, top_k=final_k), RetrievalTrace(
        trace.query, trace.variants, trace.candidate_count, min(len(candidates), final_k)
    )


def recall_at_k(ranking: list[RankedDocument], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of labeled relevant documents present in the top k."""

    if not relevant_ids:
        return 1.0
    returned = {item.document.doc_id for item in ranking[:k]}
    return len(returned & relevant_ids) / len(relevant_ids)


def reciprocal_rank(ranking: list[RankedDocument], relevant_ids: set[str]) -> float:
    """Return reciprocal rank of the first labeled relevant result."""

    for position, item in enumerate(ranking, start=1):
        if item.document.doc_id in relevant_ids:
            return 1 / position
    return 0.0
