from pathlib import Path

from src.enterprise_rag.lab_experiments import (
    adaptive_trace,
    build_enterprise_chunks,
    compare_chunking,
    compare_rag_vs_no_rag,
    compare_retrievers,
    production_run,
)


def chunks():
    return build_enterprise_chunks(Path("data/enterprise"))


def test_compare_rag_vs_no_rag_returns_citations():
    result = compare_rag_vs_no_rag("What increased by 14% in Q2 2025?", chunks())
    assert result["without_rag"]["risk"] == "unsupported claim"
    assert result["with_rag"]["citations"]


def test_compare_chunking_exposes_multiple_strategies():
    rows = compare_chunking("What increased by 14% in Q2 2025?", Path("data/enterprise"), sizes=(8,))
    assert {row["strategy"] for row in rows} == {"fixed", "structure"}


def test_compare_retrievers_reports_three_methods():
    report = compare_retrievers("What does AX-774-B mean?", chunks(), top_k=2)
    assert set(report) == {"bm25_sparse", "semantic_dense_toy", "hybrid_rrf"}


def test_adaptive_and_production_traces_are_inspectable():
    data = chunks()
    trace = adaptive_trace("Who supplies Project Atlas technology and what regulation applies?", data)
    assert trace["router_choice"] == "graph"
    run = production_run(["What does AX-774-B mean?"], data)
    assert run["summary"]["successful_tasks"] == 1
