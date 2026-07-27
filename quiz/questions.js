export const questions = [
  {
    id: "foundations-1",
    category: "Foundations",
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
      label: "What is RAG?",
      url: "docs/what-is-rag.md",
    },
  },
  {
    id: "foundations-2",
    category: "Foundations",
    prompt: "Which problems are especially well suited to RAG?",
    options: [
      "Answering from internal documentation with traceable citations.",
      "Changing a model's permanent writing style.",
      "Using information that changes more often than model training cycles.",
      "Answering questions over a specialized corpus too large for every prompt.",
    ],
    correct: [0, 2, 3],
    explanation:
      "RAG is a strong fit for private, current, specialized, and auditable knowledge. Fine-tuning is usually a better tool for persistent style or behavior changes.",
    source: {
      label: "RAG versus adjacent approaches",
      url: "docs/what-is-rag.md#rag-versus-adjacent-approaches",
    },
  },
  {
    id: "foundations-3",
    category: "Foundations",
    prompt: "Which two quality questions should a RAG team measure separately?",
    options: [
      "Did retrieval find the evidence needed to answer?",
      "Did the model answer faithfully from the supplied evidence?",
      "Did the model use the maximum available context window?",
      "Did every query return the same number of chunks?",
    ],
    correct: [0, 1],
    explanation:
      "Retrieval quality and generation quality are different failure surfaces. Separating them makes it possible to identify whether a bad answer came from missing evidence or unfaithful generation.",
    source: {
      label: "RAG explained",
      url: "README.md#rag-explained",
    },
  },
  {
    id: "ingestion-1",
    category: "Ingestion",
    prompt: "Which metadata should normally be retained with every indexed chunk?",
    options: [
      "A stable source identifier and document version.",
      "Page, section, or record location for citations.",
      "Permissions or tenant information used for access control.",
      "Only the embedding vector, to minimize storage.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Stable identifiers, versions, locations, and permissions make citations, freshness checks, and authorization possible. An embedding alone cannot provide provenance or enforce access boundaries.",
    source: {
      label: "RAG lifecycle: ingest",
      url: "docs/what-is-rag.md#the-lifecycle",
    },
  },
  {
    id: "ingestion-2",
    category: "Ingestion",
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
      label: "A practical RAG architecture",
      url: "README.md#a-practical-rag-architecture",
    },
  },
  {
    id: "ingestion-3",
    category: "Ingestion",
    prompt: "Which extraction failures can directly damage downstream RAG answers?",
    options: [
      "Losing table relationships during PDF conversion.",
      "Dropping headings that establish section context.",
      "Failing to preserve page locations needed for citations.",
      "Using both lexical and vector indexes.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Retrieval cannot recover structure or provenance that ingestion discarded. Hybrid indexing is a retrieval strategy, not an extraction failure.",
    source: {
      label: "Ingestion and document processing",
      url: "README.md#ingestion-and-document-processing",
    },
  },
  {
    id: "retrieval-1",
    category: "Retrieval",
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
      label: "Lexical retrieval",
      url: "docs/retrieval-patterns.md#lexical-retrieval",
    },
  },
  {
    id: "retrieval-2",
    category: "Retrieval",
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
      label: "Reranking",
      url: "docs/retrieval-patterns.md#reranking",
    },
  },
  {
    id: "retrieval-3",
    category: "Retrieval",
    prompt: "Which techniques can help a difficult multi-part or conversational query?",
    options: [
      "Rewrite a follow-up into a standalone search query.",
      "Decompose the question into focused subqueries.",
      "Generate multiple query formulations and merge the results.",
      "Always retrieve more chunks without changing the query.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Query rewriting, decomposition, and multi-query retrieval can improve recall when the original query is ambiguous or compound. Increasing top-k alone may add noise without fixing query intent.",
    source: {
      label: "Query rewriting and multi-query retrieval",
      url: "docs/retrieval-patterns.md#query-rewriting-and-multi-query-retrieval",
    },
  },
  {
    id: "generation-1",
    category: "Generation",
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
      label: "Security and production checklist",
      url: "README.md#security-and-production-checklist",
    },
  },
  {
    id: "generation-2",
    category: "Generation",
    prompt: "Why can supplying more retrieved context reduce answer quality?",
    options: [
      "Irrelevant passages can distract the model from the best evidence.",
      "Larger contexts can increase latency and cost.",
      "More context always prevents the model from producing citations.",
      "Conflicting or duplicated passages can make synthesis harder.",
    ],
    correct: [0, 1, 3],
    explanation:
      "A larger context is not automatically a better context. Noise, duplication, conflicts, cost, and latency all motivate retrieving a small, high-quality evidence set.",
    source: {
      label: "Common misconceptions",
      url: "docs/what-is-rag.md#more-context-is-always-better",
    },
  },
  {
    id: "generation-3",
    category: "Generation",
    prompt: "Which tasks should usually use structured tools alongside or instead of text RAG?",
    options: [
      "Looking up a live account balance from an authorized database.",
      "Running an exact aggregate over business records.",
      "Explaining the meaning of a policy paragraph.",
      "Executing a transaction that changes external state.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Live structured facts, exact computation, and state-changing actions belong behind validated tools or database queries. RAG remains useful for explanatory unstructured knowledge such as policy text.",
    source: {
      label: "RAG versus adjacent approaches",
      url: "docs/what-is-rag.md#rag-versus-adjacent-approaches",
    },
  },
  {
    id: "evaluation-1",
    category: "Evaluation",
    prompt: "Which items belong in a representative RAG evaluation set?",
    options: [
      "Expected answers or explicit answer criteria.",
      "Passages that should support the answer.",
      "Permission context and freshness constraints when relevant.",
      "Only successful production conversations.",
    ],
    correct: [0, 1, 2],
    explanation:
      "A useful test set records the expected evidence and conditions, and includes failures, adversarial cases, permission boundaries, and no-answer questions—not only successful examples.",
    source: {
      label: "Build a useful test set",
      url: "docs/evaluation.md#build-a-useful-test-set",
    },
  },
  {
    id: "evaluation-2",
    category: "Evaluation",
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
      label: "Measure retrieval separately",
      url: "docs/evaluation.md#measure-retrieval-separately",
    },
  },
  {
    id: "evaluation-3",
    category: "Evaluation",
    prompt: "Which practices make automated RAG evaluation more reliable?",
    options: [
      "Calibrate LLM-as-a-judge metrics against human review.",
      "Inspect changed failures as well as aggregate scores.",
      "Change several pipeline stages simultaneously to save time.",
      "Compare each focused change with a stable baseline.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Human calibration, failure inspection, and controlled comparisons reduce misleading conclusions. Changing many stages together makes it difficult to identify what caused an improvement or regression.",
    source: {
      label: "Evaluation iteration loop",
      url: "docs/evaluation.md#an-iteration-loop",
    },
  },
  {
    id: "security-1",
    category: "Security",
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
      label: "Metadata-filtered retrieval",
      url: "docs/retrieval-patterns.md#metadata-filtered-retrieval",
    },
  },
  {
    id: "security-2",
    category: "Security",
    prompt: "Why should retrieved documents be treated as untrusted input?",
    options: [
      "Documents may contain instructions intended to override the application.",
      "External content can include prompt-injection attacks.",
      "Retrieved text is automatically executable by the operating system.",
      "Agent tools can amplify the impact of malicious retrieved instructions.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Retrieved content can carry prompt injection. The risk grows when a model can call tools, so systems need separation of instructions and data, constrained tools, and validated parameters.",
    source: {
      label: "Security and production checklist",
      url: "README.md#security-and-production-checklist",
    },
  },
  {
    id: "security-3",
    category: "Security",
    prompt: "Which signals should a production RAG system monitor?",
    options: [
      "Indexing failures and corpus freshness.",
      "Empty retrieval and citation coverage.",
      "Latency and cost regressions.",
      "Only the model provider's uptime.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Production monitoring spans the full pipeline: ingestion, freshness, retrieval, citations, latency, cost, and answer quality. Provider uptime is only one dependency.",
    source: {
      label: "Security and production checklist",
      url: "README.md#security-and-production-checklist",
    },
  },
  {
    id: "operations-1",
    category: "Operations",
    prompt: "Which controls make a production RAG rollout safer?",
    options: [
      "Trace retrieval, generation, latency, and cost for each request.",
      "Use a small canary or shadow deployment before broad release.",
      "Disable regression evaluation once the system is in production.",
      "Define rollback and model/index versioning procedures.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Operational safety comes from end-to-end traces, gradual rollout, and reversible versioned changes. Production traffic is where regression checks matter most, not least.",
    source: {
      label: "Production operations guide",
      url: "curriculum/advanced/05-production-operations/README.md",
    },
  },
  {
    id: "operations-2",
    category: "Operations",
    prompt: "What should a RAG freshness policy specify?",
    options: [
      "How quickly changed source content must reach the index.",
      "What happens when ingestion fails or a source is stale.",
      "Only the embedding model's release date.",
      "Which owner is alerted when freshness SLOs are missed.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Freshness is a service-level property: define a target, failure behavior, and ownership. Embedding release dates do not describe whether source content is current.",
    source: {
      label: "Freshness and indexing checklist",
      url: "curriculum/advanced/05-production-operations/README.md",
    },
  },
  {
    id: "operations-3",
    category: "Operations",
    prompt: "Which signals help diagnose a sudden increase in RAG cost?",
    options: [
      "Token usage and retrieved context size by route.",
      "Cache hit rate and repeated-query volume.",
      "Only the number of Git commits in the repository.",
      "Model, retrieval, and tool latency broken down by request.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Cost investigations need request-level attribution: context and token volume, caching, and latency across model and retrieval steps. Repository activity is not a runtime cost signal.",
    source: {
      label: "Budgets and observability",
      url: "curriculum/advanced/05-production-operations/README.md",
    },
  },
];
