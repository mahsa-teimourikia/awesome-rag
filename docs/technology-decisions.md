# Technology decisions

The core curriculum intentionally uses small Python implementations first, then introduces production technologies when the learner understands the failure mode they address. This keeps the learning path coherent while still showing the broader ecosystem.

## Default path

| Need | Default | Why it appears here |
| --- | --- | --- |
| Environment | `uv` + Python 3.11+ | Fast, reproducible project setup |
| Data framework | LlamaIndex | Clear ingestion and retrieval abstractions |
| Workflow/agents | LangGraph | Explicit stateful routing and recovery |
| Vector search | Qdrant | Local Docker path plus metadata filtering |
| Embeddings | Sentence Transformers | Local experimentation and model choice |
| Documents | Docling | Layout-aware PDF and document parsing |
| Schemas | Pydantic | Typed boundaries and validation |
| API | FastAPI | Small production-style service surface |
| Evaluation | Ragas + DeepEval | Retrieval and answer-quality checks |
| Observability | OpenTelemetry + Phoenix/Langfuse | Traces, metrics, and experiment inspection |

## Choosing alternatives

- Choose **LangChain** when a team already uses its integrations or wants broad provider coverage; do not introduce it before learners understand the underlying stages.
- Choose **Haystack** when component pipelines and deployment-oriented abstractions are the main teaching goal.
- Choose **Chroma** for a very small prototype; choose **Qdrant**, **Weaviate**, **Milvus**, or **OpenSearch** when filtering, scale, hybrid search, or operational requirements justify them.
- Choose hosted retrieval when managed operations matter more than local control; still teach permissions, citations, evaluation, and failure behavior around it.
- Choose GraphRAG only when relationships or corpus-level questions justify graph extraction and traversal complexity.

## Selection checklist

Before choosing a library, write down:

1. Corpus size, update frequency, and document modalities.
2. Tenant and document authorization requirements.
3. Exact-term versus semantic retrieval needs.
4. Latency, cost, and deployment constraints.
5. Evaluation data and regression thresholds.
6. Observability, retention, and incident-response requirements.

The most prominent tool is not automatically the best tool. A technology belongs in a production design only when its trade-offs match the use case and can be measured.
