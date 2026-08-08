from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Iterable
import time

from .advanced import corrective_retrieve, graph_answer, route, expand_queries
from .corpus import Chunk, chunk_documents, load_corpus
from .evaluation import evaluate_case, cost_per_successful_task
from .generation import answer_with_citations, naive_answer
from .retrieval import hybrid_retrieve, retrieve, tokenize


def build_enterprise_chunks(data_dir="data/enterprise", strategy="structure", max_words=80) -> list[Chunk]:
    return chunk_documents(load_corpus(data_dir), strategy=strategy, max_words=max_words)


def explain_hits(hits: list[tuple[Chunk, float]], limit: int = 5) -> list[dict]:
    rows = []
    for rank, (chunk, score) in enumerate(hits[:limit], start=1):
        rows.append({
            "rank": rank,
            "score": round(score, 4),
            "chunk_id": chunk.id,
            "source": chunk.document_id,
            "section": chunk.metadata.get("section", ""),
            "preview": chunk.text[:170] + ("…" if len(chunk.text) > 170 else ""),
        })
    return rows


def compare_rag_vs_no_rag(question: str, chunks: list[Chunk], top_k: int = 5) -> dict:
    evidence = hybrid_retrieve(question, chunks, top_k=top_k)
    return {
        "question": question,
        "without_rag": {"answer": naive_answer(question), "citations": [], "risk": "unsupported claim"},
        "with_rag": answer_with_citations(question, evidence),
        "retrieval_trace": explain_hits(evidence),
    }


def compare_chunking(question: str, data_dir="data/enterprise", sizes=(8, 16, 40)) -> list[dict]:
    rows = []
    for strategy in ["fixed", "structure"]:
        for size in sizes:
            chunks = build_enterprise_chunks(data_dir, strategy=strategy, max_words=size)
            hits = hybrid_retrieve(question, chunks, top_k=3)
            rows.append({
                "strategy": strategy,
                "max_words": size,
                "chunk_count": len(chunks),
                "top_sources": [c.document_id for c, _ in hits],
                "top_preview": hits[0][0].text[:140] if hits else "NO HIT",
            })
    return rows


def compare_retrievers(question: str, chunks: list[Chunk], top_k: int = 5) -> dict[str, list[dict]]:
    return {
        "bm25_sparse": explain_hits(retrieve(question, chunks, method="bm25", top_k=top_k)),
        "semantic_dense_toy": explain_hits(retrieve(question, chunks, method="dense", top_k=top_k)),
        "hybrid_rrf": explain_hits(hybrid_retrieve(question, chunks, top_k=top_k)),
    }


def rerank_by_evidence_terms(question: str, hits: list[tuple[Chunk, float]], extra_terms: Iterable[str] = ()) -> list[tuple[Chunk, float]]:
    q_terms = set(tokenize(question)) | {t.lower() for t in extra_terms}
    return sorted(hits, key=lambda hit: (len(q_terms & set(tokenize(hit[0].text))), hit[1]), reverse=True)


def query_transformation_report(question: str, chunks: list[Chunk]) -> list[dict]:
    rows = []
    for variant in expand_queries(question):
        hits = hybrid_retrieve(variant, chunks, top_k=3)
        rows.append({"variant": variant, "hits": explain_hits(hits, limit=3)})
    return rows


def evaluate_questions(cases: list[dict], chunks: list[Chunk], retriever: Callable[[str, list[Chunk]], list[tuple[Chunk, float]]] = hybrid_retrieve) -> list[dict]:
    report = []
    for case in cases:
        started = time.perf_counter()
        hits = retriever(case["question"], chunks)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        metrics = evaluate_case([c.id for c, _ in hits], case["relevant_ids"])
        report.append({
            "id": case["id"],
            "question": case["question"],
            **metrics,
            "latency_ms": elapsed_ms,
            "top_sources": [c.document_id for c, _ in hits[:3]],
        })
    return report


def diagnostic_next_step(row: dict) -> str:
    if row.get("recall@5", 0) < 1:
        return "Improve ingestion, chunking, query transformation, or first-stage retrieval."
    if row.get("precision@5", 0) < 0.5:
        return "Add reranking or stronger evidence selection."
    return "Inspect answer faithfulness, citation validation, latency, and cost."


def adaptive_trace(question: str, chunks: list[Chunk]) -> dict:
    retrieval = corrective_retrieve(question, chunks)
    return {
        "question": question,
        "router_choice": route(question),
        "corrective_route": retrieval["route"],
        "abstained": retrieval["abstained"],
        "evidence": explain_hits(retrieval["evidence"], limit=5),
    }


def production_run(questions: list[str], chunks: list[Chunk]) -> dict:
    traces = []
    for q in questions:
        start = time.perf_counter()
        hits = hybrid_retrieve(q, chunks, top_k=5)
        answer = answer_with_citations(q, hits)
        elapsed = time.perf_counter() - start
        traces.append({
            "question": q,
            "route": route(q),
            "retrieved": len(hits),
            "citation_count": len(answer["citations"]),
            "supported": answer["supported"],
            "latency_ms": round(elapsed * 1000, 3),
            "estimated_cost": 0.002 + 0.0003 * len(hits),
        })
    successes = sum(t["supported"] for t in traces)
    total_cost = sum(t["estimated_cost"] for t in traces)
    return {
        "traces": traces,
        "summary": {
            "successful_tasks": successes,
            "total_tasks": len(traces),
            "total_estimated_cost": round(total_cost, 4),
            "cost_per_successful_task": cost_per_successful_task(total_cost, successes),
        },
    }
