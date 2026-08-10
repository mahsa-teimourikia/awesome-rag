"""An inspectable, dependency-free RAG baseline for the beginner curriculum.

The fictional Harborline Support team needs answers over a small, changing
operations handbook.  This deliberately uses lexical retrieval: learners can
inspect every token, score, source ID, and abstention decision before later
lessons introduce embeddings, vector databases, and rerankers.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


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


@dataclass(frozen=True)
class CorpusAudit:
    """A minimal ingestion-quality report for a local document collection."""

    document_count: int
    chunk_count: int
    duplicate_chunk_ids: tuple[str, ...]
    empty_chunk_ids: tuple[str, ...]
    sources_without_sections: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not (self.duplicate_chunk_ids or self.empty_chunk_ids)


@dataclass(frozen=True)
class LocalRAGResult:
    """The end-to-end, auditable result of a deterministic local RAG run."""

    decision: Literal["answer", "abstain"]
    answer: str
    query: str
    hits: tuple[RetrievalHit, ...]
    context: str
    citations: tuple[str, ...]
    retrieval_threshold: float
    context_budget: int


@dataclass(frozen=True)
class ContextPack:
    """Bounded evidence with retained provenance for an answer component."""

    text: str
    citations: tuple[str, ...]
    retained_ids: tuple[str, ...]
    truncated: bool


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


def audit_corpus(chunks: list[Chunk]) -> CorpusAudit:
    """Make basic ingestion defects visible before retrieval is trusted."""

    identifiers = [chunk.chunk_id for chunk in chunks]
    duplicate_ids = tuple(sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1}))
    empty_ids = tuple(chunk.chunk_id for chunk in chunks if not tokenize(chunk.text))
    source_sections: dict[str, set[str | None]] = {}
    for chunk in chunks:
        source_sections.setdefault(chunk.source, set()).add(chunk.section)
    missing_sections = tuple(sorted(source for source, sections in source_sections.items() if not any(sections)))
    return CorpusAudit(
        document_count=len(source_sections),
        chunk_count=len(chunks),
        duplicate_chunk_ids=duplicate_ids,
        empty_chunk_ids=empty_ids,
        sources_without_sections=missing_sections,
    )


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


def retrieve_bm25(
    query: str,
    chunks: list[Chunk],
    *,
    top_k: int = 3,
    k1: float = 1.2,
    b: float = 0.75,
) -> list[RetrievalHit]:
    """A transparent BM25 comparison ranker, not a production search index."""

    query_terms = tokenize(query)
    document_terms = [TOKEN.findall(chunk.text.lower()) for chunk in chunks]
    average_length = sum(len(terms) for terms in document_terms) / max(len(document_terms), 1)
    document_frequency = {term: sum(term in set(terms) for terms in document_terms) for term in query_terms}
    scored: list[tuple[Chunk, float, tuple[str, ...]]] = []
    for chunk, terms in zip(chunks, document_terms):
        frequencies = {term: terms.count(term) for term in query_terms}
        matched = tuple(sorted(term for term, count in frequencies.items() if count))
        score = 0.0
        for term, frequency in frequencies.items():
            if not frequency:
                continue
            inverse_frequency = math.log(1 + (len(chunks) - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
            normalization = frequency + k1 * (1 - b + b * len(terms) / max(average_length, 1))
            score += inverse_frequency * (frequency * (k1 + 1) / normalization)
        if score:
            scored.append((chunk, score, matched))
    ranked = sorted(scored, key=lambda item: (-item[1], item[0].chunk_id))[:top_k]
    return [RetrievalHit(chunk, score, matched, rank) for rank, (chunk, score, matched) in enumerate(ranked, start=1)]


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


def build_context_pack(hits: list[RetrievalHit], *, max_characters: int = 900) -> ContextPack:
    """Keep the exact source IDs that made it into the context budget."""

    retained: list[RetrievalHit] = []
    used = 0
    for hit in hits:
        labelled = f"[{hit.chunk.chunk_id} | {hit.chunk.source}] {hit.chunk.text}"
        if retained and used + len(labelled) > max_characters:
            break
        retained.append(hit)
        used += len(labelled)
    return ContextPack(
        text=build_context(retained, max_characters=max_characters),
        citations=tuple(f"{hit.chunk.chunk_id} ({hit.chunk.source})" for hit in retained),
        retained_ids=tuple(hit.chunk.chunk_id for hit in retained),
        truncated=len(retained) < len(hits),
    )


def answer(query: str, chunks: list[Chunk], min_score: float = 0.2) -> str:
    results = retrieve(query, chunks)
    if not results or results[0][1] < min_score:
        return "I don't have enough evidence in the indexed documents to answer that."
    evidence = " ".join(chunk.text for chunk, _ in results)
    citations = ", ".join(f"[{chunk.chunk_id}]({chunk.source})" for chunk, _ in results)
    return f"Evidence found: {evidence}\n\nSources: {citations}"


def run_local_rag(
    query: str,
    chunks: list[Chunk],
    *,
    top_k: int = 3,
    min_score: float = 0.2,
    max_characters: int = 900,
) -> LocalRAGResult:
    """Run the beginner pipeline with an explicit evidence/decision contract.

    This function does not pretend to be an LLM. It demonstrates the hand-off a
    real generator should receive: a bounded, cited evidence package and a
    policy decision. A provider-backed generator can later replace the template
    while retaining retrieval traces and the abstention boundary.
    """

    hits = retrieve_with_trace(query, chunks, top_k=top_k)
    pack = build_context_pack(hits, max_characters=max_characters)
    context = pack.text
    citations = tuple(f"[{hit.chunk.chunk_id}]({hit.chunk.source})" for hit in hits if hit.chunk.chunk_id in pack.retained_ids)
    if not hits or hits[0].score < min_score:
        return LocalRAGResult(
            decision="abstain",
            answer="I don't have enough evidence in the indexed documents to answer that. Verify the source set or ask a more specific question.",
            query=query,
            hits=tuple(hits),
            context=context,
            citations=(),
            retrieval_threshold=min_score,
            context_budget=max_characters,
        )
    evidence = " ".join(hit.chunk.text for hit in hits if hit.chunk.chunk_id in pack.retained_ids)
    return LocalRAGResult(
        decision="answer",
        answer=f"Evidence found: {evidence}\n\nSources: {', '.join(citations)}",
        query=query,
        hits=tuple(hits),
        context=context,
        citations=citations,
        retrieval_threshold=min_score,
        context_budget=max_characters,
    )


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
            result = run_local_rag(query, chunks)
            print(result.answer)
    except EOFError:
        print()


if __name__ == "__main__":
    main()
