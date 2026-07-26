"""A dependency-free RAG baseline for the beginner curriculum.

This intentionally uses lexical retrieval so the learner can inspect every step.
Later lessons replace `retrieve` with dense, hybrid, and reranked retrieval.
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


def tokenize(text: str) -> set[str]:
    return set(TOKEN.findall(text.lower())) - STOPWORDS


def load_chunks(directory: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        paragraphs = [p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for index, paragraph in enumerate(paragraphs, start=1):
            chunks.append(Chunk(f"{path.stem}-{index}", paragraph, path.name))
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


def answer(query: str, chunks: list[Chunk], min_score: float = 0.2) -> str:
    results = retrieve(query, chunks)
    if not results or results[0][1] < min_score:
        return "I don't have enough evidence in the indexed documents to answer that."
    evidence = " ".join(chunk.text for chunk, _ in results)
    citations = ", ".join(f"[{chunk.chunk_id}]({chunk.source})" for chunk, _ in results)
    return f"Evidence found: {evidence}\n\nSources: {citations}"


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
