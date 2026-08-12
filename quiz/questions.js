export const questions = [
  {
    id: "b1-foundations",
    category: "01 - RAG Foundations",
    prompt: "Which statements accurately describe retrieval-augmented generation?",
    options: [
      "It retrieves external evidence at answer time.",
      "It requires retraining the language model whenever a document changes.",
      "It can ground answers in private or frequently updated information.",
      "It guarantees that every generated claim is factual.",
    ],
    correct: [0, 2],
    explanation:
      "RAG supplies retrieved evidence at runtime, so the corpus can change without retraining model weights. Retrieval and generation can still fail, so grounding must be evaluated rather than assumed.",
    source: {
      label: "RAG Foundations",
      url: "curriculum/beginner/01-rag-foundations/README.md",
    },
  },
  {
    id: "b2-baseline",
    category: "02 - First Local Baseline",
    prompt: "What is the primary benefit of building a deterministic lexical baseline before adding embeddings?",
    options: [
      "It makes retrieval failures (like synonym mismatch) fully inspectable.",
      "Lexical search is always more accurate than semantic search.",
      "It allows you to evaluate your context bounds and abstention policy explicitly.",
      "It eliminates the need for an LLM.",
    ],
    correct: [0, 2],
    explanation:
      "A deterministic baseline lets you clearly see what matched and why, making it easy to tune abstention policies and context limits before introducing the opacity of embeddings.",
    source: {
      label: "First Local RAG",
      url: "curriculum/beginner/02-first-local-rag/README.md",
    },
  },
  {
    id: "b3-chunking",
    category: "03 - Chunking Lab",
    prompt: "Which chunking practices generally improve retrieval quality?",
    options: [
      "Split on document structure such as headings and sections.",
      "Keep enough local context for a chunk to make sense independently.",
      "Use the largest possible chunk for every corpus.",
      "Evaluate multiple chunk sizes against representative questions.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Useful chunks balance specificity with sufficient context. Structure-aware splitting and evaluation are more reliable than assuming one maximum-sized chunk works for every document type.",
    source: {
      label: "Chunking Lab",
      url: "curriculum/beginner/03-chunking-lab/README.md",
    },
  },
  {
    id: "b4-citations",
    category: "04 - Citations & Abstention",
    prompt: "Which generation behaviors make a grounded RAG answer more trustworthy?",
    options: [
      "Cite the exact sources supporting important claims.",
      "Abstain when the retrieved context is insufficient.",
      "Fill evidence gaps using plausible-sounding model knowledge.",
      "Keep the supplied context focused and relevant.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Citations, abstention, and focused context reduce unsupported claims. A model should not silently replace missing evidence with plausible text when the application promises grounded answers.",
    source: {
      label: "Citations & Abstention",
      url: "curriculum/beginner/04-citations-abstention/README.md",
    },
  },
  {
    id: "i1-retrieval",
    category: "05 - Retrieval Strategies",
    prompt: "When does lexical retrieval often outperform dense retrieval?",
    options: [
      "Queries containing exact error codes or product identifiers.",
      "Queries centered on rare names or legal citations.",
      "Queries whose wording differs greatly from the relevant passage.",
      "Queries requiring exact dates or version strings.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Lexical retrieval is strong when exact tokens matter. Dense retrieval is often better at paraphrase and semantic similarity, which is why hybrid systems combine the two.",
    source: {
      label: "Retrieval Strategies",
      url: "curriculum/intermediate/01-retrieval-strategies/README.md",
    },
  },
  {
    id: "i2-metadata",
    category: "06 - Metadata Permissions",
    prompt: "How should document access control work in a multi-user RAG system?",
    options: [
      "Filter unauthorized documents before their contents reach the model.",
      "Include tenant or permission metadata in retrieval filters.",
      "Ask the model not to mention unauthorized passages after retrieval.",
      "Test permission-boundary queries in the evaluation set.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Authorization is a retrieval boundary, not a prompt instruction. Unauthorized content must never enter the model context, and boundary cases should be tested continuously.",
    source: {
      label: "Metadata Permissions",
      url: "curriculum/intermediate/02-metadata-permissions/README.md",
    },
  },
  {
    id: "i3-reranking",
    category: "07 - Query Reranking",
    prompt: "What does a two-stage retrieve-and-rerank pipeline do?",
    options: [
      "Retrieves a broad candidate set with a relatively inexpensive method.",
      "Applies a stronger relevance model to the smaller candidate set.",
      "Reranks every document in the corpus with a cross-encoder.",
      "Improves the ordering of plausible retrieved evidence.",
    ],
    correct: [0, 1, 3],
    explanation:
      "The first stage emphasizes recall and speed. A more accurate, expensive reranker then improves precision over a small candidate set rather than scoring the full corpus.",
    source: {
      label: "Query Reranking",
      url: "curriculum/intermediate/03-query-reranking/README.md",
    },
  },
  {
    id: "i4-evaluation",
    category: "08 - Evaluation Lab",
    prompt: "Which metrics primarily evaluate the retrieval stage?",
    options: [
      "Recall@k",
      "Mean reciprocal rank (MRR)",
      "Normalized discounted cumulative gain (nDCG)",
      "Writing-style preference",
    ],
    correct: [0, 1, 2],
    explanation:
      "Recall@k, MRR, and nDCG measure whether relevant evidence is retrieved and ranked well. Writing-style preference evaluates generation behavior, not retrieval.",
    source: {
      label: "Evaluation Lab",
      url: "curriculum/intermediate/04-evaluation/README.md",
    },
  },
  {
    id: "i5-research",
    category: "09 - Research Synthesis",
    prompt: "Why should you use multiple focused queries for research synthesis?",
    options: [
      "To prevent framing bias from a single initial query.",
      "To intentionally duplicate context for the LLM.",
      "To retrieve findings, limitations, and counterpoints independently.",
      "To reduce the number of API calls.",
    ],
    correct: [0, 2],
    explanation:
      "Using multiple focused queries reduces framing bias and ensures you retrieve diverse evidence (like limitations or counterpoints) rather than just evidence that confirms the premise.",
    source: {
      label: "Research Synthesis",
      url: "curriculum/intermediate/05-research-synthesis/README.md",
    },
  },
  {
    id: "i6-qdrant",
    category: "10 - Local Qdrant & Embeddings",
    prompt: "When adopting a vector database like Qdrant, what must you retain from the baseline?",
    options: [
      "Source document metadata for citations.",
      "Tenant metadata for authorization filters.",
      "The exact BM25 index.",
      "The ability to inspect retrieval behavior.",
    ],
    correct: [0, 1, 3],
    explanation:
      "A vector database should still preserve provenance (citations) and permissions (tenant metadata) in its payloads, ensuring behavior remains inspectable and secure.",
    source: {
      label: "Local Qdrant",
      url: "curriculum/intermediate/06-qdrant-local/README.md",
    },
  },
  {
    id: "a1-corrective",
    category: "11 - Corrective RAG",
    prompt: "What is a valid terminal state in a Corrective RAG loop?",
    options: [
      "Retrying infinitely until a document matches.",
      "Abstaining when the recovery routes fail to find evidence.",
      "Providing a grounded answer after successful query rewriting.",
      "Hallucinating an answer if the retry budget runs out.",
    ],
    correct: [1, 2],
    explanation:
      "Corrective loops must have bounds. It is perfectly valid (and safe) to abstain if rewriting or fallback retrieval fails to find solid evidence.",
    source: {
      label: "Corrective RAG",
      url: "curriculum/advanced/01-corrective-rag/README.md",
    },
  },
  {
    id: "a2-graphrag",
    category: "12 - GraphRAG",
    prompt: "When is GraphRAG especially useful?",
    options: [
      "Answering corpus-level aggregation questions.",
      "Traversing multi-hop relationships between entities.",
      "Answering every simple isolated definition.",
      "Overriding tenant boundaries during traversal.",
    ],
    correct: [0, 1],
    explanation:
      "GraphRAG excels at relationships, paths, and corpus-level summaries. Simple definitions are better served by standard retrieval, and traversal must never cross authorization boundaries.",
    source: {
      label: "GraphRAG",
      url: "curriculum/advanced/02-graphrag/README.md",
    },
  },
  {
    id: "a3-agentic",
    category: "13 - Agentic RAG",
    prompt: "Who is responsible for enforcing tool authorization in Agentic RAG?",
    options: [
      "The language model reasoning loop.",
      "The application boundary.",
      "The user prompt.",
      "The agent's system prompt.",
    ],
    correct: [1],
    explanation:
      "An agent is not authorized merely because a model selected a tool. The application boundary must enforce permissions, require approval for side effects, and validate arguments.",
    source: {
      label: "Agentic RAG",
      url: "curriculum/advanced/03-agentic-rag/README.md",
    },
  },
  {
    id: "a4-multimodal",
    category: "14 - Structured & Multimodal RAG",
    prompt: "Which tasks should usually use structured tools alongside or instead of text RAG?",
    options: [
      "Looking up a live account balance from an authorized database.",
      "Running an exact aggregate over business records.",
      "Explaining the meaning of a policy paragraph.",
      "Executing a transaction that changes external state.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Live structured facts, exact computation, and state-changing actions belong behind validated tools or database queries. Text similarity is poor for exact numeric aggregation.",
    source: {
      label: "Structured & Multimodal",
      url: "curriculum/advanced/04-structured-multimodal/README.md",
    },
  },
  {
    id: "a5-adaptive",
    category: "15 - Adaptive RAG",
    prompt: "Which decisions can a bounded Adaptive RAG controller make for an incoming query?",
    options: [
      "Whether retrieval is needed at all.",
      "Which source or retrieval method fits the information need.",
      "How much evidence to retrieve and whether it is sufficient.",
      "Whether to bypass authorization when a query is complex.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Adaptive RAG dynamically selects the retrieval/reasoning policy by query complexity. Authorization, however, is a non-negotiable boundary.",
    source: {
      label: "Adaptive RAG",
      url: "curriculum/advanced/05-adaptive-rag/README.md",
    },
  },
  {
    id: "a6-operations",
    category: "16 - Production Operations",
    prompt: "Which controls make a production RAG rollout safer?",
    options: [
      "Trace retrieval, generation, latency, and cost for each request.",
      "Use a small canary or shadow deployment before broad release.",
      "Disable regression evaluation once the system is in production.",
      "Define rollback and model/index versioning procedures.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Operational safety comes from end-to-end traces, gradual rollout, and reversible versioned changes. Production traffic is where regression checks matter most.",
    source: {
      label: "Production Operations",
      url: "curriculum/advanced/06-production-operations/README.md",
    },
  },
];
