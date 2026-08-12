export const learningPath = [
  { id: "beginner", level: "Beginner", tone: "beginner", outcome: "Build a trustworthy local RAG assistant.", modules: [
    { id: "b1", title: "RAG foundations", description: "Understand the pipeline and retrieved evidence.", material: "../curriculum/beginner/01-rag-foundations/README.md", notebook: "../curriculum/beginner/01-rag-foundations/rag_foundations.ipynb", category: "01 - RAG Foundations", minutes: 20, technologies: ["Theory"] },
    { id: "b2", title: "First local baseline", description: "Retrieve inspectable evidence and abstain safely.", material: "../curriculum/beginner/02-first-local-rag/README.md", notebook: "../curriculum/beginner/02-first-local-rag/02_first_local_rag.ipynb", category: "02 - First Local Baseline", minutes: 75, technologies: ["Python", "Lexical"] },
    { id: "b3", title: "Chunking lab", description: "Compare fixed and structure-aware chunks.", material: "../curriculum/beginner/03-chunking-lab/README.md", notebook: "../curriculum/beginner/03-chunking-lab/03_chunking_lab.ipynb", category: "03 - Chunking Lab", minutes: 80, technologies: ["Chunking"] },
    { id: "b4", title: "Citations & abstention", description: "Preserve provenance and explain uncertainty.", material: "../curriculum/beginner/04-citations-abstention/README.md", notebook: "../curriculum/beginner/04-citations-abstention/04_citations_abstention.ipynb", category: "04 - Citations & Abstention", minutes: 80, technologies: ["Citations", "Abstention"] }
  ]},
  { id: "intermediate", level: "Intermediate", tone: "intermediate", outcome: "Improve and measure retrieval quality.", modules: [
    { id: "i1", title: "Retrieval strategies", description: "Compare BM25, dense & hybrid.", material: "../curriculum/intermediate/01-retrieval-strategies/README.md", notebook: "../curriculum/intermediate/01-retrieval-strategies/01_retrieval_strategies.ipynb", category: "05 - Retrieval Strategies", minutes: 45, technologies: ["Hybrid Search"] },
    { id: "i2", title: "Metadata permissions", description: "Authorize before retrieval.", material: "../curriculum/intermediate/02-metadata-permissions/README.md", notebook: "../curriculum/intermediate/02-metadata-permissions/02_metadata_permissions.ipynb", category: "06 - Metadata Permissions", minutes: 40, technologies: ["ACLs", "Security"] },
    { id: "i3", title: "Query reranking", description: "Improve recall and candidate ordering.", material: "../curriculum/intermediate/03-query-reranking/README.md", notebook: "../curriculum/intermediate/03-query-reranking/03_query_reranking.ipynb", category: "07 - Query Reranking", minutes: 45, technologies: ["Reranking"] },
    { id: "i4", title: "Evaluation lab", description: "Build golden sets and regression gates.", material: "../curriculum/intermediate/04-evaluation/README.md", notebook: "../curriculum/intermediate/04-evaluation/01_building_eval_datasets.ipynb", category: "08 - Evaluation Lab", minutes: 45, technologies: ["Recall@k", "Metrics"] },
    { id: "i5", title: "Research synthesis", description: "Use multi-query evidence.", material: "../curriculum/intermediate/05-research-synthesis/README.md", notebook: "../curriculum/intermediate/05-research-synthesis/05_research_synthesis.ipynb", category: "09 - Research Synthesis", minutes: 60, technologies: ["Multi-query", "Claims"] },
    { id: "i6", title: "Local Qdrant & embeddings", description: "Run vector search with payload filters.", material: "../curriculum/intermediate/06-qdrant-local/README.md", notebook: "../curriculum/intermediate/06-qdrant-local/06_qdrant_local.ipynb", category: "10 - Local Qdrant & Embeddings", minutes: 60, technologies: ["Qdrant", "Embeddings"] }
  ]},
  { id: "advanced", level: "Advanced", tone: "advanced", outcome: "Design recoverable, agentic, and operable RAG systems.", modules: [
    { id: "a1", title: "Corrective RAG", description: "Recover from weak retrieval with bounded routes.", material: "../curriculum/advanced/01-corrective-rag/README.md", notebook: "../curriculum/advanced/01-corrective-rag/01_corrective_rag.ipynb", category: "11 - Corrective RAG", minutes: 60, technologies: ["Routing", "Recovery"] },
    { id: "a2", title: "GraphRAG & entity retrieval", description: "Traverse entities and preserve fact provenance.", material: "../curriculum/advanced/02-graphrag/README.md", notebook: "../curriculum/advanced/02-graphrag/02_graphrag.ipynb", category: "12 - GraphRAG", minutes: 60, technologies: ["Graph", "Traversal"] },
    { id: "a3", title: "Agentic RAG & tool boundaries", description: "Route tools with explicit approval boundaries.", material: "../curriculum/advanced/03-agentic-rag/README.md", notebook: "../curriculum/advanced/03-agentic-rag/03_agentic_rag.ipynb", category: "13 - Agentic RAG", minutes: 60, technologies: ["Agents", "Tools"] },
    { id: "a4", title: "Structured & multimodal RAG", description: "Handle tables, images, and OCR.", material: "../curriculum/advanced/04-structured-multimodal/README.md", notebook: "../curriculum/advanced/04-structured-multimodal/04_structured_multimodal.ipynb", category: "14 - Structured & Multimodal RAG", minutes: 60, technologies: ["SQL", "OCR"] },
    { id: "a5", title: "Adaptive RAG", description: "Choose the minimum safe retrieval strategy.", material: "../curriculum/advanced/05-adaptive-rag/README.md", notebook: "../curriculum/advanced/05-adaptive-rag/README.md", category: "15 - Adaptive RAG", minutes: 60, technologies: ["Adaptive"] },
    { id: "a6", title: "Production operations", description: "Operate with traces, budgets, and readiness.", material: "../curriculum/advanced/06-production-operations/README.md", notebook: "../curriculum/advanced/06-production-operations/README.md", category: "16 - Production Operations", minutes: 60, technologies: ["Tracing", "Budgets"] }
  ]},
];

const questionIdsByCategory = {
  "01 - RAG Foundations": ["b1-foundations"],
  "02 - First Local Baseline": ["b2-baseline"],
  "03 - Chunking Lab": ["b3-chunking"],
  "04 - Citations & Abstention": ["b4-citations"],
  "05 - Retrieval Strategies": ["i1-retrieval"],
  "06 - Metadata Permissions": ["i2-metadata"],
  "07 - Query Reranking": ["i3-reranking"],
  "08 - Evaluation Lab": ["i4-evaluation"],
  "09 - Research Synthesis": ["i5-research"],
  "10 - Local Qdrant & Embeddings": ["i6-qdrant"],
  "11 - Corrective RAG": ["a1-corrective"],
  "12 - GraphRAG": ["a2-graphrag"],
  "13 - Agentic RAG": ["a3-agentic"],
  "14 - Structured & Multimodal RAG": ["a4-multimodal"],
  "15 - Adaptive RAG": ["a5-adaptive"],
  "16 - Production Operations": ["a6-operations"],
};

export const allLessons = learningPath.flatMap((track) => track.modules.map((module) => ({ ...module, level: track.level, tone: track.tone, trackId: track.id, questionIds: questionIdsByCategory[module.category] ?? [] })));
