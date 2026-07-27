# Learning guide

Use this page as the shortest route through the repository. Each step has a concept lesson, a guided notebook, reusable Python, an exercise, and tests.

## Beginner: build one trustworthy assistant

1. [RAG foundations](curriculum/beginner/01-rag-foundations/README.md) — understand the pipeline.
2. [First local baseline](curriculum/beginner/02-first-local-rag/README.md) — retrieve local evidence.
3. [Chunking lab](curriculum/beginner/03-chunking-lab/README.md) — compare boundaries and metadata.
4. [Citations and abstention](curriculum/beginner/04-citations-abstention/README.md) — preserve provenance and say “not enough evidence.”
5. [Documentation assistant capstone](use-cases/documentation-assistant/README.md) — combine the pieces.

## Intermediate: improve and measure retrieval

1. [Retrieval strategies](curriculum/intermediate/01-retrieval-strategies/README.md) — BM25, dense adapters, and fusion.
2. [Metadata permissions](curriculum/intermediate/02-metadata-permissions/README.md) — authorize before retrieval.
3. [Query rewriting and reranking](curriculum/intermediate/03-query-reranking/README.md) — improve recall and ordering.
4. [Evaluation lab](curriculum/intermediate/04-evaluation/README.md) — golden sets and regression gates.
5. [Research synthesis](curriculum/intermediate/05-research-synthesis/README.md) — multi-query, deduplication, and claim citations.
6. [Customer-support assistant](use-cases/customer-support/README.md) — apply the patterns to a realistic workflow.

## Advanced: design for recovery and operations

1. [Corrective RAG](curriculum/advanced/01-corrective-rag/README.md) — recover from weak retrieval.
2. [GraphRAG](curriculum/advanced/02-graphrag/README.md) — traverse entity relationships.
3. [Agentic RAG](curriculum/advanced/03-agentic-rag/README.md) — route tools with approval boundaries.
4. [Structured and multimodal RAG](curriculum/advanced/04-structured-multimodal/README.md) — typed tables, images, and OCR.
5. [Production operations](curriculum/advanced/05-production-operations/README.md) — traces, budgets, freshness, and readiness.

## How to study a lesson

1. Read the objectives and architecture diagram.
2. Run the notebook from the repository root.
3. Read the companion Python module.
4. Change one variable and record the result.
5. Run the tests and add one test for your exercise.
6. Explain one failure mode and one production safeguard.

If you are unsure where to start, complete the beginner documentation assistant first. If you already operate a RAG system, start with the evaluation lab and work backward from observed failures.
