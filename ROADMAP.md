# RAG learning roadmap

This repository is evolving from a curated reading list into a progressive, runnable learning platform. Each lesson should move through the same loop: learn the concept, run a small example, change one variable, measure the effect, and explain the trade-off.

## Levels

| Level | Outcome | Typical projects |
| --- | --- | --- |
| Beginner | Build a cited RAG application over local documents | Notes assistant, documentation Q&A, FAQ bot |
| Intermediate | Diagnose and improve retrieval quality | Support assistant, policy research, codebase search |
| Advanced | Design reliable, secure, observable RAG systems | Enterprise assistant, GraphRAG investigator, agentic RAG |

## Delivery sequence

1. **Foundation (current):** learning paths, tutorial contract, use-case catalog, and shared conventions.
2. **Beginner track:** local ingestion, chunking, embeddings, vector search, citations, and abstention.
3. **Intermediate track:** BM25, hybrid retrieval, filters, query rewriting, reranking, and evaluation.
4. **Use-case projects:** documentation, support, legal research, codebases, research synthesis, and tables.
5. **Advanced track:** corrective RAG, GraphRAG, agentic routing, multimodal data, and freshness.
6. **Production track:** API serving, observability, access control, cost/latency, security, and CI regression tests.

Every stage should add runnable code, a small fixture dataset, an evaluation check, a Mermaid diagram where it clarifies the design, and a quiz checkpoint.

## Definition of done for a lesson

- [ ] Level, prerequisites, estimated time, and learning objectives are stated.
- [ ] The lesson explains the concept before introducing framework APIs.
- [ ] The example runs from a clean checkout with documented commands.
- [ ] Inputs and expected outputs are deterministic or seeded.
- [ ] At least one failure mode is demonstrated.
- [ ] The learner has an exercise with an observable success criterion.
- [ ] Sources link to primary documentation, research, or maintained projects.

## Technology policy

The main path will use one coherent Python stack: `uv`, LlamaIndex, Qdrant, Sentence Transformers, Docling, Pydantic, FastAPI, Ragas, and Phoenix or Langfuse. Comparison notes may cover LangChain, Haystack, Chroma, Weaviate, Milvus, OpenSearch, and hosted retrieval services, but learners should not need every framework to complete the core path.

## How to use the roadmap

Use the catalog in the README to choose a lesson. New tutorials should be added to the appropriate level directory. The roadmap is intentionally incremental: a small, evaluated tutorial is more valuable than an untested collection of notebooks.
