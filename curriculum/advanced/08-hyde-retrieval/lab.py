"""Credential-free HyDE retrieval lab.

The production HyDE pattern uses an instruction-following generator and a dense
document encoder. This module deliberately substitutes a deterministic
hypothesis generator and a transparent TF-IDF vectorizer so learners can inspect
the representation change, failure modes, routing, and evaluation without an
API key. Hypothetical text is used only as a search representation; every
returned evidence item is a real document from ``CORPUS``.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log, sqrt
import re
from typing import Callable, Iterable, Literal, Sequence


Strategy = Literal["original", "hyde", "hyde_plus_original", "conditional"]


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    tenant: str = "harborline"
    genre: str = "technical_documentation"


@dataclass(frozen=True)
class RankedDocument:
    document: Document
    score: float
    rank: int


@dataclass(frozen=True)
class RetrievalTrace:
    query: str
    strategy: str
    hypotheses: tuple[str, ...]
    results: tuple[RankedDocument, ...]

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        """IDs of real corpus documents; hypotheses never enter this ledger."""

        return tuple(item.document.doc_id for item in self.results)


@dataclass(frozen=True)
class EvaluationCase:
    query: str
    relevant_ids: frozenset[str]
    query_type: str


@dataclass(frozen=True)
class EvaluationRow:
    query: str
    query_type: str
    strategy: str
    retrieved_ids: tuple[str, ...]
    recall_at_k: float
    reciprocal_rank: float
    hypothesis_count: int


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "or",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "why",
    "with",
}


CORPUS: tuple[Document, ...] = (
    Document(
        "application-logging",
        "Application logging windows",
        "Application logging records are archived during overnight maintenance windows.",
    ),
    Document(
        "auth-token-lifecycle",
        "OIDC token lifecycle",
        "OIDC refresh token invalidation occurs after prolonged inactivity. Session renewal requires a fresh identity-provider authentication.",
    ),
    Document(
        "dependent-care-leave",
        "Dependent-care leave",
        "Employees looking after a parent may request paid or unpaid dependent-care leave.",
        genre="policy",
    ),
    Document(
        "cross-border-work",
        "Cross-border temporary work",
        "Cross-border temporary remote work arrangements require mobility, tax, payroll, immigration, and data-access review.",
        genre="policy",
    ),
    Document(
        "cloud-invoices",
        "Cloud invoice access",
        "Billing contacts can download a cloud service invoice from the finance portal.",
    ),
    Document(
        "spend-drivers",
        "Unexpected spend drivers",
        "Unexpected monthly spend can result from compute autoscaling, data egress charges, storage growth, or reduced reserved-capacity coverage.",
    ),
    Document(
        "pharma-safety",
        "Experimental compound safety",
        "A pharmaceutical compound requires toxicity screening, dosage review, and clinical safety monitoring.",
    ),
    Document(
        "zx-47-controller",
        "ZX-47 controller",
        "ZX-47 is a proprietary hardware controller used for cold-storage telemetry.",
    ),
    Document(
        "hr-427",
        "Policy HR-427",
        "HR-427 requires manager approval for domestic remote-work equipment reimbursement.",
        genre="policy",
    ),
    Document(
        "q3-margin",
        "Q3 2025 operating margin",
        "For Q3 2025, operating margin was 18.4 percent under the approved finance definition.",
        genre="financial_report",
    ),
    Document(
        "tenant-b-secret",
        "Tenant B identity procedure",
        "OIDC refresh token invalidation for Tenant B uses a confidential recovery process.",
        tenant="tenant-b",
    ),
)


EVALUATION_CASES: tuple[EvaluationCase, ...] = (
    EvaluationCase(
        "Why does the app log me out overnight?",
        frozenset({"auth-token-lifecycle"}),
        "semantic_gap",
    ),
    EvaluationCase(
        "Can I look after my parent while staying overseas?",
        frozenset({"cross-border-work"}),
        "semantic_gap",
    ),
    EvaluationCase(
        "Why is my cloud bill suddenly higher?",
        frozenset({"spend-drivers"}),
        "semantic_gap",
    ),
    EvaluationCase(
        "What is ZX-47?",
        frozenset({"zx-47-controller"}),
        "exact_identifier",
    ),
    EvaluationCase(
        "What does HR-427 require?",
        frozenset({"hr-427"}),
        "exact_identifier",
    ),
    EvaluationCase(
        "What was operating margin in Q3 2025?",
        frozenset({"q3-margin"}),
        "numerical_lookup",
    ),
)


def tokenize(text: str) -> list[str]:
    """Return normalized terms while retaining identifiers such as ``ZX-47``."""

    terms = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return [term for term in terms if term not in STOPWORDS]


class TfidfIndex:
    """Small exact vector index used as an inspectable encoder/search adapter."""

    def __init__(self, documents: Sequence[Document]):
        if not documents:
            raise ValueError("documents must not be empty")
        self.documents = tuple(documents)
        document_frequency: Counter[str] = Counter()
        for document in self.documents:
            document_frequency.update(set(tokenize(f"{document.title} {document.text}")))
        count = len(self.documents)
        self.idf = {
            term: log((1 + count) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }
        self._vectors = {
            document.doc_id: self.encode(f"{document.title} {document.text}")
            for document in self.documents
        }

    def encode(self, text: str) -> dict[str, float]:
        counts = Counter(tokenize(text))
        weighted = {
            term: frequency * self.idf.get(term, 1.0)
            for term, frequency in counts.items()
        }
        norm = sqrt(sum(value * value for value in weighted.values()))
        return {term: value / norm for term, value in weighted.items()} if norm else {}

    @staticmethod
    def cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(term, 0.0) for term, value in left.items())

    def search(self, text: str, *, top_k: int = 5) -> tuple[RankedDocument, ...]:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        query_vector = self.encode(text)
        scored = [
            (self.cosine(query_vector, self._vectors[document.doc_id]), document)
            for document in self.documents
        ]
        scored.sort(key=lambda item: (-item[0], item[1].doc_id))
        return tuple(
            RankedDocument(document=document, score=score, rank=rank)
            for rank, (score, document) in enumerate(scored[:top_k], start=1)
        )


def authorized_documents(
    documents: Iterable[Document], tenant: str
) -> tuple[Document, ...]:
    """Apply authorization before either original-query or HyDE retrieval."""

    return tuple(document for document in documents if document.tenant == tenant)


def generate_hypotheses(query: str, *, count: int = 1) -> tuple[str, ...]:
    """Return bounded, corpus-shaped fixtures in place of a live LLM call.

    The intentionally incorrect ZX-47 branch makes hypothesis drift observable.
    A production implementation would replace this function with a constrained
    generator and keep the remaining retrieval/evaluation contract.
    """

    if count < 1 or count > 3:
        raise ValueError("count must be between 1 and 3")
    lowered = query.lower()
    if "zx-47" in lowered:
        candidates = (
            "An experimental pharmaceutical compound requires dosage review, toxicity screening, and clinical safety monitoring.",
            "A drug-development monograph describes an investigational compound and adverse-event controls.",
        )
    elif "log" in lowered and "overnight" in lowered:
        candidates = (
            "OIDC refresh token invalidation after prolonged inactivity ends a session and requires fresh identity-provider authentication.",
            "A token lifecycle policy explains session renewal, idle expiry, and refresh credential invalidation.",
        )
    elif "parent" in lowered or "overseas" in lowered:
        candidates = (
            "Cross-border temporary remote work requires mobility, tax, payroll, immigration, and data-access review.",
            "An international work policy describes approval for employees working temporarily from another country.",
        )
    elif "bill" in lowered or "spend" in lowered:
        candidates = (
            "Unexpected monthly spend can result from compute autoscaling, data egress charges, storage growth, and reduced reserved-capacity coverage.",
            "A cloud cost guide explains utilization growth, transfer fees, storage, and commitment coverage.",
        )
    else:
        candidates = (
            f"A concise technical document that addresses this information need: {query}",
            f"An enterprise knowledge article containing terminology relevant to: {query}",
        )
    repeated = (candidates * 2)[:count]
    return tuple(repeated)


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[RankedDocument]], *, top_k: int, constant: int = 60
) -> tuple[RankedDocument, ...]:
    """Fuse result lists without assuming their raw scores are comparable."""

    scores: defaultdict[str, float] = defaultdict(float)
    documents: dict[str, Document] = {}
    for ranking in rankings:
        for item in ranking:
            scores[item.document.doc_id] += 1 / (constant + item.rank)
            documents[item.document.doc_id] = item.document
    ordered = sorted(scores, key=lambda doc_id: (-scores[doc_id], doc_id))[:top_k]
    return tuple(
        RankedDocument(documents[doc_id], scores[doc_id], rank)
        for rank, doc_id in enumerate(ordered, start=1)
    )


def route_query(query: str) -> Literal["original", "hyde"]:
    """Choose HyDE only for a narrow, observable semantic-gap slice."""

    if re.search(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b", query):
        return "original"
    if re.search(r"\b(?:q[1-4]|fy)\s*20\d{2}\b", query, re.IGNORECASE):
        return "original"
    lowered = query.lower()
    semantic_gap_signals = ("why", "how", "overnight", "overseas", "suddenly")
    return "hyde" if any(signal in lowered for signal in semantic_gap_signals) else "original"


def retrieve(
    query: str,
    *,
    strategy: Strategy = "original",
    top_k: int = 5,
    tenant: str = "harborline",
    hypothesis_count: int = 1,
    generator: Callable[..., tuple[str, ...]] = generate_hypotheses,
) -> RetrievalTrace:
    """Run a retrieval strategy and return an auditable search trace."""

    index = TfidfIndex(authorized_documents(CORPUS, tenant))
    resolved = route_query(query) if strategy == "conditional" else strategy
    if resolved == "original":
        return RetrievalTrace(query, "original", (), index.search(query, top_k=top_k))

    hypotheses = generator(query, count=hypothesis_count)
    hyde_rankings = [index.search(text, top_k=top_k) for text in hypotheses]
    if resolved == "hyde_plus_original":
        hyde_rankings.insert(0, index.search(query, top_k=top_k))
    results = reciprocal_rank_fusion(hyde_rankings, top_k=top_k)
    return RetrievalTrace(query, resolved, hypotheses, results)


def recall_at_k(retrieved_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    if not relevant_ids:
        return 1.0
    return len(set(retrieved_ids) & relevant_ids) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: Sequence[str], relevant_ids: frozenset[str]) -> float:
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1 / rank
    return 0.0


def evaluate(
    strategy: Strategy,
    *,
    cases: Sequence[EvaluationCase] = EVALUATION_CASES,
    top_k: int = 1,
    hypothesis_count: int = 1,
) -> tuple[EvaluationRow, ...]:
    rows = []
    for case in cases:
        trace = retrieve(
            case.query,
            strategy=strategy,
            top_k=top_k,
            hypothesis_count=hypothesis_count,
        )
        rows.append(
            EvaluationRow(
                query=case.query,
                query_type=case.query_type,
                strategy=trace.strategy,
                retrieved_ids=trace.evidence_ids,
                recall_at_k=recall_at_k(trace.evidence_ids, case.relevant_ids),
                reciprocal_rank=reciprocal_rank(trace.evidence_ids, case.relevant_ids),
                hypothesis_count=len(trace.hypotheses),
            )
        )
    return tuple(rows)


def summarize(rows: Sequence[EvaluationRow]) -> dict[str, float]:
    if not rows:
        raise ValueError("rows must not be empty")
    return {
        "mean_recall_at_k": sum(row.recall_at_k for row in rows) / len(rows),
        "mrr": sum(row.reciprocal_rank for row in rows) / len(rows),
        "total_hypotheses": float(sum(row.hypothesis_count for row in rows)),
    }


if __name__ == "__main__":
    for name in ("original", "hyde", "hyde_plus_original", "conditional"):
        report = summarize(evaluate(name, top_k=1))
        print(name, report)
