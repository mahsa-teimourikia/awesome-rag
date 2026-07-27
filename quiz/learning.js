export const learningPath = [
  { level: "Beginner", tone: "beginner", outcome: "Build a cited local RAG assistant.", modules: [
    ["RAG foundations", "Understand the pipeline and groundedness.", "../curriculum/beginner/01-rag-foundations/README.md", "../notebooks/beginner/01_first_local_rag.ipynb", "Foundations"],
    ["First local baseline", "Retrieve inspectable evidence and abstain safely.", "../curriculum/beginner/02-first-local-rag/README.md", "../notebooks/beginner/01_first_local_rag.ipynb", "Foundations"],
    ["Chunking lab", "Compare fixed-size and structure-aware chunks.", "../curriculum/beginner/03-chunking-lab/README.md", "../notebooks/beginner/02_chunking_lab.ipynb", "Ingestion"],
    ["Citations and abstention", "Preserve provenance and explain uncertainty.", "../curriculum/beginner/04-citations-abstention/README.md", "../notebooks/beginner/03_citations_abstention.ipynb", "Generation"],
    ["Documentation assistant", "Combine the beginner patterns in a capstone.", "../use-cases/documentation-assistant/README.md", "../use-cases/documentation-assistant/documentation_assistant.ipynb", "Foundations"],
  ]},
  { level: "Intermediate", tone: "intermediate", outcome: "Improve and measure retrieval quality.", modules: [
    ["Retrieval strategies", "Compare BM25, dense adapters, and fusion.", "../curriculum/intermediate/01-retrieval-strategies/README.md", "../curriculum/intermediate/01-retrieval-strategies/retrieval_strategies.ipynb", "Retrieval"],
    ["Metadata permissions", "Authorize before retrieval and context construction.", "../curriculum/intermediate/02-metadata-permissions/README.md", "../curriculum/intermediate/02-metadata-permissions/metadata_permissions.ipynb", "Security"],
    ["Query rewriting and reranking", "Improve recall and candidate ordering.", "../curriculum/intermediate/03-query-reranking/README.md", "../curriculum/intermediate/03-query-reranking/query_reranking.ipynb", "Retrieval"],
    ["Evaluation lab", "Build golden sets and regression gates.", "../curriculum/intermediate/04-evaluation/README.md", "../curriculum/intermediate/04-evaluation/evaluation.ipynb", "Evaluation"],
    ["Research synthesis", "Use multi-query evidence and claim citations.", "../curriculum/intermediate/05-research-synthesis/README.md", "../curriculum/intermediate/05-research-synthesis/research_synthesis.ipynb", "Evaluation"],
    ["Customer support", "Apply retrieval, permissions, and escalation.", "../use-cases/customer-support/README.md", "../use-cases/customer-support/customer_support.ipynb", "Security"],
  ]},
  { level: "Advanced", tone: "advanced", outcome: "Design recoverable, agentic, and operable RAG systems.", modules: [
    ["Corrective RAG", "Recover from weak retrieval with bounded routes.", "../curriculum/advanced/01-corrective-rag/README.md", "../curriculum/advanced/01-corrective-rag/corrective_rag.ipynb", "Retrieval"],
    ["GraphRAG", "Traverse entities and preserve fact provenance.", "../curriculum/advanced/02-graphrag/README.md", "../curriculum/advanced/02-graphrag/graph_rag.ipynb", "Retrieval"],
    ["Agentic RAG", "Route tools with explicit approval boundaries.", "../curriculum/advanced/03-agentic-rag/README.md", "../curriculum/advanced/03-agentic-rag/agentic_rag.ipynb", "Security"],
    ["Structured and multimodal", "Handle tables, images, and OCR as typed evidence.", "../curriculum/advanced/04-structured-multimodal/README.md", "../curriculum/advanced/04-structured-multimodal/structured_multimodal.ipynb", "Retrieval"],
    ["Production operations", "Operate with traces, budgets, freshness, and readiness.", "../curriculum/advanced/05-production-operations/README.md", "../curriculum/advanced/05-production-operations/production_operations.ipynb", "Operations"],
  ]},
];
