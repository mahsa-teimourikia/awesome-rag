"""Inspectable lexical, dense-adapter, and hybrid retrieval strategies."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field


TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str


@dataclass(frozen=True)
class AttributedDocument(Document):
    """A document carrying retrieval-time metadata such as tenant and freshness."""

    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalTrace:
    """Inspectable candidate, fusion, and reranking output for one request."""

    query: str
    filters: dict[str, str]
    lexical_ids: tuple[str, ...]
    dense_ids: tuple[str, ...]
    fused_ids: tuple[str, ...]
    final_ids: tuple[str, ...]


@dataclass(frozen=True)
class RankingMetrics:
    recall_at_k: float
    mean_reciprocal_rank: float


def terms(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class BM25:
    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1, self.b = k1, b
        self.term_frequencies = [Counter(terms(doc.text)) for doc in documents]
        self.lengths = [sum(freq.values()) for freq in self.term_frequencies]
        self.average_length = sum(self.lengths) / max(len(self.lengths), 1)
        self.document_frequency = Counter(term for freq in self.term_frequencies for term in freq)

    def search(self, query: str, top_k: int = 3) -> list[tuple[Document, float]]:
        query_terms = set(terms(query))
        scored = []
        count = len(self.documents)
        for doc, frequencies, length in zip(self.documents, self.term_frequencies, self.lengths):
            score = 0.0
            for term in query_terms:
                if term not in frequencies:
                    continue
                df = self.document_frequency[term]
                idf = math.log(1 + (count - df + 0.5) / (df + 0.5))
                tf = frequencies[term]
                norm = tf + self.k1 * (1 - self.b + self.b * length / max(self.average_length, 1))
                score += idf * (tf * (self.k1 + 1) / norm)
            if score:
                scored.append((doc, score))
        return sorted(scored, key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]


def filter_documents(documents: list[Document], filters: dict[str, str] | None = None) -> list[Document]:
    """Apply exact metadata filters before retrieval/fusion.

    This tiny function demonstrates the placement of authorization, tenant, and
    freshness filters. Production backends should apply equivalent filters in
    their query, not retrieve all candidates and filter an answer afterwards.
    """

    filters = filters or {}
    return [
        document
        for document in documents
        if all(getattr(document, "metadata", {}).get(key) == value for key, value in filters.items())
    ]


def static_dense_ranking(documents: list[Document], scores_by_id: dict[str, float], top_k: int = 3) -> list[Document]:
    """Adapt externally computed dense scores without hiding the boundary.

    The course supplies deterministic scores so it runs without a model download.
    Replace this adapter with Sentence Transformers or a vector database only
    after evaluating the same query set and metadata filters.
    """

    return [
        document
        for document, score in sorted(
            ((document, scores_by_id.get(document.doc_id, 0.0)) for document in documents),
            key=lambda item: (-item[1], item[0].doc_id),
        )[:top_k]
        if score > 0
    ]


def reciprocal_rank_fusion(*rankings: list[Document], k: int = 60, top_k: int = 3) -> list[tuple[Document, float]]:
    scores: dict[str, tuple[Document, float]] = {}
    for ranking in rankings:
        for rank, document in enumerate(ranking, start=1):
            current = scores.get(document.doc_id, (document, 0.0))
            scores[document.doc_id] = (document, current[1] + 1 / (k + rank))
    return sorted(scores.values(), key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]


def weighted_reciprocal_rank_fusion(
    rankings: list[tuple[list[Document], float]],
    *,
    k: int = 60,
    top_k: int = 3,
) -> list[tuple[Document, float]]:
    """Fuse ranks with explicit, evaluated retriever weights."""

    scores: dict[str, tuple[Document, float]] = {}
    for ranking, weight in rankings:
        if weight < 0:
            raise ValueError("weights must be non-negative")
        for rank, document in enumerate(ranking, start=1):
            current = scores.get(document.doc_id, (document, 0.0))
            scores[document.doc_id] = (document, current[1] + weight / (k + rank))
    return sorted(scores.values(), key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]


def rerank_by_query_coverage(query: str, candidates: list[Document], top_k: int = 3) -> list[tuple[Document, float]]:
    """A transparent second-stage reranker used only on a bounded candidate set.

    This is not a neural cross-encoder. It demonstrates the contract: first-stage
    retrieval recalls candidates; a more expensive stage reorders only those
    candidates. It cannot recover a document that was never retrieved.
    """

    query_terms = set(terms(query))
    scored: list[tuple[Document, float]] = []
    for document in candidates:
        document_terms = terms(document.text)
        coverage = len(query_terms & set(document_terms)) / max(len(query_terms), 1)
        phrase_bonus = 0.2 if query.lower() in document.text.lower() else 0.0
        scored.append((document, coverage + phrase_bonus))
    return sorted(scored, key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]


def hybrid_retrieve(
    query: str,
    documents: list[Document],
    dense_scores: dict[str, float],
    *,
    filters: dict[str, str] | None = None,
    candidate_k: int = 5,
    final_k: int = 3,
    lexical_weight: float = 1.0,
    dense_weight: float = 1.0,
) -> tuple[list[tuple[Document, float]], RetrievalTrace]:
    """Run filter -> lexical/dense candidates -> RRF -> rerank with a trace."""

    visible = filter_documents(documents, filters)
    lexical = [document for document, _ in BM25(visible).search(query, top_k=candidate_k)]
    dense = static_dense_ranking(visible, dense_scores, top_k=candidate_k)
    fused = weighted_reciprocal_rank_fusion(
        [(lexical, lexical_weight), (dense, dense_weight)],
        top_k=candidate_k,
    )
    reranked = rerank_by_query_coverage(query, [document for document, _ in fused], top_k=final_k)
    trace = RetrievalTrace(
        query=query,
        filters=dict(filters or {}),
        lexical_ids=tuple(document.doc_id for document in lexical),
        dense_ids=tuple(document.doc_id for document in dense),
        fused_ids=tuple(document.doc_id for document, _ in fused),
        final_ids=tuple(document.doc_id for document, _ in reranked),
    )
    return reranked, trace


def ranking_metrics(rankings: list[list[Document]], relevant_ids: list[set[str]], *, k: int = 3) -> RankingMetrics:
    """Compute retrieval-only Recall@k and MRR over a small labelled dataset."""

    if len(rankings) != len(relevant_ids):
        raise ValueError("rankings and relevant_ids must have equal length")
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    for ranking, relevant in zip(rankings, relevant_ids):
        identifiers = [document.doc_id for document in ranking[:k]]
        recalls.append(float(bool(set(identifiers) & relevant)))
        first = next((rank for rank, identifier in enumerate(identifiers, start=1) if identifier in relevant), None)
        reciprocal_ranks.append(1 / first if first else 0.0)
    return RankingMetrics(sum(recalls) / max(len(recalls), 1), sum(reciprocal_ranks) / max(len(reciprocal_ranks), 1))
