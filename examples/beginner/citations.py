"""Structured citations, abstention, and simple evidence-policy checks."""

from __future__ import annotations

from dataclasses import dataclass

from .first_local_rag import Chunk, retrieve


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    source: str
    score: float


@dataclass(frozen=True)
class CitedAnswer:
    text: str
    citations: tuple[Citation, ...]
    abstained: bool
    reason: str


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


def answer_with_citations(query: str, chunks: list[Chunk], *, top_k: int = 3, min_score: float = 0.2, policy: AbstentionPolicy | None = None) -> CitedAnswer:
    policy = policy or AbstentionPolicy(min_score=min_score)
    results = retrieve(query, chunks, top_k=top_k)
    if not results or results[0][1] < policy.min_score:
        return CitedAnswer("I don't have enough evidence in the indexed documents to answer that.", (), True, "insufficient-evidence")
    margin = results[0][1] - (results[1][1] if len(results) > 1 else 0.0)
    if margin < policy.min_margin:
        return CitedAnswer("I found competing evidence but cannot answer reliably from this corpus.", (), True, "ambiguous-evidence")
    citations = tuple(Citation(chunk.chunk_id, chunk.source, score) for chunk, score in results)
    if policy.require_distinct_sources and len({citation.source for citation in citations}) < 2:
        return CitedAnswer("I need corroborating evidence from more than one source before answering.", (), True, "insufficient-source-diversity")
    evidence = " ".join(chunk.text for chunk, _ in results)
    return CitedAnswer(evidence, citations, False, "grounded-evidence")


def render_markdown(answer: CitedAnswer) -> str:
    if answer.abstained:
        return f"{answer.text}\n\nReason: `{answer.reason}`"
    sources = ", ".join(f"[{citation.chunk_id}]({citation.source})" for citation in answer.citations)
    return f"{answer.text}\n\nSources: {sources}"


def citations_are_retrieved(answer: CitedAnswer, chunks: list[Chunk]) -> bool:
    known_ids = {chunk.chunk_id for chunk in chunks}
    return all(citation.chunk_id in known_ids for citation in answer.citations)


def audit_answer(answer: CitedAnswer, chunks: list[Chunk]) -> CitationAudit:
    """Check provenance invariants separately from answer presentation."""

    retrieved = citations_are_retrieved(answer, chunks)
    sources = {citation.source for citation in answer.citations}
    scores = [citation.score for citation in answer.citations]
    top_score = scores[0] if scores else 0.0
    margin = top_score - (scores[1] if len(scores) > 1 else 0.0)
    return CitationAudit(
        citations_retrieved=retrieved,
        sources_distinct=len(sources) >= 2,
        top_score=top_score,
        score_margin=margin,
        decision="abstain" if answer.abstained else "answer",
    )


if __name__ == "__main__":
    from pathlib import Path

    root = Path(__file__).parents[1] / "data" / "beginner-docs"
    chunks = []
    from .first_local_rag import load_chunks

    chunks = load_chunks(root)
    print(render_markdown(answer_with_citations("What is an abstention?", chunks)))
