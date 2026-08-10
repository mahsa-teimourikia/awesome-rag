"""Operational checks for a production-oriented RAG service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Trace:
    query: str
    route: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[str] = field(default_factory=list)
    latency_ms: float | None = None
    cost_usd: float | None = None
    trace_id: str = "local-trace"

    def record(self, event: str) -> None:
        self.events.append(event)


@dataclass(frozen=True)
class Budget:
    max_latency_ms: float
    max_cost_usd: float


def within_budget(trace: Trace, budget: Budget) -> bool:
    return (trace.latency_ms is None or trace.latency_ms <= budget.max_latency_ms) and (trace.cost_usd is None or trace.cost_usd <= budget.max_cost_usd)


def freshness_status(last_indexed: datetime, now: datetime, max_age_hours: float) -> str:
    age_hours = (now - last_indexed).total_seconds() / 3600
    return "fresh" if age_hours <= max_age_hours else "stale"


def health_status(*, index_ready: bool, evaluator_ready: bool, corpus_fresh: bool) -> dict[str, str]:
    return {"ready": "ok" if index_ready and evaluator_ready else "not-ready", "corpus": "fresh" if corpus_fresh else "stale"}


def release_gate(*, quality_score: float, min_quality: float, readiness: dict[str, str], error_rate: float, max_error_rate: float) -> dict[str, str]:
    """Return a human-readable, deterministic deployment decision."""
    reasons = []
    if quality_score < min_quality:
        reasons.append("golden-set-quality-below-threshold")
    if readiness.get("ready") != "ok":
        reasons.append("service-not-ready")
    if readiness.get("corpus") != "fresh":
        reasons.append("corpus-stale")
    if error_rate > max_error_rate:
        reasons.append("error-rate-above-threshold")
    return {"decision": "promote" if not reasons else "hold", "reasons": ",".join(reasons) or "all-gates-passed"}


def circuit_breaker(*, consecutive_failures: int, threshold: int) -> str:
    return "open" if consecutive_failures >= threshold else "closed"
