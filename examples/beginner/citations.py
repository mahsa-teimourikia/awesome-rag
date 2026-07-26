"""Structured citations and abstention for the beginner RAG path."""

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


def answer_with_citations(query: str, chunks: list[Chunk], *, top_k: int = 3, min_score: float = 0.2) -> CitedAnswer:
    results = retrieve(query, chunks, top_k=top_k)
    if not results or results[0][1] < min_score:
        return CitedAnswer("I don't have enough evidence in the indexed documents to answer that.", (), True, "insufficient-evidence")
    citations = tuple(Citation(chunk.chunk_id, chunk.source, score) for chunk, score in results)
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


if __name__ == "__main__":
    from pathlib import Path

    root = Path(__file__).parents[1] / "data" / "beginner-docs"
    chunks = []
    from .first_local_rag import load_chunks

    chunks = load_chunks(root)
    print(render_markdown(answer_with_citations("What is an abstention?", chunks)))
