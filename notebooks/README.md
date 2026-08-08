# RAG notebooks

The notebooks are now organized around two learning modes. Start with the scenario-based Enterprise Knowledge Assistant track if you want the most complete theory + practice path. Use the beginner notebooks as small focused companions to the existing curriculum lessons.

## Enterprise Knowledge Assistant track

| Notebook | Topic |
| --- | --- |
| [01 RAG from scratch](enterprise/01_rag_from_scratch.ipynb) | Manual RAG loop, citations, failure-first baseline |
| [02 Parsing and chunking](enterprise/02_parsing_chunking_context.ipynb) | Structure-aware chunks and context engineering |
| [03 Dense, sparse, hybrid](enterprise/03_dense_sparse_hybrid.ipynb) | BM25, semantic search, exact identifiers, RRF |
| [04 Reranking](enterprise/04_reranking_evidence_selection.ipynb) | Evidence selection after noisy retrieval |
| [05 Query transformation](enterprise/05_query_transformation.ipynb) | Rewriting, multi-query, decomposition, HyDE |
| [06 GraphRAG](enterprise/06_graphrag_multihop.ipynb) | Multi-hop relationship questions |
| [07 RAG evaluation](enterprise/07_rag_evaluation.ipynb) | Retrieval and answer-quality diagnostics |
| [08 Adaptive and agentic RAG](enterprise/08_adaptive_corrective_agentic_rag.ipynb) | Routing, corrective loops, bounded agentic retrieval |
| [09 Production capstone](enterprise/09_production_capstone.ipynb) | Production architecture, operations, cost, and reliability |

## Focused beginner companions

| Notebook | Companion implementation |
| --- | --- |
| [First local RAG](beginner/01_first_local_rag.ipynb) | [`examples/beginner/first_local_rag.py`](../examples/beginner/first_local_rag.py) |
| [Chunking lab](beginner/02_chunking_lab.ipynb) | [`examples/beginner/chunking_lab.py`](../examples/beginner/chunking_lab.py) |
| [Citations and abstention](beginner/03_citations_abstention.ipynb) | [`examples/beginner/citations.py`](../examples/beginner/citations.py) |

Run locally with Jupyter or open the files in GitHub. Notebook code uses repository-relative paths; launch Jupyter from the repository root. Architecture diagrams in notebooks use readable ASCII flowcharts so the learning sequence remains legible in GitHub previews, Jupyter, and light or dark themes without a Mermaid renderer.

## PolicyAssist RAG Evaluation Lab

For a dedicated evaluation specialization, follow the [12-notebook PolicyAssist RAG Evaluation Lab](evaluation/README.md). It uses one Northstar Insurance scenario to teach dataset design, retrieval and context metrics, grounding, claims/citations, LLM-judge calibration, robustness, security, production monitoring, and release decisions.

## Adaptive RAG Lab

Follow the [six-notebook Adaptive RAG Lab](adaptive-rag/README.md) when you want to understand the transition from fixed retrieval to bounded retrieval/reasoning policies. It covers retrieval necessity, complexity routing, source and query routing, adaptive context depth, corrective loops, and the agentic-RAG boundary.
