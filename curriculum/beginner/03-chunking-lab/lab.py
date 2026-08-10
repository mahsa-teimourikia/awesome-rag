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
    parent_id: str | None = None


@dataclass(frozen=True)
class CoverageResult:
    """A simple evidence-boundary check for one required set of terms."""

    required_terms: tuple[str, ...]
    supporting_chunk_ids: tuple[str, ...]
    missing_terms: tuple[str, ...]

    @property
    def covered(self) -> bool:
        return bool(self.supporting_chunk_ids)


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


def by_heading_bounded(markdown: str, source: str, *, max_characters: int = 240, overlap: int = 30) -> list[Chunk]:
    """Respect headings, then bound long sections with deterministic windows.

    This parent/child pattern is useful for manuals: a child is small enough to
    retrieve while its ``section`` and ``parent_id`` retain the human-readable
    context needed for a citation or later parent-document expansion.
    """

    if max_characters <= 0 or overlap < 0 or overlap >= max_characters:
        raise ValueError("max_characters must be positive and overlap must be between 0 and max_characters")
    bounded: list[Chunk] = []
    for parent in by_heading(markdown, source):
        parent_id = parent.chunk_id
        if len(parent.text) <= max_characters:
            bounded.append(Chunk(f"{parent_id}-1", parent.text, source, parent.section, parent_id))
            continue
        for index, child in enumerate(fixed_size(parent.text, source, max_characters, overlap), start=1):
            bounded.append(Chunk(f"{parent_id}-{index}", child.text, source, parent.section, parent_id))
    return bounded


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
        "chunks_with_parent_ids": sum(chunk.parent_id is not None for chunk in chunks),
        "total_characters": sum(lengths),
        "adjacent_overlap_characters": adjacent_overlap_characters(chunks),
    }


def answer_coverage(chunks: list[Chunk], required_terms: set[str]) -> list[str]:
    """Identify chunks that contain all required answer terms for a question."""

    normalized = {term.lower() for term in required_terms}
    return [chunk.chunk_id for chunk in chunks if normalized <= set(re.findall(r"[a-z0-9]+", chunk.text.lower()))]


def coverage_result(chunks: list[Chunk], required_terms: set[str]) -> CoverageResult:
    """State which evidence terms are not co-located in a retrieved unit."""

    normalized = tuple(sorted(term.lower() for term in required_terms))
    supporting = tuple(answer_coverage(chunks, set(normalized)))
    present = set().union(*(set(re.findall(r"[a-z0-9]+", chunk.text.lower())) for chunk in chunks)) if chunks else set()
    return CoverageResult(normalized, supporting, tuple(term for term in normalized if term not in present))


def adjacent_overlap_characters(chunks: list[Chunk]) -> int:
    """Approximate duplicated adjacent text; a visible cost of overlap."""

    overlap = 0
    for left, right in zip(chunks, chunks[1:]):
        limit = min(len(left.text), len(right.text))
        for width in range(limit, 0, -1):
            if left.text[-width:] == right.text[:width]:
                overlap += width
                break
    return overlap


def scorecard(chunks: list[Chunk], questions: dict[str, set[str]]) -> dict[str, object]:
    """Combine size diagnostics and direct evidence coverage for an experiment."""

    diagnostics = describe_chunks(chunks)
    coverage = {question: coverage_result(chunks, terms) for question, terms in questions.items()}
    diagnostics["covered_questions"] = sum(result.covered for result in coverage.values())
    diagnostics["question_count"] = len(coverage)
    diagnostics["coverage"] = coverage
    return diagnostics


if __name__ == "__main__":
    sample = "# Intro\n\nRAG retrieves evidence.\n\n## Evaluation\n\nMeasure retrieval and answer quality separately."
    for strategy, chunks in (("fixed", fixed_size(sample, "sample", 45, 8)), ("heading", by_heading(sample, "sample"))):
        print(f"{strategy}: {len(chunks)} chunks")
        for chunk in chunks:
            print(f"  {chunk.chunk_id} [{chunk.section or 'n/a'}] {chunk.text}")
