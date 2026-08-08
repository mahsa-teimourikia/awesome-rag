"""A transparent, bounded router: teaching policy selection before agent frameworks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    strategy: str
    reason: str
    retrieval_needed: bool
    method: str | None
    max_steps: int


def classify_query(question: str) -> RouteDecision:
    q = question.lower()
    if any(term in q for term in ("our policy", "company", "approved for deployment", "current", "2026")):
        if any(term in q for term in ("compare", "why", "changed", "moved", "which policy applies")):
            return RouteDecision("iterative_rag", "temporal or multi-document policy reasoning", True, "hybrid", 3)
        return RouteDecision("single_rag", "private or current enterprise fact", True, "hybrid", 1)
    if any(term in q for term in ("policy pol-", "hx-", "error code")):
        return RouteDecision("single_rag", "exact identifier benefits from lexical retrieval", True, "bm25", 1)
    if any(term in q for term in ("major themes", "across all reports", "relationships")):
        return RouteDecision("graph_rag", "corpus-wide or relational synthesis", True, "graph", 2)
    return RouteDecision("no_retrieval", "stable general knowledge with no enterprise or freshness cue", False, None, 0)


def choose_k(question: str, uncertainty: float = 0.0) -> int:
    q = question.lower()
    if any(term in q for term in ("compare", "why", "all", "sections", "appendix")):
        return 10
    if uncertainty > 0.5:
        return 5
    return 2


def transform_query(question: str, strategy: str) -> list[str]:
    if strategy != "iterative_rag":
        return [question]
    return [question, question.replace("changed", "policy differences effective dates"), "authoritative policy version and eligibility conditions"]


def evidence_quality(evidence: list[str]) -> str:
    if not evidence:
        return "poor"
    if any("stale" in item.lower() for item in evidence):
        return "ambiguous"
    return "good"


def adaptive_answer(question: str, retrieve) -> dict:
    """Execute a small adaptive loop with visible continuation bounds."""
    decision = classify_query(question)
    if not decision.retrieval_needed:
        return {"route": decision, "queries": [], "evidence": [], "status": "answer_directly"}
    queries = transform_query(question, decision.strategy)
    evidence: list[str] = []
    for attempt, query in enumerate(queries[: decision.max_steps], start=1):
        evidence.extend(retrieve(query, choose_k(query)))
        if evidence_quality(evidence) == "good":
            return {"route": decision, "queries": queries[:attempt], "evidence": evidence, "status": "answer_grounded"}
    return {"route": decision, "queries": queries, "evidence": evidence, "status": "abstain_or_escalate"}
