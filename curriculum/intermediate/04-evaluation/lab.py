"""Deterministic RAG evaluation and release-gate utilities.

These functions make retrieval, answer-support, abstention, and operational
signals visible without a provider dependency.  In production, model/judge
adapters should emit the same explicit observations and be calibrated against
human-reviewed cases.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    query: str
    relevant_ids: frozenset[str]
    slice: str = "general"
    answerable: bool = True


@dataclass(frozen=True)
class EvalObservation:
    query: str
    retrieved_ids: tuple[str, ...]
    cited_ids: tuple[str, ...]
    answered: bool
    supported: bool
    latency_ms: float
    estimated_cost: float


@dataclass(frozen=True)
class ReleaseGate:
    minimum_recall: float = 0.8
    minimum_mrr: float = 0.7
    minimum_citation_coverage: float = 0.9
    minimum_abstention_accuracy: float = 0.9
    maximum_p95_latency_ms: float = 2_000.0
    maximum_cost_per_case: float = 0.03


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


def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str] | frozenset[str], k: int) -> float:
    """Binary-relevance normalized discounted cumulative gain."""

    relevant = set(relevant_ids)
    dcg = sum((1 / math.log2(rank + 1)) for rank, doc_id in enumerate(retrieved_ids[:k], start=1) if doc_id in relevant)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
    return dcg / ideal if ideal else 1.0


def citation_coverage(observations: list[EvalObservation]) -> float:
    """Fraction of answered cases whose citations are nonempty and supported."""

    answered = [row for row in observations if row.answered]
    if not answered:
        return 1.0
    return sum(bool(row.cited_ids) and row.supported for row in answered) / len(answered)


def abstention_accuracy(observations: list[EvalObservation], cases: list[EvalCase]) -> float:
    expected = {case.query: case.answerable for case in cases}
    if not observations:
        return 1.0
    return sum(row.answered == expected.get(row.query, False) for row in observations) / len(observations)


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = math.ceil(percentile_value / 100 * len(ordered)) - 1
    return ordered[max(0, min(index, len(ordered) - 1))]


def evaluate(retrievals: dict[str, list[str]], cases: list[EvalCase], k: int = 3) -> dict[str, float]:
    # Retrieval metrics describe whether evidence was found for answerable
    # requests.  No-answer behavior is measured separately by abstention
    # accuracy; otherwise correct abstentions would artificially lower MRR.
    cases = [case for case in cases if case.answerable]
    recalls, precisions, ranks, ndcgs = [], [], [], []
    for case in cases:
        retrieved = retrievals.get(case.query, [])
        recalls.append(recall_at_k(retrieved, case.relevant_ids, k))
        precisions.append(precision_at_k(retrieved, case.relevant_ids, k))
        ranks.append(reciprocal_rank(retrieved, case.relevant_ids))
        ndcgs.append(ndcg_at_k(retrieved, case.relevant_ids, k))
    count = max(len(cases), 1)
    return {
        "recall@k": sum(recalls) / count,
        "precision@k": sum(precisions) / count,
        "mrr": sum(ranks) / count,
        "ndcg@k": sum(ndcgs) / count,
    }


def evaluate_slices(retrievals: dict[str, list[str]], cases: list[EvalCase], k: int = 3) -> dict[str, dict[str, float]]:
    """Report metrics by failure-mode slice; averages must not hide a weak slice."""

    slices = sorted({case.slice for case in cases})
    return {slice_name: evaluate(retrievals, [case for case in cases if case.slice == slice_name], k) for slice_name in slices}


def release_report(
    retrievals: dict[str, list[str]],
    cases: list[EvalCase],
    observations: list[EvalObservation],
    *,
    gate: ReleaseGate = ReleaseGate(),
    k: int = 3,
) -> dict[str, object]:
    """Return measurable release criteria and failure reasons, never a hidden score."""

    metrics = evaluate(retrievals, cases, k)
    coverage = citation_coverage(observations)
    abstention = abstention_accuracy(observations, cases)
    p95_latency = percentile([row.latency_ms for row in observations], 95)
    average_cost = sum(row.estimated_cost for row in observations) / max(len(observations), 1)
    checks = {
        "retrieval_recall": metrics["recall@k"] >= gate.minimum_recall,
        "retrieval_mrr": metrics["mrr"] >= gate.minimum_mrr,
        "citation_coverage": coverage >= gate.minimum_citation_coverage,
        "abstention": abstention >= gate.minimum_abstention_accuracy,
        "p95_latency": p95_latency <= gate.maximum_p95_latency_ms,
        "average_cost": average_cost <= gate.maximum_cost_per_case,
    }
    return {
        "ship": all(checks.values()),
        "checks": checks,
        "metrics": metrics,
        "citation_coverage": coverage,
        "abstention_accuracy": abstention,
        "p95_latency_ms": p95_latency,
        "average_cost": average_cost,
        "slice_metrics": evaluate_slices(retrievals, cases, k),
    }
