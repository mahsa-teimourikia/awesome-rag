"""Evidence-first research synthesis primitives for deterministic RAG labs."""

from __future__ import annotations

from dataclasses import dataclass

from src.rag_core.retrieval import BM25, Document


@dataclass(frozen=True)
class Claim:
    text: str
    source_ids: tuple[str, ...]
    claim_type: str = "finding"
    confidence: str = "moderate"
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceTrace:
    question: str
    queries: tuple[str, ...]
    source_ids: tuple[str, ...]


def research_queries(question: str) -> list[str]:
    """Decompose a question into bounded, reviewable evidence views."""

    question = " ".join(question.split())
    if not question:
        return []
    return [
        question,
        f"evidence and findings about {question}",
        f"limitations and counterarguments for {question}",
        f"operational trade-offs and failure modes for {question}",
    ]


def retrieve_unique(question: str, documents: list[Document], top_k: int = 3) -> list[Document]:
    """Retrieve once per question view and deduplicate by stable source ID."""

    unique: dict[str, Document] = {}
    index = BM25(documents)
    for query in research_queries(question):
        for document, _ in index.search(query, top_k=top_k):
            unique.setdefault(document.doc_id, document)
    return list(unique.values())


def trace_evidence(question: str, documents: list[Document], top_k: int = 3) -> EvidenceTrace:
    evidence = retrieve_unique(question, documents, top_k)
    return EvidenceTrace(question, tuple(research_queries(question)), tuple(document.doc_id for document in evidence))


def classify_claim(text: str) -> tuple[str, str]:
    lowered = text.lower()
    if any(term in lowered for term in ("limitation", "risk", "cost", "may miss", "however", "cannot")):
        return "limitation", "moderate"
    if any(term in lowered for term in ("unknown", "open question", "insufficient")):
        return "open-question", "low"
    return "finding", "moderate"


def make_claims(question: str, documents: list[Document]) -> list[Claim]:
    """Create citation-bound claim candidates; review/merge them before prose."""

    claims = []
    for document in retrieve_unique(question, documents):
        claim_type, confidence = classify_claim(document.text)
        claims.append(Claim(document.text, (document.doc_id,), claim_type, confidence))
    return claims


def synthesis_outline(claims: list[Claim]) -> dict[str, list[Claim]]:
    """Keep findings, limitations, and unknowns separate until final writing."""

    return {kind: [claim for claim in claims if claim.claim_type == kind] for kind in ("finding", "limitation", "open-question")}


def citation_coverage(claims: list[Claim]) -> float:
    if not claims:
        return 1.0
    return sum(bool(claim.source_ids) for claim in claims) / len(claims)
