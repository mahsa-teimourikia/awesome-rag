# Adaptive RAG Lab: from static retrieval to bounded decision systems

This six-notebook specialization teaches Adaptive RAG as a policy-selection problem: choose the smallest retrieval and reasoning strategy that can answer a particular question reliably. The Northstar Insurance scenario makes the trade-offs visible: policy questions are current and private, comparisons need more evidence, exact identifiers reward lexical search, corpus-wide questions may need graph retrieval, and poor evidence must trigger bounded recovery or abstention.

| Step | Notebook | Decision exercised |
| --- | --- | --- |
| 01 | [Fixed versus adaptive](01_fixed_vs_adaptive.ipynb) | Why one pipeline does not fit every query |
| 02 | [Gates and complexity](02_retrieval_gates_and_complexity.ipynb) | Whether retrieval is needed and how difficult the evidence problem is |
| 03 | [Query and source routing](03_query_and_source_routing.ipynb) | Rewrite/decompose and select BM25, dense, hybrid, graph, SQL, or API routes |
| 04 | [Adaptive depth and context](04_adaptive_depth_and_context.ipynb) | Choose K and minimal sufficient context |
| 05 | [Corrective and self-reflective retrieval](05_corrective_and_self_reflective.ipynb) | Recover from poor evidence within a finite budget |
| 06 | [Production capstone](06_adaptive_rag_capstone.ipynb) | Evaluate routing, operations, safety, and the agentic boundary |

Start with [`docs/adaptive-rag.md`](../../docs/adaptive-rag.md). The deterministic code is in [`src/adaptive_rag/`](../../src/adaptive_rag/); it deliberately makes routing decisions explainable before learners try LangGraph, Haystack `ConditionalRouter`, LlamaIndex routing, or Microsoft GraphRAG.
