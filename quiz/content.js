const content = {
  Foundations: {
    theory: "RAG combines a searchable, versioned knowledge base with a language model at answer time. Retrieval supplies evidence; generation turns that evidence into a response. Retrieval quality and answer faithfulness are separate things to measure.",
    workflow: ["Define the corpus and source-of-truth policy", "Retrieve a small, inspectable evidence set", "Generate only from supplied evidence", "Cite sources and abstain when evidence is insufficient"],
    bestPractices: ["Keep source IDs, versions, and locations with every chunk", "Show retrieved evidence during debugging", "Treat groundedness as a measured property, not a prompt promise"],
    references: [{ label: "Original RAG paper", url: "https://arxiv.org/abs/2005.11401" }, { label: "What is RAG?", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/docs/what-is-rag.md" }],
  },
  Ingestion: {
    theory: "Ingestion turns source material into retrievable units. Extraction, normalization, chunking, metadata, and indexing decisions determine what evidence can be found later.",
    workflow: ["Extract text while preserving structure", "Split by semantic boundaries and test chunk sizes", "Attach provenance, permissions, and freshness metadata", "Index and verify representative retrievals"],
    bestPractices: ["Version indexes and make ingestion idempotent", "Never discard page, section, or record locations", "Evaluate chunking with real questions rather than intuition"],
    references: [{ label: "Lifecycle and chunking guide", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/docs/what-is-rag.md#the-lifecycle" }, { label: "RAG from scratch", url: "https://github.com/langchain-ai/rag-from-scratch" }],
  },
  Retrieval: {
    theory: "Retrieval is a ranking problem: find useful candidates, apply authorization and filters, then order evidence for the generator. Lexical, dense, hybrid, reranking, graph, and corrective strategies solve different failure modes.",
    workflow: ["Normalize or rewrite the query", "Apply tenant and metadata constraints", "Retrieve a broad candidate set", "Rerank, deduplicate, and inspect recall"],
    bestPractices: ["Measure recall separately from answer quality", "Keep lexical fallback for exact identifiers", "Tune top-k, filters, and reranking against a golden set"],
    references: [{ label: "Retrieval patterns", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/docs/retrieval-patterns.md" }, { label: "Introduction to Information Retrieval", url: "https://nlp.stanford.edu/IR-book/" }],
  },
  Generation: {
    theory: "Generation should transform retrieved evidence into a useful answer without inventing unsupported claims. Citations, claim-level grounding, confidence signals, and abstention make uncertainty visible.",
    workflow: ["Format evidence with stable source labels", "Use an answer contract that requires citations", "Check claims against retrieved passages", "Abstain or ask a clarifying question when evidence is weak"],
    bestPractices: ["Separate instructions from retrieved data", "Prefer concise answers with traceable citations", "Test unsupported, conflicting, and no-answer cases"],
    references: [{ label: "Citations and abstention lab", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/curriculum/beginner/04-citations-abstention/README.md" }, { label: "OpenAI file search guide", url: "https://platform.openai.com/docs/guides/tools-file-search" }],
  },
  Security: {
    theory: "RAG security is a data-boundary problem. Authorization must happen before content reaches the model, and retrieved documents must be treated as untrusted input because they may contain prompt injection.",
    workflow: ["Resolve identity and tenant context", "Filter candidates before context construction", "Constrain tools and validate parameters", "Log and test permission-boundary failures"],
    bestPractices: ["Never ask the model to enforce access control", "Keep secrets out of prompts and traces", "Include malicious and cross-tenant cases in evaluation"],
    references: [{ label: "Metadata permissions guide", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/curriculum/intermediate/02-metadata-permissions/README.md" }, { label: "OWASP GenAI risks", url: "https://genai.owasp.org/llm-top-10/" }],
  },
  Evaluation: {
    theory: "Evaluation turns RAG iteration into an engineering discipline. Retrieval metrics, answer faithfulness, citation quality, latency, cost, and human review expose different failure surfaces.",
    workflow: ["Create a representative golden set", "Measure retrieval and generation separately", "Inspect changed failures, not only averages", "Gate releases and compare against a stable baseline"],
    bestPractices: ["Calibrate LLM judges with human review", "Track slices such as permissions and no-answer cases", "Store experiment configuration with every score"],
    references: [{ label: "Evaluation guide", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/docs/evaluation.md" }, { label: "Ragas metrics", url: "https://docs.ragas.io/en/stable/concepts/metrics/" }],
  },
  Operations: {
    theory: "Production RAG requires observability and controlled change. Freshness, index versions, traces, budgets, latency, quality regressions, and rollback paths keep the system dependable after the demo.",
    workflow: ["Trace ingestion, retrieval, generation, and tools", "Set freshness, latency, cost, and quality SLOs", "Roll out index and model changes gradually", "Use alerts, runbooks, and reversible rollback"],
    bestPractices: ["Attribute cost and latency per request route", "Canary changes against a stable baseline", "Document ownership for stale data and failed ingestion"],
    references: [{ label: "Production operations guide", url: "https://github.com/mahsa-teimourikia/awsome-rag/blob/main/curriculum/advanced/05-production-operations/README.md" }, { label: "RAG observability patterns", url: "https://github.com/Arize-ai/phoenix" }],
  },
};

export const lessonContent = content;
