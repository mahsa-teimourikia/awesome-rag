const content = {
  "01 - RAG Foundations": {
    theory:
      "RAG is an application architecture that connects generation to external evidence selected at request time. A complete RAG system includes ingestion, representation, retrieval, context construction, generation, provenance, and evaluation. Retrieval failures and generation failures must be diagnosed separately; embedding similarity is a relevance signal, not a calibrated probability of truth.",
    workflow: [
      "Define authoritative knowledge sources and provenance",
      "Parse, chunk, represent, and index retrievable evidence",
      "Retrieve and inspect candidate evidence for each query",
      "Construct bounded context while preserving source identity",
      "Generate from the supplied evidence",
      "Evaluate retrieval, grounding, citations, and abstention separately",
    ],
    bestPractices: [
      "Diagnose corpus, parsing, chunking, retrieval, context, and generation failures separately",
      "Preserve source and version metadata from ingestion onward",
      "Treat top-k and context size as tunable engineering budgets",
      "Do not interpret embedding similarity as answer confidence",
      "Prefer the simplest measurable RAG baseline before adding advanced orchestration",
    ],
    references: [
      {
        label: "RAG Foundations",
        url: "curriculum/beginner/01-rag-foundations/README.md",
      },
    ],
  },

  "02 - First Local RAG": {
    theory:
      "The first RAG implementation should optimize for inspectability. A small local pipeline makes documents, metadata, embeddings, scores, retrieved candidates, context, and the final answer visible. This creates a reproducible baseline for separating representation problems, retrieval problems, and generation problems before introducing production infrastructure.",
    workflow: [
      "Create a small corpus with stable document and source IDs",
      "Embed documents with a local embedding model",
      "Build a local vector index",
      "Embed the user query and retrieve top-k candidates",
      "Inspect candidate scores and provenance before generation",
      "Construct context and generate a grounded response",
      "Test the pipeline with a tiny labelled evaluation set",
    ],
    bestPractices: [
      "Inspect retrieval results before changing the generation prompt",
      "Keep source metadata attached to every retrieved item",
      "Record embedding model, corpus version, and retrieval configuration",
      "Distinguish ANN recall from semantic relevance when moving to production indexes",
      "Use frameworks only after understanding the underlying retrieval contracts",
    ],
    references: [
      {
        label: "First Local RAG",
        url: "curriculum/beginner/02-first-local-rag/README.md",
      },
    ],
  },

  "03 - Chunking Lab": {
    theory:
      "Chunking defines the evidence units a retriever can find. Small chunks can improve specificity but lose context; large chunks preserve context but may dilute retrieval signals. Overlap, document structure, parent-child retrieval, semantic boundaries, and multi-representation retrieval should be treated as alternatives to evaluate rather than universal defaults.",
    workflow: [
      "Inspect the source document's logical structure",
      "Create a fixed-size baseline",
      "Compare recursive or structure-aware splitting",
      "Vary chunk size and overlap one parameter at a time",
      "Preserve source, section, version, and chunk metadata",
      "Evaluate configurations with the same labelled queries",
      "Compare retrieval quality, duplicate rate, and context cost",
    ],
    bestPractices: [
      "Choose chunking from measured retrieval behavior, not a universal token count",
      "Use overlap only when it solves boundary failures",
      "Preserve headings, table context, code structure, and source provenance",
      "Consider parent-child retrieval when retrieval and generation need different granularities",
      "Evaluate chunking and context assembly together",
    ],
    references: [
      {
        label: "Chunking Lab",
        url: "curriculum/beginner/03-chunking-lab/README.md",
      },
    ],
  },

  "04 - Citations & Abstention": {
    theory:
      "A trustworthy RAG response needs an explicit link between claims and evidence. Citation quality includes validity, correctness, and completeness. Groundedness is different from factual correctness, and a model can produce a true statement that still violates a strict evidence contract. Abstention is a valid system outcome when authorized evidence is insufficient or conflicting.",
    workflow: [
      "Retrieve authorized evidence with stable evidence IDs",
      "Build an evidence ledger for the request",
      "Assess whether required evidence is sufficient",
      "Generate claims with explicit evidence references",
      "Validate citation identity and claim support",
      "Return an answer, partial answer, clarification request, or abstention",
    ],
    bestPractices: [
      "Construct citations from trusted evidence metadata rather than model memory",
      "Evaluate citation correctness and completeness separately",
      "Treat model self-confidence as insufficient for answerability decisions",
      "Preserve unresolved source conflicts instead of hiding them",
      "Test unanswerable, partially answerable, stale, and conflicting-evidence cases",
    ],
    references: [
      {
        label: "Citations & Abstention",
        url: "curriculum/beginner/04-citations-abstention/README.md",
      },
    ],
  },

  "Capstone - Enterprise RAG": {
    theory:
      "Enterprise RAG is not simply calling a single chain. A robust system requires an ingestion pipeline that respects document structure, a real vector store, explicit orchestration, and quantitative evaluation.",
    workflow: [
      "Load complex, multi-format documents",
      "Apply structure-aware chunking strategies",
      "Index vectors and metadata in a database",
      "Execute structured generation and validation",
    ],
    references: [
      {
        label: "Enterprise RAG Capstone",
        url: "curriculum/beginner/05-capstone-enterprise-rag/README.md",
      },
    ],
  },

  "05 - Retrieval Strategies": {
    theory:
      "Enterprise retrieval is usually a candidate-generation problem with complementary signals. Lexical and sparse methods are strong for exact terms, identifiers, and rare vocabulary; dense retrieval captures semantic similarity and paraphrases. Hybrid retrieval, rank fusion, query expansion, multi-representation search, and late interaction should be added only when evaluation shows the baseline misses important evidence.",
    workflow: [
      "Create labelled query slices for exact-match and semantic cases",
      "Run lexical or sparse retrieval",
      "Run dense retrieval",
      "Fuse ranked candidate lists",
      "Deduplicate or group repeated evidence",
      "Optionally apply a high-precision reranker",
      "Measure Recall@k, MRR, nDCG, latency, and cost",
    ],
    bestPractices: [
      "Keep lexical retrieval for identifiers, error codes, names, and policy numbers",
      "Use RRF when combining ranked lists with incompatible score scales",
      "Treat query expansion as a search hypothesis, not evidence",
      "Tune candidate budgets instead of assuming one top-k value",
      "Justify late interaction or multi-vector search with measured relevance gains",
    ],
    references: [
      {
        label: "Retrieval Strategies",
        url: "curriculum/intermediate/01-retrieval-strategies/README.md",
      },
    ],
  },

  "06 - Metadata & Permissions": {
    theory:
      "Authorization is part of retrieval, not a post-generation filter. Metadata such as tenant, classification, effective date, document type, and version determines which evidence is eligible before relevance ranking. RBAC, ABAC, relationship-aware access, temporal validity, and authorization-aware caching all belong outside model discretion.",
    workflow: [
      "Authenticate the caller",
      "Resolve trusted user, tenant, role, and relationship attributes",
      "Evaluate authorization policy",
      "Construct the trusted retrieval filter",
      "Retrieve and rank only eligible evidence",
      "Preserve policy, filter, evidence, and version metadata for auditability",
    ],
    bestPractices: [
      "Filter before unauthorized content can reach model-visible stages",
      "Never derive tenant or clearance from model-generated arguments alone",
      "Use controlled metadata vocabularies and explicit null semantics",
      "Include authorization-relevant state in retrieval cache keys",
      "Treat cross-tenant leakage as a hard release failure",
    ],
    references: [
      {
        label: "Metadata & Permissions",
        url: "curriculum/intermediate/02-metadata-permissions/README.md",
      },
    ],
  },

  "07 - Query Planning & Reranking": {
    theory:
      "Planning changes what the system searches for; reranking changes the order of candidates already found. Query decomposition, rewriting, expansion, and HyDE can improve candidate recall, while cross-encoders and late-interaction models improve precision on bounded candidate sets. Reranking cannot recover evidence that first-stage retrieval never produced.",
    workflow: [
      "Preserve the original user query and authorization scope",
      "Optionally decompose or rewrite the information need",
      "Generate candidates with one or more retrievers",
      "Fuse and deduplicate candidate lists",
      "Rerank a bounded candidate set",
      "Select context using relevance, diversity, and token budgets",
      "Evaluate candidate recall before and ranking quality after reranking",
    ],
    bestPractices: [
      "Use structured, bounded query plans",
      "Treat HyDE output as a retrieval representation, never as evidence",
      "Measure candidate recall before tuning rerankers",
      "Bound subqueries, candidates, rerank pairs, latency, and cost",
      "Run ablations to prove each retrieval stage adds value",
    ],
    references: [
      {
        label: "Query Planning & Reranking",
        url: "curriculum/intermediate/03-query-reranking/README.md",
      },
    ],
  },

  "08 - RAG Evaluation": {
    theory:
      "Evaluation is the control system for RAG development. A useful test suite separates retrieval, evidence sufficiency, groundedness, citation quality, answerability, task success, latency, and cost. Deterministic IR metrics should be used when relevance labels exist, while LLM judges require explicit rubrics, versioning, calibration, and slice analysis.",
    workflow: [
      "Build a versioned dataset of representative and adversarial cases",
      "Label answerability and required or relevant evidence",
      "Measure retrieval with Recall@k, Precision@k, MRR, or nDCG",
      "Evaluate claim support, citations, completeness, and abstention",
      "Calibrate LLM judges against human-reviewed cases",
      "Run slice analysis and compare against a fixed baseline",
      "Use regression gates in CI/CD and online monitoring after release",
    ],
    bestPractices: [
      "Keep a held-out regression set",
      "Include both answerable and unanswerable questions",
      "Treat LLM judges as measurement instruments, not ground truth",
      "Store per-case results so averages cannot hide critical failures",
      "Hard-fail authorization or citation-identity violations",
    ],
    references: [
      {
        label: "RAG Evaluation",
        url: "curriculum/intermediate/04-evaluation/README.md",
      },
    ],
  },

  "09 - Research Synthesis": {
    theory:
      "Research synthesis is evidence integration rather than generic summarization. A robust workflow plans evidence needs, records source-backed findings, tracks authority and freshness, detects duplicate or correlated sources, preserves contradictions, maps claims to evidence, and performs targeted gap filling before producing cited prose.",
    workflow: [
      "Decompose the research question into evidence needs",
      "Retrieve focused evidence from diverse sources",
      "Normalize findings into structured evidence records",
      "Check authority, freshness, duplication, and source independence",
      "Identify contradictions and unresolved gaps",
      "Map intended claims to supporting evidence IDs",
      "Synthesize with claim-level citations and explicit uncertainty",
    ],
    bestPractices: [
      "Do not treat citation count as source diversity",
      "Prefer primary or authoritative sources for material claims",
      "Preserve contradictory evidence when it cannot be resolved",
      "Keep provenance through intermediate summaries and compression",
      "Bound iterative gap filling and report uncertainty when evidence remains unavailable",
    ],
    references: [
      {
        label: "Research Synthesis",
        url: "curriculum/intermediate/05-research-synthesis/README.md",
      },
    ],
  },

  "10 - Qdrant Search Engineering": {
    theory:
      "Qdrant is retrieval infrastructure rather than the definition of RAG. Collections and points can store payloads, dense vectors, sparse vectors, named vectors, and multivectors. Modern search engineering combines metadata filtering, HNSW ANN search, hybrid fusion, multi-stage prefetch, late-interaction reranking, quantization, and production lifecycle controls.",
    workflow: [
      "Define collection vector and payload schemas",
      "Create stable point, document, and chunk IDs",
      "Index dense, sparse, or multiple representations as required",
      "Apply trusted payload filters during search",
      "Use hybrid fusion or multi-stage prefetch when evaluation justifies it",
      "Measure ANN recall separately from semantic relevance",
      "Plan updates, deletion, migration, backup, and index-version lifecycle",
    ],
    bestPractices: [
      "Distinguish ANN approximation loss from embedding or relevance failure",
      "Index frequently filtered payload fields",
      "Use stable IDs for deterministic updates and provenance",
      "Benchmark HNSW and quantization settings on real workloads",
      "Do not confuse a local in-memory lab with production availability and security",
    ],
    references: [
      {
        label: "Qdrant Search Engineering",
        url: "curriculum/intermediate/06-qdrant-local/README.md",
      },
    ],
  },

  "11 - Corrective RAG": {
    theory:
      "Corrective RAG evaluates retrieved evidence before generation and selects from a bounded set of recovery actions when evidence is weak. Recovery can include rewriting, alternate retrievers, clarification, approved external sources, or abstention. Correction is a policy-controlled evidence-recovery process, not an unbounded retry loop.",
    workflow: [
      "Retrieve an initial authorized candidate set",
      "Grade evidence sufficiency, authority, freshness, and coverage",
      "Accept strong evidence or select an approved recovery route",
      "Enforce attempt, latency, cost, and authorization budgets",
      "Re-grade recovered evidence",
      "Generate only when evidence is sufficient; otherwise abstain or escalate",
    ],
    bestPractices: [
      "Use finite recovery graphs with explicit terminal states",
      "Do not automatically widen to public web search",
      "Measure false acceptance and false abstention",
      "Record route, evidence IDs, attempts, latency, and cost",
      "Compare corrective RAG against a fixed-RAG baseline",
    ],
    references: [
      {
        label: "Corrective RAG",
        url: "curriculum/advanced/01-corrective-rag/README.md",
      },
    ],
  },

  "12 - GraphRAG": {
    theory:
      "GraphRAG is useful when relationships are part of the information need. Trustworthy graph retrieval depends on canonical entities, typed and directional relationships, bounded traversal, provenance on every fact or edge, and source-backed text where users need verification. Graph retrieval complements rather than universally replaces text retrieval.",
    workflow: [
      "Extract or define canonical entities",
      "Create typed relationships with source provenance",
      "Resolve aliases and entity identity",
      "Apply authorization before graph traversal",
      "Traverse only permitted relation types and bounded hop counts",
      "Retrieve supporting source spans for graph facts",
      "Generate answers from verified paths and provenance",
    ],
    bestPractices: [
      "Preserve edge direction when relation semantics require it",
      "Store source, version, and validity metadata with relationships",
      "Bound hops, facts, and high-degree expansion",
      "Evaluate entity resolution and path correctness separately",
      "Use graph retrieval only for query classes that benefit from explicit relationships",
    ],
    references: [
      {
        label: "GraphRAG",
        url: "curriculum/advanced/02-graphrag/README.md",
      },
    ],
  },

  "13 - Agentic RAG": {
    theory:
      "Agentic RAG gives a model bounded discretion to choose the next evidence tool when the useful next step depends on prior observations. Tool selection is not authorization. The application must enforce schemas, permissions, approval, budgets, and terminal states, while traces record observable tool decisions and evidence rather than hidden chain-of-thought.",
    workflow: [
      "Determine whether a deterministic workflow is sufficient",
      "Expose only narrow, typed, policy-approved tools",
      "Let the model propose a permitted tool call",
      "Validate arguments and authorization outside the model",
      "Require approval for material side effects",
      "Record tool results as evidence or receipts",
      "Terminate within turn, tool-call, latency, and cost budgets",
    ],
    bestPractices: [
      "Prefer deterministic workflows when the sequence is already known",
      "Separate read, propose, and execute tool classes",
      "Keep authorization and approval outside model discretion",
      "Treat tool outputs as untrusted data",
      "Evaluate trajectories, repeated calls, policy violations, latency, and cost",
    ],
    references: [
      {
        label: "Agentic RAG",
        url: "curriculum/advanced/03-agentic-rag/README.md",
      },
    ],
  },

  "14 - Structured & Multimodal RAG": {
    theory:
      "Structured and multimodal RAG routes each operation to an evidence mechanism appropriate to its data type. Exact calculations should use deterministic code, SQL, or typed tools; OCR should retain source regions and confidence; visual interpretations should preserve image locators; and model-derived inference should be distinguished from computed or directly observed facts.",
    workflow: [
      "Classify the information need by operation and modality",
      "Apply authorization to the underlying structured or unstructured source",
      "Use deterministic queries or calculations for exact structured facts",
      "Use OCR for extractable text and preserve page or region provenance",
      "Use multimodal models when layout or visual interpretation is required",
      "Label outputs as computed, observed, or inferred",
      "Evaluate each modality using appropriate metrics",
    ],
    bestPractices: [
      "Prefer constrained structured operations over arbitrary generated code",
      "Do not use an LLM as the source of truth for exact arithmetic",
      "Preserve row, cell, page, frame, and bounding-box provenance",
      "Treat OCR confidence as extraction uncertainty, not final answer confidence",
      "Keep observation and interpretation separate",
    ],
    references: [
      {
        label: "Structured & Multimodal RAG",
        url: "curriculum/advanced/04-structured-multimodal/README.md",
      },
    ],
  },

  "15 - Adaptive RAG": {
    theory:
      "Adaptive RAG selects the minimum evidence strategy appropriate to a request before or around retrieval. A router can use deterministic rules, classifiers, structured LLM output, or combined policy. Routing is separate from authorization and can be composed with Corrective RAG so the system first selects a route and then evaluates whether that route produced sufficient evidence.",
    workflow: [
      "Identify route-relevant signals such as source, freshness, modality, or complexity",
      "Select among direct, internal retrieval, graph, structured, multimodal, or approved external routes",
      "Authorize the selected route independently",
      "Execute retrieval or computation within route-specific budgets",
      "Optionally grade evidence with a corrective controller",
      "Record route, quality, latency, cost, and terminal outcome",
    ],
    bestPractices: [
      "Use the simplest router that performs well on labelled route cases",
      "Do not use query length alone as a complexity signal",
      "Keep route selection separate from authorization",
      "Measure high-risk misroutes, not only overall accuracy",
      "Compare adaptive routing against a fixed-route baseline",
    ],
    references: [
      {
        label: "Adaptive RAG",
        url: "curriculum/advanced/05-adaptive-rag/README.md",
      },
    ],
  },

  "16 - Production Operations": {
    theory:
      "Production RAG combines service reliability with retrieval quality, evidence freshness, security, cost, and recoverability. Stage-level tracing, versioned release bundles, offline and online evaluation, release gates, canaries, rollback criteria, safe degradation, and incident-driven regression tests are required to operate the system as a production service.",
    workflow: [
      "Instrument authorization, retrieval, reranking, generation, and verification stages",
      "Track corpus, index, model, prompt, policy, and evaluator versions",
      "Run offline regression and safety gates before release",
      "Canary or shadow new configurations",
      "Monitor quality, freshness, latency, cost, and failure signals",
      "Rollback when predefined criteria are violated",
      "Turn incidents and production failures into regression cases",
    ],
    bestPractices: [
      "Separate readiness, freshness, offline quality, and online behavior",
      "Use stage-level spans to localize latency and quality regressions",
      "Use provider-reported usage and include retrieval, reranking, verification, external calls, and retries in route cost",
      "Version the complete RAG release bundle for reproducibility and rollback",
      "Degrade optional capability without weakening authorization or evidence controls",
    ],
    references: [
      {
        label: "Production Operations",
        url: "curriculum/advanced/06-production-operations/README.md",
      },
    ],
  },
};

export const lessonContent = content;
