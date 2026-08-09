"""Compare chunking choices using deterministic, inspectable document units."""

from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    section: str | None = None


def fixed_size(text: str, source: str, size: int = 240, overlap: int = 40) -> list[Chunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size must be positive and overlap must be between 0 and size")
    chunks = []
    start = 0
    index = 1
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(Chunk(f"{source}-fixed-{index}", text[start:end].strip(), source))
        if end == len(text):
            break
        start = end - overlap
        index += 1
    return [chunk for chunk in chunks if chunk.text]


def by_heading(markdown: str, source: str) -> list[Chunk]:
    sections: list[tuple[str, list[str]]] = []
    heading = "Document"
    body: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^#{1,3}\s+(.+)$", line.strip())
        if match:
            if body:
                sections.append((heading, body))
                body = []
            heading = match.group(1).strip()
        elif line.strip():
            body.append(line.strip())
    if body:
        sections.append((heading, body))
    return [Chunk(f"{source}-section-{index}", " ".join(body), source, section) for index, (section, body) in enumerate(sections, 1)]


def by_sentence_window(text: str, source: str, *, sentences_per_chunk: int = 2, overlap_sentences: int = 1) -> list[Chunk]:
    """Chunk at sentence boundaries so a fragment does not start mid-sentence."""

    if sentences_per_chunk <= 0 or overlap_sentences < 0 or overlap_sentences >= sentences_per_chunk:
        raise ValueError("sentences_per_chunk must be positive and overlap must be smaller")
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]
    chunks: list[Chunk] = []
    step = sentences_per_chunk - overlap_sentences
    for index, start in enumerate(range(0, len(sentences), step), start=1):
        window = sentences[start : start + sentences_per_chunk]
        if not window:
            break
        chunks.append(Chunk(f"{source}-sentence-{index}", " ".join(window), source, "Sentence window"))
        if start + sentences_per_chunk >= len(sentences):
            break
    return chunks


def describe_chunks(chunks: list[Chunk]) -> dict[str, float | int]:
    """Return lightweight diagnostics before comparing retrieval behavior."""

    lengths = [len(chunk.text) for chunk in chunks]
    return {
        "count": len(chunks),
        "min_characters": min(lengths, default=0),
        "max_characters": max(lengths, default=0),
        "mean_characters": round(mean(lengths), 1) if lengths else 0.0,
        "chunks_with_sections": sum(chunk.section is not None for chunk in chunks),
    }


def answer_coverage(chunks: list[Chunk], required_terms: set[str]) -> list[str]:
    """Identify chunks that contain all required answer terms for a question."""

    normalized = {term.lower() for term in required_terms}
    return [chunk.chunk_id for chunk in chunks if normalized <= set(re.findall(r"[a-z0-9]+", chunk.text.lower()))]


if __name__ == "__main__":
    sample = "# Intro\n\nRAG retrieves evidence.\n\n## Evaluation\n\nMeasure retrieval and answer quality separately."
    for strategy, chunks in (("fixed", fixed_size(sample, "sample", 45, 8)), ("heading", by_heading(sample, "sample"))):
        print(f"{strategy}: {len(chunks)} chunks")
        for chunk in chunks:
            print(f"  {chunk.chunk_id} [{chunk.section or 'n/a'}] {chunk.text}")
