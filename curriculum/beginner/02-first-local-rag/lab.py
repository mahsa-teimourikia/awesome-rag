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
class ContextPack:
    """A bounded, auditable evidence package sent to an answer component.

    A RAG application should pass evidence *with* its identity and source, not
    concatenate anonymous text.  This object keeps the small baseline honest:
    callers can see which chunks were retained and whether a context budget
    discarded lower-ranked material.
    """

    text: str
    citations: tuple[str, ...]
    retained_ids: tuple[str, ...]
    truncated: bool


@dataclass(frozen=True)
class RetrievalMetrics:
    """Retrieval-only metrics; generation quality is measured elsewhere."""

    recall_at_k: float
    precision_at_k: float
    mean_reciprocal_rank: float
    abstention_accuracy: float


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


def retrieve_bm25(
    query: str,
    chunks: list[Chunk],
    *,
    top_k: int = 3,
    k1: float = 1.2,
    b: float = 0.75,
) -> list[RetrievalHit]:
    """A small BM25 implementation for comparing rankers in the notebook.

    This function intentionally favors clarity over indexing performance. It
    computes document frequencies from the supplied in-memory corpus each time;
    production search engines pre-compute those statistics and expose ranking
    configuration through a managed index.
    """

    query_terms = tokenize(query)
    document_terms = [TOKEN.findall(chunk.text.lower()) for chunk in chunks]
    average_length = sum(len(terms) for terms in document_terms) / max(len(document_terms), 1)
    document_frequency = {
        term: sum(term in set(terms) for terms in document_terms)
        for term in query_terms
    }
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


def retrieve_authorized(
    query: str,
    chunks: list[Chunk],
    *,
    allowed_sources: set[str],
    top_k: int = 3,
) -> list[RetrievalHit]:
    """Apply an allow-list before ranking, rather than filtering an answer.

    This is deliberately a source-level policy because the introductory corpus
    has no identities.  Production implementations normally filter by tenant,
    document ACL, and time/version metadata at the retrieval layer.
    """

    visible = [chunk for chunk in chunks if chunk.source in allowed_sources]
    return retrieve_with_trace(query, visible, top_k=top_k)


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
    """Return a labelled context window plus the provenance it contains."""

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
            "relevant_ids": case.relevant_ids,
            "retrieved_ids": retrieved_ids,
            "retrieval_hit": bool(relevant & set(retrieved_ids)),
            "abstained": abstained,
            "abstention_correct": abstained == case.should_abstain,
            "top_score": hits[0].score if hits else 0.0,
        })
    return report


def summarize_retrieval_metrics(report: list[dict[str, object]]) -> RetrievalMetrics:
    """Calculate simple, inspectable retrieval metrics from a golden-set run.

    ``recall_at_k`` answers whether at least one expected evidence ID appeared;
    ``precision_at_k`` measures how much of the returned set was relevant; MRR
    rewards placing relevant evidence earlier.  Cases intended to abstain are
    excluded from ranking metrics because they have no relevant document.
    """

    ranking_cases = [row for row in report if row["relevant_ids"]]
    hits = sum(bool(row["retrieval_hit"]) for row in ranking_cases)
    denominator = max(len(ranking_cases), 1)
    abstention_accuracy = sum(bool(row["abstention_correct"]) for row in report) / max(len(report), 1)
    precision_values: list[float] = []
    reciprocal_ranks: list[float] = []
    for row in ranking_cases:
        relevant = set(row["relevant_ids"])
        retrieved = tuple(row["retrieved_ids"])
        precision_values.append(sum(identifier in relevant for identifier in retrieved) / max(len(retrieved), 1))
        first_rank = next((index for index, identifier in enumerate(retrieved, start=1) if identifier in relevant), None)
        reciprocal_ranks.append(1 / first_rank if first_rank else 0.0)
    return RetrievalMetrics(
        recall_at_k=hits / denominator,
        precision_at_k=sum(precision_values) / denominator,
        mean_reciprocal_rank=sum(reciprocal_ranks) / denominator,
        abstention_accuracy=abstention_accuracy,
    )


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
