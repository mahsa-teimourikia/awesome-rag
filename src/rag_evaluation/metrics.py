"""Small, inspectable evaluation primitives used by the PolicyAssist notebooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log2
from typing import Iterable


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    relevant_ids: frozenset[str]
    expected_behavior: str = "answer"
    severity: str = "medium"
    question_type: str = "factual"
    user_role: str = "underwriter"


@dataclass
class EvaluationTrace:
    question: str
    retrieved_ids: list[str]
    context_ids: list[str]
    citations: dict[str, list[str]] = field(default_factory=dict)
    latency_ms: int = 0
    estimated_cost: float = 0.0
    refused: bool = False


def precision_at_k(retrieved: Iterable[str], relevant: set[str] | frozenset[str], k: int) -> float:
    items = list(retrieved)[:k]
    return 0.0 if not items else sum(item in relevant for item in items) / len(items)


def recall_at_k(retrieved: Iterable[str], relevant: set[str] | frozenset[str], k: int) -> float:
    return 0.0 if not relevant else len(set(list(retrieved)[:k]) & set(relevant)) / len(relevant)


def reciprocal_rank(retrieved: Iterable[str], relevant: set[str] | frozenset[str]) -> float:
    for position, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / position
    return 0.0


def ndcg_at_k(retrieved: Iterable[str], relevance: dict[str, int], k: int) -> float:
    ranked = list(retrieved)[:k]
    dcg = sum(relevance.get(item, 0) / log2(position + 1) for position, item in enumerate(ranked, start=1))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum(value / log2(position + 1) for position, value in enumerate(ideal, start=1))
    return 0.0 if idcg == 0 else dcg / idcg


def context_recall(context_ids: Iterable[str], relevant: set[str] | frozenset[str]) -> float:
    return recall_at_k(list(context_ids), relevant, len(list(context_ids)))


def claim_support(claims: Iterable[str], citations: dict[str, list[str]], supported_by: dict[str, set[str]]) -> dict[str, bool]:
    """Return claim-level support instead of a misleading whole-answer score."""
    return {claim: bool(set(citations.get(claim, [])) & supported_by.get(claim, set())) for claim in claims}


def release_decision(metrics: dict[str, float]) -> tuple[str, list[str]]:
    gates = {"recall_at_10": 0.9, "citation_support": 0.95, "abstention_accuracy": 0.85, "permission_leak_rate": 0.0}
    blockers = [name for name, floor in gates.items() if (metrics.get(name, 0.0) < floor if name != "permission_leak_rate" else metrics.get(name, 1.0) > floor)]
    return ("GO" if not blockers else "CONDITIONAL GO", blockers)
