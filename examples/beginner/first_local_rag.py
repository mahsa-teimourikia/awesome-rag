"""An inspectable, dependency-free RAG baseline for the beginner curriculum.

The fictional Harborline Support team needs answers over a small, changing
operations handbook.  This deliberately uses lexical retrieval: learners can
inspect every token, score, source ID, and abstention decision before later
lessons introduce embeddings, vector databases, and rerankers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = {"a", "an", "and", "are", "for", "is", "of", "the", "to", "what", "when", "in"}


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    section: str | None = None
    ordinal: int = 0


@dataclass(frozen=True)
class RetrievalHit:
    """A transparent first-stage retrieval result.

    Keeping match terms and rank alongside the score lets a learner debug a
    surprising result instead of treating retrieval as a black box.
    """

    chunk: Chunk
    score: float
    matched_terms: tuple[str, ...]
    rank: int


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    relevant_ids: tuple[str, ...]
    should_abstain: bool = False


def tokenize(text: str) -> set[str]:
    return set(TOKEN.findall(text.lower())) - STOPWORDS


def load_chunks(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        section = "Document"
        paragraphs = [p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for index, paragraph in enumerate(paragraphs, start=1):
            if paragraph.startswith("#"):
                section = paragraph.lstrip("#").strip()
            chunks.append(Chunk(f"{path.stem}-{index}", paragraph, path.name, section, index))
    return chunks


def retrieve(query: str, chunks: list[Chunk], top_k: int = 3) -> list[tuple[Chunk, float]]:
    query_terms = tokenize(query)
    scored = []
    for chunk in chunks:
        terms = tokenize(chunk.text)
        overlap = query_terms & terms
        score = len(overlap) / max(len(query_terms), 1)
        if score:
            scored.append((chunk, score))
    return sorted(scored, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]


def retrieve_with_trace(query: str, chunks: list[Chunk], top_k: int = 3) -> list[RetrievalHit]:
    """Return ranked evidence plus the exact lexical matches that caused it."""

    query_terms = tokenize(query)
    hits = []
    for rank, (chunk, score) in enumerate(retrieve(query, chunks, top_k), start=1):
        matched_terms = tuple(sorted(query_terms & tokenize(chunk.text)))
        hits.append(RetrievalHit(chunk, score, matched_terms, rank))
    return hits


def build_context(hits: list[RetrievalHit], *, max_characters: int = 900) -> str:
    """Build a bounded, labelled context window for a generator or template."""

    parts: list[str] = []
    used = 0
    for hit in hits:
        labelled = f"[{hit.chunk.chunk_id} | {hit.chunk.source}] {hit.chunk.text}"
        if parts and used + len(labelled) > max_characters:
            break
        parts.append(labelled)
        used += len(labelled)
    return "\n\n".join(parts)


def answer(query: str, chunks: list[Chunk], min_score: float = 0.2) -> str:
    results = retrieve(query, chunks)
    if not results or results[0][1] < min_score:
        return "I don't have enough evidence in the indexed documents to answer that."
    evidence = " ".join(chunk.text for chunk, _ in results)
    citations = ", ".join(f"[{chunk.chunk_id}]({chunk.source})" for chunk, _ in results)
    return f"Evidence found: {evidence}\n\nSources: {citations}"


def evaluate_baseline(cases: list[EvaluationCase], chunks: list[Chunk], *, top_k: int = 3, min_score: float = 0.2) -> list[dict[str, object]]:
    """Evaluate retrieval and abstention separately on a small golden set."""

    report: list[dict[str, object]] = []
    for case in cases:
        hits = retrieve_with_trace(case.question, chunks, top_k)
        retrieved_ids = tuple(hit.chunk.chunk_id for hit in hits)
        abstained = not hits or hits[0].score < min_score
        relevant = set(case.relevant_ids)
        report.append({
            "question": case.question,
            "retrieved_ids": retrieved_ids,
            "retrieval_hit": bool(relevant & set(retrieved_ids)),
            "abstained": abstained,
            "abstention_correct": abstained == case.should_abstain,
            "top_score": hits[0].score if hits else 0.0,
        })
    return report


def main() -> None:
    root = Path(__file__).parents[1] / "data" / "beginner-docs"
    chunks = load_chunks(root)
    print("Indexed", len(chunks), "chunks. Ask about the documents; Ctrl-D to exit.")
    try:
        while query := input("\nQuestion> ").strip():
            print(answer(query, chunks))
    except EOFError:
        print()


if __name__ == "__main__":
    main()
