# Enterprise Knowledge Assistant notebook track

This is the canonical scenario-based practical track for the RAG Learning Hub. The fictional company **NovaTech** needs an Enterprise Knowledge Assistant over HR policies, finance reviews, operational runbooks, vendor contracts, and project documentation. Each notebook teaches one RAG engineering decision by breaking the system first, then improving it with evidence.

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
