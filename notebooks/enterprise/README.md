# Enterprise Knowledge Assistant notebook track

This is the canonical scenario-based practical track for the RAG Learning Hub. The fictional company **NovaTech** needs an Enterprise Knowledge Assistant over HR policies, finance reviews, operational runbooks, vendor contracts, and project documentation. Each notebook is designed as the primary learning artifact for its topic: it explains the theory, shows the architecture with Mermaid, runs the implementation, breaks the system deliberately, evaluates the result, and closes with production-design questions.

| # | Notebook | Focus | Main implementation |
| --- | --- | --- | --- |
| 01 | [RAG from scratch](01_rag_from_scratch.ipynb) | Build the full loop manually | Python baseline |
| 02 | [Parsing and chunking](02_parsing_chunking_context.ipynb) | Context boundaries and chunk failures | Python baseline |
| 03 | [Dense, sparse, hybrid](03_dense_sparse_hybrid.ipynb) | BM25, semantic search, RRF | Python baseline, maps to Sentence Transformers/BM25 |
| 04 | [Reranking](04_reranking_evidence_selection.ipynb) | Candidate set vs final evidence | Haystack-style pipeline concept |
| 05 | [Query transformation](05_query_transformation.ipynb) | Rewriting, multi-query, decomposition, HyDE | LangChain/LlamaIndex concepts |
| 06 | [GraphRAG](06_graphrag_multihop.ipynb) | Multi-hop entity evidence | Neo4j/Microsoft GraphRAG concepts |
| 07 | [Evaluation](07_rag_evaluation.ipynb) | Recall@K, precision, MRR, faithfulness diagnostics | Ragas-style metrics |
| 08 | [Adaptive and agentic RAG](08_adaptive_corrective_agentic_rag.ipynb) | Routing and corrective loops | LangGraph concepts |
| 09 | [Production capstone](09_production_capstone.ipynb) | Offline/online pipeline, operations, cost, citations | Framework-independent architecture |

Run from the repository root so imports and data paths resolve:

```bash
python -m pip install -e .
jupyter lab notebooks/enterprise
```

The deterministic path has no API-key requirement. Optional extensions can replace the toy retriever with Sentence Transformers, Chroma, FAISS, Qdrant, OpenSearch, Haystack, LlamaIndex, LangChain, LangGraph, Neo4j, and Ragas.


## Notebook lesson format

Every notebook follows the same learning loop:

1. **Scenario and theory** — why this RAG problem appears in a real enterprise assistant.
2. **Concept map** — a Mermaid diagram of the architecture or decision flow.
3. **Implementation walkthrough** — runnable, deterministic Python backed by reusable modules in `src/enterprise_rag`.
4. **Failure-first experiment** — a query, chunking choice, retriever route, or evaluation fixture that makes the weakness visible.
5. **Production note** — how the idea maps to common libraries such as Sentence Transformers, Chroma, FAISS, Qdrant, OpenSearch, Haystack, LangChain, LlamaIndex, LangGraph, Neo4j, and Ragas.
6. **Reflection and exercises** — questions that ask learners to justify the next engineering improvement.

Treat these notebooks as the lab reference. The Learning Hub and README point learners here when they are ready to practice theory and implementation together.
