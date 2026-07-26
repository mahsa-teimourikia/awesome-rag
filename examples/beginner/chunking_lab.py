"""Compare fixed-size and heading-aware chunking without external dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass


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


if __name__ == "__main__":
    sample = "# Intro\n\nRAG retrieves evidence.\n\n## Evaluation\n\nMeasure retrieval and answer quality separately."
    for strategy, chunks in (("fixed", fixed_size(sample, "sample", 45, 8)), ("heading", by_heading(sample, "sample"))):
        print(f"{strategy}: {len(chunks)} chunks")
        for chunk in chunks:
            print(f"  {chunk.chunk_id} [{chunk.section or 'n/a'}] {chunk.text}")
