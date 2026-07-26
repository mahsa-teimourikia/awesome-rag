# ✨ Awesome RAG (Retrieval-Augmented Generation) ✨

> A curated, practical guide to learning, building, evaluating, and operating Retrieval-Augmented Generation (RAG) systems.

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

RAG connects a language model to external knowledge at answer time: retrieve relevant evidence, then generate an answer grounded in that evidence. It is a strong fit when knowledge changes, must be private, needs citations, or is too specialized to assume the model knows it.

This collection emphasizes primary sources, maintained open-source projects, and resources that explain *why* a technique works—not just copy-paste demos.

## Contents

- [Start here](#start-here)
- [Learning roadmap](#learning-roadmap)
- [RAG explained](#rag-explained)
- [Test your RAG knowledge](#test-your-rag-knowledge)
- [A practical RAG architecture](#a-practical-rag-architecture)
- [Learning paths](#learning-paths)
- [Official educational resources](#official-educational-resources)
- [Open-source frameworks and libraries](#open-source-frameworks-and-libraries)
- [Retrieval infrastructure](#retrieval-infrastructure)
- [Patterns by use case](#patterns-by-use-case)
- [Evaluation and observability](#evaluation-and-observability)
- [Security and production checklist](#security-and-production-checklist)
- [Research and benchmarks](#research-and-benchmarks)
- [Related awesome lists](#related-awesome-lists)
- [Contributing](#contributing)

## Start here

**New to RAG?** Follow this sequence:

1. Read [What is RAG?](docs/what-is-rag.md) and the original [RAG paper](https://arxiv.org/abs/2005.11401).
2. Build a minimal, cited question-answering app with the [LangChain retrieval tutorial](https://docs.langchain.com/oss/python/langchain/retrieval) or [LlamaIndex starter tutorial](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/).
3. Learn retrieval quality with [hybrid search](docs/retrieval-patterns.md#hybrid-retrieval) and reranking.
4. Establish a representative evaluation set before tuning—see [Evaluation](docs/evaluation.md).
5. Add access control, observability, and continuous evaluation before calling it production-ready.

## RAG explained

RAG is a system design, not a single database query. The original paper describes augmenting a parametric generator with non-parametric retrieved memory. In modern applications, the memory is usually a versioned corpus of documents, records, or multimodal assets that is searched at runtime.

![Retrieval-Augmented Generation pipeline showing knowledge ingestion, query-time retrieval, grounded answer generation, and evaluation](assets/rag-pipeline.svg)

<sub>Diagram source: [Mermaid](assets/rag-pipeline.mmd).</sub>

The two quality questions are distinct:

- **Did we retrieve the right evidence?** (retrieval quality)
- **Did the model answer faithfully from that evidence?** (generation quality)

See [What is RAG?](docs/what-is-rag.md) for the concepts, trade-offs, and a source-by-source explanation.

## Test your RAG knowledge

Finished the guides? Take the [interactive RAG Knowledge Check](https://mahsa-teimourikia.github.io/awsome-rag/)—18 multiple-answer questions covering foundations, ingestion, retrieval, generation, evaluation, and security. It grades the complete test, gives a topic-by-topic score, and lets you reveal the correct answers with explanations and source links.

## Learning roadmap

This repository is expanding into a structured, project-based curriculum. Use the [roadmap](ROADMAP.md) and [curriculum map](curriculum/README.md) to choose a level:

- **Beginner:** build a local, cited RAG assistant from first principles.
- **Intermediate:** improve retrieval with hybrid search, filters, rewriting, reranking, and evaluation.
- **Advanced:** design corrective, graph, multimodal, agentic, and production RAG systems.

The [use-case catalog](use-cases/README.md) lets you choose a project after learning the underlying pattern. New lessons follow the [tutorial template](docs/tutorial-template.md) so every example includes objectives, setup, experiments, failure modes, evaluation, and exercises.

The quiz runs entirely in the browser and stores progress only on the learner's device. See the [quiz source](quiz/) or open [`quiz/index.html`](quiz/index.html) locally.

## A practical RAG architecture

| Stage | Responsibility | Common failure | First improvement |
| --- | --- | --- | --- |
| Ingestion | Extract text, metadata, and permissions | Broken PDF/layout extraction | Preserve source, page, section, and timestamps |
| Chunking | Create retrievable units | Chunks split an answer across boundaries | Chunk by document structure; test several sizes |
| Indexing | Make units searchable | Semantic matches miss exact terms | Use hybrid lexical + dense retrieval |
| Retrieval | Find candidate evidence | Vague queries retrieve noise | Rewrite/decompose queries; apply metadata filters |
| Reranking | Order candidates by relevance | Top-k contains weak evidence | Add a cross-encoder or late-interaction reranker |
| Generation | Answer only from supplied context | Hallucinated or unsupported claims | Require citations and an abstention path |
| Evaluation | Measure change over time | Only testing happy-path demos | Keep a labeled, representative golden set |

## Learning paths

### Foundations

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — the foundational 2020 paper; explains parametric vs. retrieved knowledge and RAG-Sequence/RAG-Token formulations.
- [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906) — foundational dense retrieval paper; useful for understanding dual encoders and contrastive retrieval training.
- [Sentence Transformers: Semantic Search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html) — practical explanation and examples of embedding-based search.
- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/) — free textbook covering BM25, ranking, evaluation metrics, and the information-retrieval basics RAG depends on.

### Build a first system

- [LangChain retrieval docs](https://docs.langchain.com/oss/python/langchain/retrieval) — explains 2-step RAG and agentic RAG patterns with implementation guidance.
- [LlamaIndex starter example](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/) — a concise first local-document Q&A workflow.
- [Haystack RAG pipeline tutorial](https://haystack.deepset.ai/tutorials/27_first_rag_pipeline) — component-oriented RAG tutorial from an open-source framework.
- [Microsoft Azure AI Search RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) — vendor documentation, but an unusually clear explanation of the end-to-end architecture and retrieval options.

### Improve quality

- [Advanced RAG Techniques: an Illustrated Overview](https://arxiv.org/abs/2309.07864) — taxonomy of pre-retrieval, retrieval, post-retrieval, and generation improvements.
- [RAG from scratch](https://github.com/langchain-ai/rag-from-scratch) — Jupyter notebooks covering routing, query construction, indexing, and evaluation patterns.
- [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) — hands-on notebooks for common advanced patterns; use as an experimentation companion, not a substitute for evaluation.

## Official educational resources

- [OpenAI: File search guide](https://platform.openai.com/docs/guides/tools-file-search) — official guide to hosted retrieval with vector stores and citations.
- [OpenAI cookbook: RAG](https://cookbook.openai.com/examples/file_search/responses) — runnable official examples using file search.
- [LangChain: retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) — official architecture and tutorial material.
- [LlamaIndex: understanding RAG](https://docs.llamaindex.ai/en/stable/understanding/rag/) — official conceptual and implementation guide.
- [Haystack: introduction](https://docs.haystack.deepset.ai/docs/intro) — official overview of pipelines, components, and integrations.
- [Hugging Face course: semantic search](https://huggingface.co/learn/cookbook/en/semantic_search_with_faiss) — practical semantic-search notebook using FAISS.
- [Cohere: RAG best practices](https://docs.cohere.com/docs/rag) — provider documentation with a useful retrieval/reranking focus.
- [Pinecone learn: RAG](https://www.pinecone.io/learn/retrieval-augmented-generation/) — accessible, vendor-neutral conceptual introduction.

## Open-source frameworks and libraries

### End-to-end frameworks

- [LangChain](https://github.com/langchain-ai/langchain) — composable building blocks for loaders, splitters, retrievers, and orchestration.
- [LlamaIndex](https://github.com/run-llama/llama_index) — data framework focused on indexing, retrieval, and agents over private data.
- [Haystack](https://github.com/deepset-ai/haystack) — component/pipeline framework for production search and RAG applications.
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel) — Microsoft SDK for AI orchestration with retrieval connectors and memory abstractions.
- [DSPy](https://github.com/stanfordnlp/dspy) — programming framework for optimizing LM pipelines; valuable for systematic RAG prompting and modules.

### Ingestion and document processing

- [Unstructured](https://github.com/Unstructured-IO/unstructured) — open-source document parsing and chunking for many file types.
- [Docling](https://github.com/docling-project/docling) — document conversion with layout-aware structure, tables, and OCR support.
- [Apache Tika](https://tika.apache.org/) — mature content extraction toolkit for broad document formats.
- [Marker](https://github.com/datalab-to/marker) — PDF-to-markdown/JSON conversion designed to preserve structure.

### Embeddings, rerankers, and retrieval models

- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) — widely used embedding and cross-encoder toolkit.
- [Hugging Face Text Embeddings Inference](https://github.com/huggingface/text-embeddings-inference) — high-performance embedding and reranking inference server.
- [BGE / FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) — open embedding, reranking, and retrieval models/tooling.
- [ColBERT](https://github.com/stanford-futuredata/ColBERT) — late-interaction retrieval for high-quality ranking at scale.

## Retrieval infrastructure

### Vector and hybrid search

- [FAISS](https://github.com/facebookresearch/faiss) — efficient dense-vector similarity search library; great for local prototypes and research.
- [Qdrant](https://github.com/qdrant/qdrant) — open-source vector database with filtering and hybrid-search capabilities.
- [Weaviate](https://github.com/weaviate/weaviate) — open-source vector database with hybrid search and modules.
- [Milvus](https://github.com/milvus-io/milvus) — distributed vector database for large-scale similarity search.
- [Chroma](https://github.com/chroma-core/chroma) — developer-friendly open-source embedding database for prototypes and applications.
- [OpenSearch](https://github.com/opensearch-project/OpenSearch) — open-source search engine for lexical, vector, and hybrid search.
- [Vespa](https://github.com/vespa-engine/vespa) — production search platform supporting lexical, vector, hybrid, and learned ranking.

### Graph and structured retrieval

- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) — graph-based retrieval for corpus-level questions and relationship-heavy data.
- [Neo4j GraphRAG](https://github.com/neo4j/neo4j-graphrag-python) — Python package for graph-enhanced RAG over Neo4j.
- [txtai](https://github.com/neuml/txtai) — embeddings database and semantic search workflows with graph support.

## Patterns by use case

| Use case | Starting pattern | Why |
| --- | --- | --- |
| Internal documentation assistant | Hybrid retrieval + metadata filters + citations | Documentation includes exact identifiers, versions, and prose |
| Customer support | Query rewriting + reranking + escalation/abstention | Questions are noisy and the cost of a wrong answer is high |
| Legal, policy, or compliance research | Section-aware chunks + source links + strict access control | Provenance and permissions matter as much as fluency |
| Analytics over tables | Text-to-SQL/tool use + schema retrieval | Answers should come from structured data, not only embedded text |
| Codebase assistant | Symbol-aware chunking + lexical search + file/line citations | Identifiers and dependency structure are essential |
| Research synthesis | Multi-query retrieval + deduplication + claim-level citations | One query rarely captures every relevant source |
| Enterprise knowledge graph | GraphRAG / entity retrieval alongside text search | Relationships and global questions exceed isolated-chunk retrieval |

Read [Retrieval patterns](docs/retrieval-patterns.md) for detailed explanations, decision criteria, and sources.

## Evaluation and observability

- [Ragas](https://github.com/explodinggradients/ragas) — open-source framework for evaluating RAG pipelines with retrieval and answer-quality metrics.
- [DeepEval](https://github.com/confident-ai/deepeval) — LLM evaluation framework with RAG metrics and test-case workflows.
- [TruLens](https://github.com/truera/trulens) — open-source evaluation and feedback functions for LLM applications.
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — open-source tracing, evaluation, and experimentation platform for LLM applications.
- [Langfuse](https://github.com/langfuse/langfuse) — open-source observability platform for tracing and evaluating LLM applications.
- [RAGAS documentation](https://docs.ragas.io/en/stable/concepts/metrics/) — definitions and use of metrics such as faithfulness, context precision, and context recall.
- [RAGChecker](https://github.com/amazon-science/RAGChecker) — fine-grained diagnostic framework for RAG evaluation.

See [Evaluation](docs/evaluation.md) for a concrete evaluation loop and metric selection guidance.

## Security and production checklist

- [ ] Enforce document-level access control *before* retrieval; never rely on the model to hide unauthorized text.
- [ ] Store source identifiers, document versions, and section/page locations with every chunk.
- [ ] Treat retrieved content as untrusted input: it can contain prompt-injection instructions.
- [ ] Use allowlisted tools and validate all tool parameters if RAG is combined with agents.
- [ ] Return traceable citations; support “I don’t have enough evidence” as a valid answer.
- [ ] Create a golden dataset covering fresh, stale, adversarial, permission-boundary, and no-answer queries.
- [ ] Measure retrieval and generation separately; inspect failures, not only aggregate scores.
- [ ] Monitor corpus freshness, indexing failures, latency, empty retrieval, and citation coverage.

Useful guidance: [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/), [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), and [OpenAI safety best practices](https://platform.openai.com/docs/guides/safety-best-practices).

## Research and benchmarks

- [RAG paper](https://arxiv.org/abs/2005.11401) — foundational retrieval-augmented generation work.
- [BEIR](https://github.com/beir-cellar/beir) — heterogeneous benchmark for zero-shot information retrieval.
- [MTEB](https://github.com/embeddings-benchmark/mteb) — benchmark suite for text-embedding models, including retrieval tasks.
- [CRAG](https://github.com/facebookresearch/CRAG) — benchmark for retrieval-augmented generation with a focus on realism and robustness.
- [RAGBench](https://github.com/RAGAI-RAGBench/RAGBench) — benchmark for diagnosing RAG systems under diverse conditions.
- [GraphRAG paper](https://arxiv.org/abs/2404.16130) — explores graph-based retrieval for global sensemaking over private corpora.
- [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884) — proposes retrieval-quality assessment and corrective actions.

## Related awesome lists

- [ai-boost/awesome-a2a](https://github.com/ai-boost/awesome-a2a)
- [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts)
- [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)
- [awesome-machine-learning](https://github.com/josephmisiti/awesome-machine-learning)
- [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Prefer primary sources, active open-source projects, and a short explanation of why each link belongs here.

## License

This repository is licensed under the [MIT License](LICENSE).
