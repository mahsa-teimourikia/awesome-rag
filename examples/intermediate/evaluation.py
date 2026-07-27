"""Small, deterministic retrieval evaluation utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    query: str
    relevant_ids: frozenset[str]


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str] | frozenset[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    return len(set(retrieved_ids[:k]) & set(relevant_ids)) / len(relevant_ids)


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str] | frozenset[str], k: int) -> float:
    selected = retrieved_ids[:k]
    return len(set(selected) & set(relevant_ids)) / max(len(selected), 1)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str] | frozenset[str]) -> float:
    relevant = set(relevant_ids)
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant:
            return 1 / rank
    return 0.0


def evaluate(retrievals: dict[str, list[str]], cases: list[EvalCase], k: int = 3) -> dict[str, float]:
    recalls, precisions, ranks = [], [], []
    for case in cases:
        retrieved = retrievals.get(case.query, [])
        recalls.append(recall_at_k(retrieved, case.relevant_ids, k))
        precisions.append(precision_at_k(retrieved, case.relevant_ids, k))
        ranks.append(reciprocal_rank(retrieved, case.relevant_ids))
    count = max(len(cases), 1)
    return {"recall@k": sum(recalls) / count, "precision@k": sum(precisions) / count, "mrr": sum(ranks) / count}
