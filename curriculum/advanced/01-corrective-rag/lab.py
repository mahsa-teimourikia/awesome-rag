"""A deterministic, auditable Corrective RAG controller.

The module deliberately uses lexical retrieval so every decision is inspectable
and executable without credentials.  Replace the retrieval adapters in a real
system; keep the policy, trace, authorization, and abstention boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Callable, Iterable

from examples.intermediate.query_reranking import RankedDocument, retrieve_candidates, rewrite_query
from examples.intermediate.retrieval_strategies import Document, terms


STOPWORDS = {"a", "an", "and", "do", "how", "i", "is", "of", "the", "to", "what", "with"}


class Route(str, Enum):
    """The terminal action selected by the corrective policy."""

    ACCEPT = "accept"
    REFORMULATE = "reformulate"
    ALTERNATE = "alternate"
    ABSTAIN = "abstain"


class EvidenceGrade(str, Enum):
    STRONG = "strong"
    AMBIGUOUS = "ambiguous"
    WEAK = "weak"


@dataclass(frozen=True)
class RetrievalDecision:
    """Compatibility result for the first, compact lesson API."""

    route: Route
    query: str
    candidates: tuple[Document, ...]
    confidence: float
    reason: str


@dataclass(frozen=True)
class Attempt:
    """One observable retrieval attempt; never discard failed evidence."""

    stage: str
    query: str
    candidate_ids: tuple[str, ...]
    score: float
    grade: EvidenceGrade
    latency_ms: float
    reason: str


@dataclass(frozen=True)
class CorrectionPolicy:
    """A bounded recovery policy; scores require offline calibration in production."""

    strong_threshold: float = 0.58
    ambiguous_threshold: float = 0.28
    max_rewrites: int = 2
    max_attempts: int = 4
    permitted_sources: frozenset[str] = frozenset({"internal"})
    require_two_distinct_query_terms: bool = True


@dataclass(frozen=True)
class CorrectiveResult:
    route: Route
    answerable: bool
    selected: tuple[Document, ...]
    confidence: float
    attempts: tuple[Attempt, ...]
    reason: str

    @property
    def total_latency_ms(self) -> float:
        return round(sum(attempt.latency_ms for attempt in self.attempts), 3)


Retriever = Callable[[str, list[Document]], list[RankedDocument]]


def _meaningful_terms(query: str) -> set[str]:
    return set(terms(query)) - STOPWORDS


def _coverage_score(query: str, candidates: Iterable[RankedDocument]) -> float:
    """Score whether the retrieved set covers the important query terms.

    This is *not* a calibrated probability or a substitute for a learned
    evaluator.  It is a transparent teaching baseline that makes thresholds,
    traces, and routing testable before adding model-based grading.
    """

    query_terms = _meaningful_terms(query)
    if not query_terms:
        return 0.0
    candidate_terms = set().union(*(set(terms(item.document.text)) for item in candidates)) if candidates else set()
    return len(query_terms & candidate_terms) / len(query_terms)


def grade_retrieval(query: str, candidates: list[RankedDocument], policy: CorrectionPolicy) -> tuple[EvidenceGrade, float, str]:
    """Return an explicit grade, score, and explanation for routing."""

    query_terms = _meaningful_terms(query)
    if policy.require_two_distinct_query_terms and len(query_terms) < 2:
        return EvidenceGrade.WEAK, 0.0, "underspecified-query-requires-clarification"
    if not candidates:
        return EvidenceGrade.WEAK, 0.0, "no-authorized-candidates"

    score = _coverage_score(query, candidates)
    if score >= policy.strong_threshold:
        return EvidenceGrade.STRONG, score, "query-terms-covered-by-authorized-evidence"
    if score >= policy.ambiguous_threshold:
        return EvidenceGrade.AMBIGUOUS, score, "partial-evidence-coverage-needs-correction"
    return EvidenceGrade.WEAK, score, "insufficient-query-term-coverage"


def authorized(documents: list[Document], policy: CorrectionPolicy) -> list[Document]:
    """Apply source authorization *before* any retrieval or model context."""

    return [document for document in documents if getattr(document, "source", "internal") in policy.permitted_sources]


def lexical_retriever(query: str, documents: list[Document]) -> list[RankedDocument]:
    candidates, _ = retrieve_candidates(query, documents, top_k_per_variant=4)
    return candidates


def _attempt(stage: str, query: str, retriever: Retriever, documents: list[Document], policy: CorrectionPolicy) -> tuple[Attempt, list[RankedDocument]]:
    started = perf_counter()
    candidates = retriever(query, authorized(documents, policy))
    grade, score, reason = grade_retrieval(query, candidates, policy)
    trace = Attempt(
        stage=stage,
        query=query,
        candidate_ids=tuple(item.document.doc_id for item in candidates),
        score=round(score, 3),
        grade=grade,
        latency_ms=round((perf_counter() - started) * 1000, 3),
        reason=reason,
    )
    return trace, candidates


def corrective_retrieve(
    query: str,
    documents: list[Document],
    *,
    policy: CorrectionPolicy = CorrectionPolicy(),
    primary_retriever: Retriever = lexical_retriever,
    alternate_retriever: Retriever | None = None,
) -> CorrectiveResult:
    """Run a bounded corrective retrieval policy.

    Sequence: grade primary retrieval → use a limited number of rewrite routes
    for ambiguous/weak evidence → optionally try one *authorized* alternate
    retriever → abstain.  This is intentionally a controller, not an endless
    autonomous loop.
    """

    attempts: list[Attempt] = []
    first, candidates = _attempt("primary", query, primary_retriever, documents, policy)
    attempts.append(first)
    if first.grade is EvidenceGrade.STRONG:
        return CorrectiveResult(Route.ACCEPT, True, tuple(item.document for item in candidates), first.score, tuple(attempts), "accepted-strong-primary-evidence")

    variants = rewrite_query(query)[1 : 1 + policy.max_rewrites]
    for index, variant in enumerate(variants, start=1):
        if len(attempts) >= policy.max_attempts:
            break
        trace, recovered = _attempt(f"rewrite-{index}", variant, primary_retriever, documents, policy)
        attempts.append(trace)
        if trace.grade is EvidenceGrade.STRONG:
            return CorrectiveResult(Route.REFORMULATE, True, tuple(item.document for item in recovered), trace.score, tuple(attempts), "accepted-after-bounded-reformulation")

    if alternate_retriever and len(attempts) < policy.max_attempts:
        trace, recovered = _attempt("alternate", query, alternate_retriever, documents, policy)
        attempts.append(trace)
        if trace.grade is EvidenceGrade.STRONG:
            return CorrectiveResult(Route.ALTERNATE, True, tuple(item.document for item in recovered), trace.score, tuple(attempts), "accepted-after-authorized-alternate-retrieval")

    best = max((attempt.score for attempt in attempts), default=0.0)
    return CorrectiveResult(Route.ABSTAIN, False, (), best, tuple(attempts), "insufficient-authorized-evidence-after-bounded-correction")


def assess(query: str, documents: list[Document], *, threshold: float = 0.35) -> RetrievalDecision:
    """Backwards-compatible compact API used by earlier course exercises."""

    policy = CorrectionPolicy(strong_threshold=threshold, ambiguous_threshold=max(0.0, threshold / 2))
    result = corrective_retrieve(query, documents, policy=policy)
    return RetrievalDecision(result.route, query, result.selected, result.confidence, result.reason)


def trace_rows(result: CorrectiveResult) -> list[dict[str, object]]:
    """A serialization-ready trace for observability or offline evaluation."""

    return [
        {
            "stage": attempt.stage,
            "query": attempt.query,
            "candidate_ids": attempt.candidate_ids,
            "grade": attempt.grade.value,
            "score": attempt.score,
            "latency_ms": attempt.latency_ms,
            "reason": attempt.reason,
        }
        for attempt in result.attempts
    ]
