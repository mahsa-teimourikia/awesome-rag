const content = {
  "01 - RAG Foundations": {
    theory: "RAG connects a language model to external knowledge at answer time. The corpus acts as non-parametric memory: retrieve relevant evidence, then generate a response grounded in that evidence.",
    workflow: ["Define the corpus", "Retrieve evidence", "Generate grounded answer", "Evaluate"],
    bestPractices: ["Measure retrieval separately from generation", "Abstain when evidence is missing"],
    references: [{ label: "RAG Foundations", url: "curriculum/beginner/01-rag-foundations/README.md" }],
  },
  "02 - First Local Baseline": {
    theory: "Start with transparent lexical retrieval so every score, match, source ID, and no-answer decision is visible. This separates retrieval quality from answer faithfulness before adding embeddings.",
    workflow: ["Load Markdown", "Retrieve lexical matches", "Bound context window", "Measure on golden set"],
    bestPractices: ["Keep behavior inspectable", "Test abstention explicitly"],
    references: [{ label: "First Local Baseline", url: "curriculum/beginner/02-first-local-rag/README.md" }],
  },
  "03 - Chunking Lab": {
    theory: "Chunking is an information-design decision. Predictable fixed windows, document headings, and sentence windows each affect whether evidence stays intact.",
    workflow: ["Extract text", "Test chunking strategies", "Compare on real questions"],
    bestPractices: ["Preserve metadata", "Evaluate on real questions"],
    references: [{ label: "Chunking Lab", url: "curriculum/beginner/03-chunking-lab/README.md" }],
  },
  "04 - Citations & Abstention": {
    theory: "A citation is data, not formatting. Distinguish insufficient evidence, ambiguous evidence, and lack of source diversity.",
    workflow: ["Audit structured evidence", "Apply threshold policies", "Render claim-level citations"],
    bestPractices: ["Return auditable objects", "Make abstention explicit"],
    references: [{ label: "Citations & Abstention", url: "curriculum/beginner/04-citations-abstention/README.md" }],
  },
  "05 - Retrieval Strategies": {
    theory: "Lexical is strong for identifiers. Dense matches paraphrases. Hybrid treats both as useful signals, combining them with reciprocal-rank fusion.",
    workflow: ["Lexical search", "Dense search", "Reciprocal-rank fusion"],
    bestPractices: ["Keep BM25 for exact terms", "Combine with dense"],
    references: [{ label: "Retrieval Strategies", url: "curriculum/intermediate/01-retrieval-strategies/README.md" }],
  },
  "06 - Metadata Permissions": {
    theory: "Filtering after retrieval is too late. The policy filter must produce an authorized subset before the retriever sees it.",
    workflow: ["Extract tenant tags", "Apply policy filter to index", "Retrieve from authorized subset"],
    bestPractices: ["Enforce tags before retrieval", "Test boundary directly"],
    references: [{ label: "Metadata Permissions", url: "curriculum/intermediate/02-metadata-permissions/README.md" }],
  },
  "07 - Query Reranking": {
    theory: "Rewriting improves recall, while reranking is applied to a bounded candidate set to improve ordering.",
    workflow: ["Rewrite query", "Retrieve broad set", "Rerank bounded set"],
    bestPractices: ["Bound reranker to top-k", "Measure precision gain vs latency cost"],
    references: [{ label: "Query Reranking", url: "curriculum/intermediate/03-query-reranking/README.md" }],
  },
  "08 - Evaluation Lab": {
    theory: "A golden dataset turns RAG iteration into an engineering discipline. Measure recall@k, precision@k, and MRR.",
    workflow: ["Create golden set", "Calculate retrieval metrics", "Gate regressions"],
    bestPractices: ["Test failure boundaries", "Separate retrieval metrics from groundedness"],
    references: [{ label: "Evaluation Lab", url: "curriculum/intermediate/04-evaluation/README.md" }],
  },
  "09 - Research Synthesis": {
    theory: "One query often overfits to its first framing. Retrieve evidence, findings, limitations, and counterarguments separately.",
    workflow: ["Use multiple focused queries", "Deduplicate evidence", "Synthesize with claim-level citations"],
    bestPractices: ["Avoid single-query bias", "Keep counterevidence"],
    references: [{ label: "Research Synthesis", url: "curriculum/intermediate/05-research-synthesis/README.md" }],
  },
  "10 - Local Qdrant & Embeddings": {
    theory: "Vector search must preserve payload metadata and filters while providing dense semantic search.",
    workflow: ["Embed chunks", "Upsert vectors and payloads", "Search with tenant filters"],
    bestPractices: ["Retain metadata", "Use tenant filters"],
    references: [{ label: "Local Qdrant", url: "curriculum/intermediate/06-qdrant-local/README.md" }],
  },
  "11 - Corrective RAG": {
    theory: "Corrective RAG detects weak retrieval, bounds recovery routes, and makes abstention a valid terminal state.",
    workflow: ["Grade first retrieval", "Reformulate or fallback", "Abstain if evidence is still weak"],
    bestPractices: ["Bound retries", "Record route, confidence, and latency"],
    references: [{ label: "Corrective RAG", url: "curriculum/advanced/01-corrective-rag/README.md" }],
  },
  "12 - GraphRAG": {
    theory: "Graph retrieval is useful for relationships, paths, and corpus-level questions. Bound traversal depth and apply authorization.",
    workflow: ["Extract nodes/edges", "Traverse with boundaries", "Return facts"],
    bestPractices: ["Bound depth", "Apply tenant filters to graph"],
    references: [{ label: "GraphRAG", url: "curriculum/advanced/02-graphrag/README.md" }],
  },
  "13 - Agentic RAG": {
    theory: "An agent is not authorized merely because a model selected a tool. The system enforces permissions and records the route.",
    workflow: ["Route to tool", "Require explicit approval", "Verify receipt"],
    bestPractices: ["Validate tool arguments", "Require human approval for destructive actions"],
    references: [{ label: "Agentic RAG", url: "curriculum/advanced/03-agentic-rag/README.md" }],
  },
  "14 - Structured & Multimodal RAG": {
    theory: "Route table questions to typed operations and treat images, audio, OCR, and text as modality-specific evidence.",
    workflow: ["Classify question", "Execute typed SQL or OCR", "Validate units"],
    bestPractices: ["Preserve row-level provenance", "Avoid forcing aggregation through text similarity"],
    references: [{ label: "Structured & Multimodal", url: "curriculum/advanced/04-structured-multimodal/README.md" }],
  },
  "15 - Adaptive RAG": {
    theory: "Choose the minimum safe retrieval strategy in an adaptive loop.",
    workflow: ["Assess complexity", "Route to simple or complex loop", "Bound depth"],
    bestPractices: ["Use fixed-RAG baselines for comparison", "Save cost/latency for simple queries"],
    references: [{ label: "Adaptive RAG", url: "curriculum/advanced/05-adaptive-rag/README.md" }],
  },
  "16 - Production Operations": {
    theory: "Operational readiness spans traces, freshness, latency, cost, quality SLOs, and rollbacks.",
    workflow: ["Instrument requests", "Detect stale indexes", "Enforce budgets", "Keep rollback path"],
    bestPractices: ["Trace everything", "Refuse deployment on failing golden sets"],
    references: [{ label: "Production Operations", url: "curriculum/advanced/06-production-operations/README.md" }],
  },
};

export const lessonContent = content;
