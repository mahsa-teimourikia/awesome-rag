"""Structured citations, abstention, and simple evidence-policy checks."""

from __future__ import annotations

from dataclasses import dataclass
import re

from src.rag_core.lesson_loader import load_lesson_module


_first_local_rag = load_lesson_module("curriculum/beginner/02-first-local-rag/lab.py")
Chunk = _first_local_rag.Chunk
retrieve = _first_local_rag.retrieve


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    source: str
    score: float
    section: str | None = None


@dataclass(frozen=True)
class Claim:
    """A user-visible assertion linked to the evidence IDs that support it."""

    claim_id: str
    text: str
    citation_ids: tuple[str, ...]


@dataclass(frozen=True)
class CitedAnswer:
    text: str
    citations: tuple[Citation, ...]
    abstained: bool
    reason: str
    claims: tuple[Claim, ...] = ()


@dataclass(frozen=True)
class AbstentionPolicy:
    min_score: float = 0.2
    min_margin: float = 0.0
    require_distinct_sources: bool = False


@dataclass(frozen=True)
class CitationAudit:
    citations_retrieved: bool
    sources_distinct: bool
    top_score: float
    score_margin: float
    decision: str
    claims_have_known_citations: bool
    lexically_supported_claim_ids: tuple[str, ...]
    unsupported_claim_ids: tuple[str, ...]


def answer_with_citations(
    query: str,
    chunks: list[Chunk],
    *,
    top_k: int = 3,
    min_score: float = 0.2,
    policy: AbstentionPolicy | None = None,
    allowed_chunk_ids: set[str] | None = None,
) -> CitedAnswer:
    """Return a deterministic evidence answer with an explicit no-answer path.

    ``allowed_chunk_ids`` is a teaching stand-in for a retrieval-time ACL or
    tenant filter. It is applied before ranking; a real system must not retrieve
    restricted text and then ask a model to ignore it.
    """

    policy = policy or AbstentionPolicy(min_score=min_score)
    visible_chunks = chunks if allowed_chunk_ids is None else [chunk for chunk in chunks if chunk.chunk_id in allowed_chunk_ids]
    results = retrieve(query, visible_chunks, top_k=top_k)
    if not results or results[0][1] < policy.min_score:
        return CitedAnswer("I don't have enough evidence in the indexed documents to answer that.", (), True, "insufficient-evidence")
    margin = results[0][1] - (results[1][1] if len(results) > 1 else 0.0)
    if margin < policy.min_margin:
        return CitedAnswer("I found competing evidence but cannot answer reliably from this corpus.", (), True, "ambiguous-evidence")
    citations = tuple(Citation(chunk.chunk_id, chunk.source, score, chunk.section) for chunk, score in results)
    if policy.require_distinct_sources and len({citation.source for citation in citations}) < 2:
        return CitedAnswer("I need corroborating evidence from more than one source before answering.", (), True, "insufficient-source-diversity")
    evidence = " ".join(chunk.text for chunk, _ in results)
    claims = (Claim("claim-1", evidence, tuple(citation.chunk_id for citation in citations)),)
    return CitedAnswer(evidence, citations, False, "grounded-evidence", claims)


def render_markdown(answer: CitedAnswer) -> str:
    if answer.abstained:
        return f"{answer.text}\n\nReason: `{answer.reason}`"
    sources = ", ".join(f"[{citation.chunk_id}]({citation.source})" for citation in answer.citations)
    return f"{answer.text}\n\nSources: {sources}"


def citations_are_retrieved(answer: CitedAnswer, chunks: list[Chunk]) -> bool:
    known_ids = {chunk.chunk_id for chunk in chunks}
    return all(citation.chunk_id in known_ids for citation in answer.citations)


def claims_have_known_citations(answer: CitedAnswer) -> bool:
    """Ensure claims cite IDs present in the answer's own evidence set."""

    cited_ids = {citation.chunk_id for citation in answer.citations}
    return all(claim.citation_ids and set(claim.citation_ids) <= cited_ids for claim in answer.claims)


def audit_claim_support(answer: CitedAnswer, chunks: list[Chunk]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Run a transparent lexical support check for a claim/citation mapping.

    It is deliberately not a proof of entailment. It catches obvious mistakes
    such as a claim citing an unrelated source and gives learners a reason to
    later add human review or an evaluated entailment/faithfulness judge.
    """

    by_id = {chunk.chunk_id: chunk for chunk in chunks}
    supported: list[str] = []
    unsupported: list[str] = []
    for claim in answer.claims:
        cited_text = " ".join(by_id[identifier].text for identifier in claim.citation_ids if identifier in by_id)
        claim_terms = set(re.findall(r"[a-z0-9]+", claim.text.lower())) - {"a", "an", "and", "the", "is", "are", "for", "to", "of", "in"}
        evidence_terms = set(re.findall(r"[a-z0-9]+", cited_text.lower()))
        if claim.citation_ids and claim_terms and claim_terms <= evidence_terms:
            supported.append(claim.claim_id)
        else:
            unsupported.append(claim.claim_id)
    return tuple(supported), tuple(unsupported)


def audit_answer(answer: CitedAnswer, chunks: list[Chunk]) -> CitationAudit:
    """Check provenance invariants separately from answer presentation."""

    retrieved = citations_are_retrieved(answer, chunks)
    sources = {citation.source for citation in answer.citations}
    scores = [citation.score for citation in answer.citations]
    top_score = scores[0] if scores else 0.0
    margin = top_score - (scores[1] if len(scores) > 1 else 0.0)
    lexically_supported, unsupported = audit_claim_support(answer, chunks)
    known_claim_citations = claims_have_known_citations(answer)
    return CitationAudit(
        citations_retrieved=retrieved,
        sources_distinct=len(sources) >= 2,
        top_score=top_score,
        score_margin=margin,
        decision="abstain" if answer.abstained else "answer",
        claims_have_known_citations=known_claim_citations,
        lexically_supported_claim_ids=lexically_supported,
        unsupported_claim_ids=unsupported,
    )


if __name__ == "__main__":
    from pathlib import Path

    root = Path(__file__).parents[1] / "data" / "beginner-docs"
    chunks = []
    from .first_local_rag import load_chunks

    chunks = load_chunks(root)
    print(render_markdown(answer_with_citations("What is an abstention?", chunks)))
