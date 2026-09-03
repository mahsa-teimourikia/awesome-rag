export const learningPath = [
  {
    id: "beginner",
    level: "Beginner",
    tone: "beginner",
    outcome:
      "Build an inspectable RAG system, understand its evidence flow, and diagnose failures before adding retrieval complexity.",
    modules: [
      {
        id: "b1",
        title: "RAG Foundations",
        description:
          "Understand RAG as an evidence architecture: ingestion, retrieval, context construction, generation, provenance, and failure decomposition.",
        material:
          "../curriculum/beginner/01-rag-foundations/README.md",
        notebook:
          "../curriculum/beginner/01-rag-foundations/rag_foundations.ipynb",
        category: "01 - RAG Foundations",
        minutes: 90,
        technologies: [
          "RAG Architecture",
          "Retrieval",
          "Provenance",
          "Evaluation",
        ],
      },
      {
        id: "b2",
        title: "First Local RAG",
        description:
          "Build a small local semantic RAG pipeline and inspect documents, embeddings, retrieved evidence, metadata, and context before generation.",
        material:
          "../curriculum/beginner/02-first-local-rag/README.md",
        notebook:
          "../curriculum/beginner/02-first-local-rag/02_first_local_rag.ipynb",
        category: "02 - First Local RAG",
        minutes: 120,
        technologies: [
          "Python",
          "Embeddings",
          "Chroma",
          "Semantic Search",
        ],
      },
      {
        id: "b3",
        title: "Chunking Lab",
        description:
          "Explore how chunk boundaries, size, overlap, structure, metadata, and retrieval granularity affect evidence quality.",
        material:
          "../curriculum/beginner/03-chunking-lab/README.md",
        notebook:
          "../curriculum/beginner/03-chunking-lab/03_chunking_lab.ipynb",
        category: "03 - Chunking Lab",
        minutes: 120,
        technologies: [
          "Chunking",
          "Text Splitters",
          "Metadata",
          "Parent-Child Retrieval",
        ],
      },
      {
        id: "b4",
        title: "Citations & Abstention",
        description:
          "Preserve evidence identity, map claims to sources, validate citations, and abstain when the available evidence is insufficient.",
        material:
          "../curriculum/beginner/04-citations-abstention/README.md",
        notebook:
          "../curriculum/beginner/04-citations-abstention/04_citations_abstention.ipynb",
        category: "04 - Citations & Abstention",
        minutes: 120,
        technologies: [
          "Citations",
          "Grounding",
          "Abstention",
          "Evidence Validation",
        ],
      },
      {
        id: "b5",
        title: "Enterprise RAG Capstone",
        description:
          "Build an end-to-end Enterprise RAG system using a real vector store, embeddings, LLM, and evaluation dataset.",
        material:
          "../curriculum/beginner/05-capstone-enterprise-rag/README.md",
        notebook:
          "../curriculum/beginner/05-capstone-enterprise-rag/05_enterprise_rag_capstone.ipynb",
        category: "Capstone - Enterprise RAG",
        minutes: 180,
        technologies: [
          "Vector Databases",
          "Embeddings",
          "LLM Generation",
          "Evaluation Metrics",
        ],
      },
    ],
  },

  {
    id: "intermediate",
    level: "Intermediate",
    tone: "intermediate",
    outcome:
      "Engineer retrieval quality with hybrid search, authorization, reranking, evaluation, synthesis, and production-oriented vector search.",
    modules: [
      {
        id: "i1",
        title: "Retrieval Strategies",
        description:
          "Compare lexical, dense, hybrid, multi-query, multi-representation, and late-interaction retrieval strategies using measurable retrieval quality.",
        material:
          "../curriculum/intermediate/01-retrieval-strategies/README.md",
        notebook:
          "../curriculum/intermediate/01-retrieval-strategies/01_retrieval_strategies.ipynb",
        category: "05 - Retrieval Strategies",
        minutes: 150,
        technologies: [
          "BM25",
          "Dense Retrieval",
          "Hybrid Search",
          "RRF",
          "Late Interaction",
        ],
      },
      {
        id: "i2",
        title: "Metadata & Permissions",
        description:
          "Constrain the candidate space with trusted tenant, classification, temporal, and authorization metadata before relevance ranking.",
        material:
          "../curriculum/intermediate/02-metadata-permissions/README.md",
        notebook:
          "../curriculum/intermediate/02-metadata-permissions/02_metadata_permissions.ipynb",
        category: "06 - Metadata & Permissions",
        minutes: 120,
        technologies: [
          "Metadata Filters",
          "RBAC",
          "ABAC",
          "Tenant Isolation",
          "Security",
        ],
      },
      {
        id: "i3",
        title: "Query Planning & Reranking",
        description:
          "Improve complex retrieval through query decomposition, rewriting, candidate generation, cross-encoder reranking, and bounded retrieval cascades.",
        material:
          "../curriculum/intermediate/03-query-reranking/README.md",
        notebook:
          "../curriculum/intermediate/03-query-reranking/03_query_reranking.ipynb",
        category: "07 - Query Planning & Reranking",
        minutes: 150,
        technologies: [
          "Query Planning",
          "HyDE",
          "Cross-Encoders",
          "Reranking",
          "ColBERT",
        ],
      },
      {
        id: "i4",
        title: "RAG Evaluation",
        description:
          "Build evaluation datasets and measure retrieval, grounding, citation quality, answerability, abstention, latency, cost, and regressions.",
        material:
          "../curriculum/intermediate/04-evaluation/README.md",
        notebook:
          "../curriculum/intermediate/04-evaluation/01_building_eval_datasets.ipynb",
        category: "08 - RAG Evaluation",
        minutes: 240,
        technologies: [
          "Recall@k",
          "MRR",
          "nDCG",
          "RAGAS",
          "LLM Judges",
          "Regression Testing",
        ],
      },
      {
        id: "i5",
        title: "Research Synthesis",
        description:
          "Build multi-source answers using evidence planning, source authority, contradiction handling, claim-evidence maps, and citation-preserving synthesis.",
        material:
          "../curriculum/intermediate/05-research-synthesis/README.md",
        notebook:
          "../curriculum/intermediate/05-research-synthesis/05_research_synthesis.ipynb",
        category: "09 - Research Synthesis",
        minutes: 150,
        technologies: [
          "Evidence Tables",
          "Map-Reduce",
          "Refine",
          "Conflict Detection",
          "Research Synthesis",
        ],
      },
      {
        id: "i6",
        title: "Qdrant Search Engineering",
        description:
          "Map retrieval theory to Qdrant using dense and sparse vectors, payload filters, HNSW, hybrid fusion, multivectors, and multi-stage search.",
        material:
          "../curriculum/intermediate/06-qdrant-local/README.md",
        notebook:
          "../curriculum/intermediate/06-qdrant-local/06_qdrant_local.ipynb",
        category: "10 - Qdrant Search Engineering",
        minutes: 150,
        technologies: [
          "Qdrant",
          "HNSW",
          "Hybrid Search",
          "Payload Filters",
          "Multivectors",
          "Prefetch",
        ],
      },
    ],
  },

  {
    id: "advanced",
    level: "Advanced",
    tone: "advanced",
    outcome:
      "Design bounded adaptive, corrective, graph-based, agentic, multimodal, and production RAG systems with explicit control and evaluation boundaries.",
    modules: [
      {
        id: "a1",
        title: "Corrective RAG",
        description:
          "Detect weak retrieval and recover through bounded, policy-approved routes such as rewriting, alternate retrieval, clarification, or abstention.",
        material:
          "../curriculum/advanced/01-corrective-rag/README.md",
        notebook:
          "../curriculum/advanced/01-corrective-rag/01_corrective_rag.ipynb",
        category: "11 - Corrective RAG",
        minutes: 150,
        technologies: [
          "CRAG",
          "LangGraph",
          "Evidence Grading",
          "Recovery Routing",
          "Abstention",
        ],
      },
      {
        id: "a2",
        title: "GraphRAG",
        description:
          "Retrieve relationship evidence through canonical entities, directional graph facts, bounded traversal, provenance, and graph-plus-text retrieval.",
        material:
          "../curriculum/advanced/02-graphrag/README.md",
        notebook:
          "../curriculum/advanced/02-graphrag/02_graphrag.ipynb",
        category: "12 - GraphRAG",
        minutes: 150,
        technologies: [
          "GraphRAG",
          "Knowledge Graphs",
          "NetworkX",
          "Entity Resolution",
          "Graph Traversal",
        ],
      },
      {
        id: "a3",
        title: "Agentic RAG",
        description:
          "Use bounded model-driven tool selection only when runtime evidence determines the next useful action, while keeping authorization and approvals deterministic.",
        material:
          "../curriculum/advanced/03-agentic-rag/README.md",
        notebook:
          "../curriculum/advanced/03-agentic-rag/03_agentic_rag.ipynb",
        category: "13 - Agentic RAG",
        minutes: 150,
        technologies: [
          "Agents",
          "Tool Calling",
          "LangGraph",
          "Human Approval",
          "Trajectory Evaluation",
        ],
      },
      {
        id: "a4",
        title: "Structured & Multimodal RAG",
        description:
          "Route structured calculations, OCR observations, visual interpretation, tables, and narrative retrieval through modality-appropriate evidence contracts.",
        material:
          "../curriculum/advanced/04-structured-multimodal/README.md",
        notebook:
          "../curriculum/advanced/04-structured-multimodal/04_structured_multimodal.ipynb",
        category: "14 - Structured & Multimodal RAG",
        minutes: 150,
        technologies: [
          "Structured Data",
          "SQL",
          "OCR",
          "Vision Models",
          "Multimodal RAG",
        ],
      },
      {
        id: "a5",
        title: "Adaptive RAG",
        description:
          "Route each request to the minimum evidence strategy that can satisfy source, freshness, modality, quality, authorization, latency, and cost requirements.",
        material:
          "../curriculum/advanced/05-adaptive-rag/README.md",
        notebook:
          "../curriculum/advanced/05-adaptive-rag/05_adaptive_rag.ipynb",
        category: "15 - Adaptive RAG",
        minutes: 300,
        technologies: [
          "Adaptive RAG",
          "Routing",
          "LangGraph",
          "Classifiers",
          "Corrective RAG",
        ],
      },
      {
        id: "a6",
        title: "Production Operations",
        description:
          "Operate RAG with stage-level tracing, release bundles, regression gates, canaries, freshness monitoring, cost controls, rollback, and safe degradation.",
        material:
          "../curriculum/advanced/06-production-operations/README.md",
        notebook:
          "../curriculum/advanced/06-production-operations/06_production_operations.ipynb",
        category: "16 - Production Operations",
        minutes: 270,
        technologies: [
          "Observability",
          "Tracing",
          "Release Gates",
          "Canary Releases",
          "Rollback",
          "Cost Monitoring",
        ],
      },
    ],
  },
];

const questionIdsByCategory = {
  "01 - RAG Foundations": [
    "b1-q1",
    "b1-q2",
    "b1-q3",
  ],

  "02 - First Local RAG": [
    "b2-q1",
    "b2-q2",
    "b2-q3",
  ],

  "03 - Chunking Lab": [
    "b3-q1",
    "b3-q2",
    "b3-q3",
  ],

  "04 - Citations & Abstention": [
    "b4-q1",
    "b4-q2",
    "b4-q3",
  ],

  "05 - Retrieval Strategies": [
    "i1-q1",
    "i1-q2",
    "i1-q3",
  ],

  "06 - Metadata & Permissions": [
    "i2-q1",
    "i2-q2",
    "i2-q3",
  ],

  "07 - Query Planning & Reranking": [
    "i3-q1",
    "i3-q2",
    "i3-q3",
  ],

  "08 - RAG Evaluation": [
    "i4-q1",
    "i4-q2",
    "i4-q3",
  ],

  "09 - Research Synthesis": [
    "i5-q1",
    "i5-q2",
    "i5-q3",
  ],

  "10 - Qdrant Search Engineering": [
    "i6-q1",
    "i6-q2",
    "i6-q3",
  ],

  "11 - Corrective RAG": [
    "a1-q1",
    "a1-q2",
    "a1-q3",
  ],

  "12 - GraphRAG": [
    "a2-q1",
    "a2-q2",
    "a2-q3",
  ],

  "13 - Agentic RAG": [
    "a3-q1",
    "a3-q2",
    "a3-q3",
  ],

  "14 - Structured & Multimodal RAG": [
    "a4-q1",
    "a4-q2",
    "a4-q3",
  ],

  "15 - Adaptive RAG": [
    "a5-q1",
    "a5-q2",
    "a5-q3",
  ],

  "16 - Production Operations": [
    "a6-q1",
    "a6-q2",
    "a6-q3",
  ],
};

export const allLessons = learningPath.flatMap((track) =>
  track.modules.map((module) => ({
    ...module,
    level: track.level,
    tone: track.tone,
    trackId: track.id,
    questionIds: questionIdsByCategory[module.category] ?? [],
  })),
);
