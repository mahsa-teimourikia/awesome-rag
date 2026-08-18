export const questions = [
  {
    id: "b1-q1",
    category: "01 - RAG Foundations",
    prompt: "What distinguishes Retrieval-Augmented Generation from relying only on a language model's parametric knowledge?",
    options: [
      "It retrieves external evidence at request time.",
      "It requires model retraining whenever a source document changes.",
      "It can use private or frequently updated information without encoding every fact into model weights.",
      "It guarantees that every generated claim is true.",
    ],
    correct: [0, 2],
    explanation:
      "RAG adds runtime retrieval of external evidence. The evidence corpus can change independently of the model weights, but retrieval and generation still need evaluation.",
    source: {
      label: "RAG Foundations",
      url: "curriculum/beginner/01-rag-foundations/README.md",
    },
  },
  {
    id: "b1-q2",
    category: "01 - RAG Foundations",
    prompt: "A RAG answer is unsupported. Which stages should be investigated before concluding that the language model itself is the problem?",
    options: [
      "Whether the required information exists in the corpus.",
      "Whether parsing, chunking, and retrieval preserved and found the evidence.",
      "Whether context construction retained the relevant evidence.",
      "Only the wording of the final generation prompt.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Unsupported answers can originate in corpus coverage, parsing, chunking, retrieval, ranking, context construction, or generation. Prompt wording is only one possible cause.",
    source: {
      label: "RAG Foundations",
      url: "curriculum/beginner/01-rag-foundations/README.md",
    },
  },
  {
    id: "b1-q3",
    category: "01 - RAG Foundations",
    prompt: "Which statement about embedding similarity is most accurate?",
    options: [
      "It is a model-dependent relevance signal, not a calibrated probability that the answer is correct.",
      "It directly measures factual truth.",
      "A similarity score of 0.9 always means 90% answer confidence.",
      "It makes lexical retrieval unnecessary.",
    ],
    correct: [0],
    explanation:
      "Embedding similarity helps rank candidates under a particular representation model. It is not calibrated answer confidence or factual truth.",
    source: {
      label: "RAG Foundations",
      url: "curriculum/beginner/01-rag-foundations/README.md",
    },
  },

  {
    id: "b2-q1",
    category: "02 - First Local RAG",
    prompt: "Why is an inspectable local RAG implementation a useful first engineering baseline?",
    options: [
      "It lets you inspect documents, metadata, retrieval results, context, and generation separately.",
      "It proves approximate nearest-neighbor search is unnecessary in production.",
      "It reduces the number of hidden variables while learning the retrieval loop.",
      "It removes the need for evaluation.",
    ],
    correct: [0, 2],
    explanation:
      "A small local pipeline makes intermediate artifacts visible and reduces infrastructure complexity. It does not replace production indexing or evaluation.",
    source: {
      label: "First Local RAG",
      url: "curriculum/beginner/02-first-local-rag/README.md",
    },
  },
  {
    id: "b2-q2",
    category: "02 - First Local RAG",
    prompt: "A query retrieves the wrong passage even though the correct passage exists in the corpus. What should you inspect before changing the generation prompt?",
    options: [
      "The chunk containing the expected evidence.",
      "The query and document representations used for retrieval.",
      "The rank and score of the expected passage.",
      "Only the final answer's writing style.",
    ],
    correct: [0, 1, 2],
    explanation:
      "If the expected evidence is present in the corpus but not retrieved correctly, inspect chunking, representations, and ranking before changing generation behavior.",
    source: {
      label: "First Local RAG",
      url: "curriculum/beginner/02-first-local-rag/README.md",
    },
  },
  {
    id: "b2-q3",
    category: "02 - First Local RAG",
    prompt: "Which distinction is important when moving from a tiny exact local search to a production vector index?",
    options: [
      "Approximate-nearest-neighbor recall is different from semantic relevance.",
      "ANN recall and answer correctness are the same metric.",
      "An ANN index can introduce approximation loss even when embeddings are unchanged.",
      "Exact local search automatically predicts production latency.",
    ],
    correct: [0, 2],
    explanation:
      "ANN search can fail to recover the same nearest vectors as exact search; that infrastructure issue is separate from whether those vectors are semantically relevant.",
    source: {
      label: "First Local RAG",
      url: "curriculum/beginner/02-first-local-rag/README.md",
    },
  },

  {
    id: "b3-q1",
    category: "03 - Chunking Lab",
    prompt: "Which principle best describes chunk-size selection?",
    options: [
      "Choose one universal token size and use it for every corpus.",
      "Balance retrieval specificity against evidence completeness and evaluate the trade-off.",
      "Always maximize chunk size to preserve context.",
      "Chunk size matters only to generation, not retrieval.",
    ],
    correct: [1],
    explanation:
      "Chunk size changes both retrieval specificity and how much evidence stays together. It should be chosen empirically for the corpus and query distribution.",
    source: {
      label: "Chunking Lab",
      url: "curriculum/beginner/03-chunking-lab/README.md",
    },
  },
  {
    id: "b3-q2",
    category: "03 - Chunking Lab",
    prompt: "What is a common cost of adding large chunk overlap?",
    options: [
      "More duplicate content can enter the index and top-k results.",
      "Index size and embedding cost can increase.",
      "Boundary context can sometimes be preserved better.",
      "It guarantees higher Recall@k.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Overlap can preserve boundary context, but also increases duplicate indexed text and cost. It does not guarantee higher retrieval recall.",
    source: {
      label: "Chunking Lab",
      url: "curriculum/beginner/03-chunking-lab/README.md",
    },
  },
  {
    id: "b3-q3",
    category: "03 - Chunking Lab",
    prompt: "Why can parent-child retrieval outperform using only one chunk size?",
    options: [
      "It can retrieve a small child unit precisely and return a larger parent for context.",
      "It removes the need for document metadata.",
      "It separates the unit optimized for retrieval from the unit supplied for generation.",
      "It guarantees semantic chunk boundaries.",
    ],
    correct: [0, 2],
    explanation:
      "Parent-child retrieval can use small evidence units for matching while returning a richer parent section for generation; it does not eliminate provenance or guarantee semantic boundaries.",
    source: {
      label: "Chunking Lab",
      url: "curriculum/beginner/03-chunking-lab/README.md",
    },
  },

  {
    id: "b4-q1",
    category: "04 - Citations & Abstention",
    prompt: "Which properties are required for a robust citation system?",
    options: [
      "The cited evidence ID actually existed in the evidence available to the response.",
      "The cited evidence supports the associated claim.",
      "Material claims have appropriate evidence coverage.",
      "The model prints any plausible-looking source filename.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Citation validity, claim support, and completeness are separate requirements. A plausible source label generated by the model is not sufficient.",
    source: {
      label: "Citations & Abstention",
      url: "curriculum/beginner/04-citations-abstention/README.md",
    },
  },
  {
    id: "b4-q2",
    category: "04 - Citations & Abstention",
    prompt: "A model gives a factually correct answer using memorized knowledge, but the required fact was absent from the supplied evidence. Under a strict grounded-RAG contract, how should this be treated?",
    options: [
      "As fully successful because the fact is true.",
      "As an evidence-grounding failure.",
      "As proof that retrieval can be removed.",
      "As equivalent to a valid cited answer.",
    ],
    correct: [1],
    explanation:
      "A strict evidence contract requires material claims to be supported by the evidence supplied to the request, even when model memory happens to produce a true fact.",
    source: {
      label: "Citations & Abstention",
      url: "curriculum/beginner/04-citations-abstention/README.md",
    },
  },
  {
    id: "b4-q3",
    category: "04 - Citations & Abstention",
    prompt: "Which signals can contribute to an abstention decision?",
    options: [
      "Required evidence coverage.",
      "Source authority and conflict status.",
      "Retrieval or reranking signals calibrated for the task.",
      "The model's self-reported confidence alone.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Answerability can combine evidence coverage, authority, conflicts, and calibrated retrieval signals. Model self-confidence alone is not a reliable answerability policy.",
    source: {
      label: "Citations & Abstention",
      url: "curriculum/beginner/04-citations-abstention/README.md",
    },
  },

  {
    id: "i1-q1",
    category: "05 - Retrieval Strategies",
    prompt: "Which query types often benefit from lexical or sparse retrieval signals?",
    options: [
      "Exact product identifiers and error codes.",
      "Rare names and policy numbers.",
      "Strong paraphrases with little lexical overlap.",
      "Version strings and acronyms.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Lexical/sparse retrieval is particularly useful when exact tokens matter. Dense retrieval often helps more with semantic paraphrases.",
    source: {
      label: "Retrieval Strategies",
      url: "curriculum/intermediate/01-retrieval-strategies/README.md",
    },
  },
  {
    id: "i1-q2",
    category: "05 - Retrieval Strategies",
    prompt: "Why is Reciprocal Rank Fusion useful in hybrid retrieval?",
    options: [
      "It combines ranked lists without requiring raw BM25 and dense scores to share the same scale.",
      "It guarantees the fused ranking is optimal.",
      "It can reward documents that rank highly in multiple candidate lists.",
      "It turns every retriever score into a calibrated probability.",
    ],
    correct: [0, 2],
    explanation:
      "RRF uses rank positions rather than directly adding incomparable raw score scales. It is robust, but not guaranteed optimal or probabilistically calibrated.",
    source: {
      label: "Retrieval Strategies",
      url: "curriculum/intermediate/01-retrieval-strategies/README.md",
    },
  },
  {
    id: "i1-q3",
    category: "05 - Retrieval Strategies",
    prompt: "When is late-interaction retrieval or reranking most justified?",
    options: [
      "When single-vector representations lose useful fine-grained query-document interactions.",
      "Whenever a vector database is used.",
      "When measured relevance gains justify higher storage and compute.",
      "To replace authorization filters.",
    ],
    correct: [0, 2],
    explanation:
      "Late interaction preserves fine-grained token-level matching and can improve relevance, but its added storage/compute should be justified by evaluation.",
    source: {
      label: "Retrieval Strategies",
      url: "curriculum/intermediate/01-retrieval-strategies/README.md",
    },
  },

  {
    id: "i2-q1",
    category: "06 - Metadata & Permissions",
    prompt: "What is the safest order for authorization-aware retrieval?",
    options: [
      "Authenticate the caller, derive authorized scope, then retrieve and rank eligible evidence.",
      "Retrieve everything, send it to the model, then ask the model to hide restricted passages.",
      "Let the model choose the caller's tenant from the prompt.",
      "Rank globally first and treat post-filtering as the primary security boundary.",
    ],
    correct: [0],
    explanation:
      "Authorization should constrain the candidate space before unauthorized content can reach ranking, model context, caches, or traces.",
    source: {
      label: "Metadata & Permissions",
      url: "curriculum/intermediate/02-metadata-permissions/README.md",
    },
  },
  {
    id: "i2-q2",
    category: "06 - Metadata & Permissions",
    prompt: "Which metadata is commonly security- or lifecycle-critical in enterprise RAG?",
    options: [
      "Tenant and classification.",
      "Effective dates and source version.",
      "Document type and language can also be relevant filters.",
      "A model-generated guess of the user's role.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Tenant/classification and temporal/version metadata can determine eligibility; document type/language can narrow scope. User roles must come from trusted identity/policy systems.",
    source: {
      label: "Metadata & Permissions",
      url: "curriculum/intermediate/02-metadata-permissions/README.md",
    },
  },
  {
    id: "i2-q3",
    category: "06 - Metadata & Permissions",
    prompt: "Why must retrieval caches be authorization-aware?",
    options: [
      "The same natural-language query can have different authorized evidence for different callers.",
      "A cache keyed only by query text can leak another tenant's result.",
      "Policy and index versions can affect a valid cache entry.",
      "Caching makes authorization unnecessary.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Cache identity must reflect authorization-relevant state and content/index versions; otherwise correct retrieval can still be undermined by stale or cross-tenant cached evidence.",
    source: {
      label: "Metadata & Permissions",
      url: "curriculum/intermediate/02-metadata-permissions/README.md",
    },
  },

  {
    id: "i3-q1",
    category: "07 - Query Planning & Reranking",
    prompt: "What can a reranker do if the relevant document is not present in the first-stage candidate set?",
    options: [
      "Recover it from the full corpus automatically.",
      "Improve its rank anyway.",
      "Nothing; candidate recall must be fixed upstream.",
      "Generate a substitute passage and treat it as evidence.",
    ],
    correct: [2],
    explanation:
      "Rerankers only score the candidates they receive. Missing evidence requires improving first-stage retrieval, query formulation, or candidate breadth.",
    source: {
      label: "Query Planning & Reranking",
      url: "curriculum/intermediate/03-query-reranking/README.md",
    },
  },
  {
    id: "i3-q2",
    category: "07 - Query Planning & Reranking",
    prompt: "Which statement correctly distinguishes bi-encoder retrieval from cross-encoder reranking?",
    options: [
      "Bi-encoders independently encode queries and documents for efficient search.",
      "Cross-encoders jointly score query-document pairs and are typically more expensive.",
      "Cross-encoders are normally run over every document in a large corpus.",
      "The architecture naturally supports retrieve-then-rerank.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Bi-encoders enable efficient candidate search, while cross-encoders provide stronger pairwise relevance on a bounded candidate set.",
    source: {
      label: "Query Planning & Reranking",
      url: "curriculum/intermediate/03-query-reranking/README.md",
    },
  },
  {
    id: "i3-q3",
    category: "07 - Query Planning & Reranking",
    prompt: "What is a key safety rule for HyDE or other generated retrieval representations?",
    options: [
      "Treat generated hypothetical text as a search probe, not evidence.",
      "Cite the hypothetical document in the final answer.",
      "Assume its factual claims are correct because an LLM generated them.",
      "Preserve the original user query so retrieval drift can be evaluated.",
    ],
    correct: [0, 3],
    explanation:
      "Generated hypothetical content can improve search, but it is not corpus evidence. The original user query should remain available for control and evaluation.",
    source: {
      label: "Query Planning & Reranking",
      url: "curriculum/intermediate/03-query-reranking/README.md",
    },
  },

  {
    id: "i4-q1",
    category: "08 - RAG Evaluation",
    prompt: "Which metrics primarily evaluate retrieval ranking when relevance labels are available?",
    options: [
      "Recall@k.",
      "MRR.",
      "nDCG.",
      "Writing style preference.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Recall@k, MRR, and nDCG evaluate retrieval coverage and ranking. Writing style is a generation preference.",
    source: {
      label: "RAG Evaluation",
      url: "curriculum/intermediate/04-evaluation/README.md",
    },
  },
  {
    id: "i4-q2",
    category: "08 - RAG Evaluation",
    prompt: "Why should an evaluation set contain unanswerable questions?",
    options: [
      "To measure false-answer behavior.",
      "To measure false abstention on answerable questions alongside abstention behavior.",
      "Because a benchmark containing only answerable questions can reward answering everything.",
      "To eliminate the need for citation evaluation.",
    ],
    correct: [0, 1, 2],
    explanation:
      "A trustworthy evaluation must cover both answerable and unanswerable cases so answerability and abstention behavior can be measured.",
    source: {
      label: "RAG Evaluation",
      url: "curriculum/intermediate/04-evaluation/README.md",
    },
  },
  {
    id: "i4-q3",
    category: "08 - RAG Evaluation",
    prompt: "How should LLM-as-a-judge evaluations be used?",
    options: [
      "With explicit rubrics and versioned judge configurations.",
      "Calibrated against human-labelled cases for important criteria.",
      "As unquestionable ground truth because the judge is another LLM.",
      "With slice analysis to inspect where agreement breaks down.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Model judges are useful measurement instruments but can be biased and variable. They should be calibrated and analyzed rather than treated as ground truth.",
    source: {
      label: "RAG Evaluation",
      url: "curriculum/intermediate/04-evaluation/README.md",
    },
  },

  {
    id: "i5-q1",
    category: "09 - Research Synthesis",
    prompt: "Why can ten citations still represent weak source diversity?",
    options: [
      "Several sources may repeat or syndicate the same original evidence.",
      "Citation count alone does not establish independence or authority.",
      "More citations always mean stronger evidence.",
      "Correlated sources can create false confidence.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Many cited pages can trace back to one underlying source. Good synthesis tracks provenance, authority, and independence rather than citation count alone.",
    source: {
      label: "Research Synthesis",
      url: "curriculum/intermediate/05-research-synthesis/README.md",
    },
  },
  {
    id: "i5-q2",
    category: "09 - Research Synthesis",
    prompt: "Two credible sources report materially different values. What should a synthesis pipeline do?",
    options: [
      "Represent the conflict explicitly.",
      "Compare source date, scope, definitions, and authority.",
      "Silently average the values.",
      "Preserve uncertainty when the conflict cannot be resolved.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Conflicting evidence should be analyzed and represented, not averaged or hidden. Unresolved disagreement should remain visible.",
    source: {
      label: "Research Synthesis",
      url: "curriculum/intermediate/05-research-synthesis/README.md",
    },
  },
  {
    id: "i5-q3",
    category: "09 - Research Synthesis",
    prompt: "What is the purpose of a claim-to-evidence map before final synthesis?",
    options: [
      "To ensure each material claim has traceable supporting evidence.",
      "To make it easier to detect unsupported connective reasoning.",
      "To replace source provenance with model-generated citations.",
      "To expose evidence gaps before polished prose is generated.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Mapping intended claims to evidence makes coverage and gaps explicit and reduces the risk of adding unsupported claims during fluent synthesis.",
    source: {
      label: "Research Synthesis",
      url: "curriculum/intermediate/05-research-synthesis/README.md",
    },
  },

  {
    id: "i6-q1",
    category: "10 - Qdrant Search Engineering",
    prompt: "Which distinction helps diagnose vector-search failures in a production ANN index?",
    options: [
      "ANN recall asks whether approximate search recovers the vectors exact search would return.",
      "Semantic relevance asks whether retrieved vectors correspond to useful evidence.",
      "ANN recall and semantic relevance are the same measurement.",
      "Measuring both can separate infrastructure approximation from representation/relevance problems.",
    ],
    correct: [0, 1, 3],
    explanation:
      "ANN recall isolates approximate-index behavior; semantic relevance evaluates whether the retrieved items actually answer the information need.",
    source: {
      label: "Qdrant Local",
      url: "curriculum/intermediate/06-qdrant-local/README.md",
    },
  },
  {
    id: "i6-q2",
    category: "10 - Qdrant Search Engineering",
    prompt: "What can named vectors or multiple document representations support?",
    options: [
      "Separate title, body, or summary representations for the same item.",
      "Searching different representations and fusing the results.",
      "Eliminating the need for metadata or provenance.",
      "Avoiding the loss that can occur when every signal is compressed into one embedding.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Multiple representations let search preserve distinct discovery signals. They complement rather than replace metadata and provenance.",
    source: {
      label: "Qdrant Local",
      url: "curriculum/intermediate/06-qdrant-local/README.md",
    },
  },
  {
    id: "i6-q3",
    category: "10 - Qdrant Search Engineering",
    prompt: "What is a typical use of Qdrant-style multi-stage prefetch?",
    options: [
      "Use a cheaper retriever to build a candidate set, then apply a more expensive representation or reranker.",
      "Run the most expensive model over the entire collection first.",
      "Combine dense and sparse candidate generation before a later precision stage.",
      "Guarantee that no evaluation is required.",
    ],
    correct: [0, 2],
    explanation:
      "Multi-stage retrieval supports coarse-to-fine search: inexpensive candidate generation followed by a more precise bounded stage.",
    source: {
      label: "Qdrant Local",
      url: "curriculum/intermediate/06-qdrant-local/README.md",
    },
  },

  {
    id: "a1-q1",
    category: "11 - Corrective RAG",
    prompt: "Which behavior makes a Corrective RAG controller bounded?",
    options: [
      "Explicit allowed recovery routes.",
      "Maximum attempts, time, or cost.",
      "Safe terminal states such as abstention or escalation.",
      "Retrying until any passage seems relevant.",
    ],
    correct: [0, 1, 2],
    explanation:
      "A corrective controller needs finite policies and terminal states. Unbounded retries increase cost and can amplify bad evidence.",
    source: {
      label: "Corrective RAG",
      url: "curriculum/advanced/01-corrective-rag/README.md",
    },
  },
  {
    id: "a1-q2",
    category: "11 - Corrective RAG",
    prompt: "An internal retrieval attempt returns weak evidence. Which recovery choices may be appropriate depending on policy?",
    options: [
      "Rewrite the query.",
      "Try an approved alternate retriever.",
      "Ask for clarification.",
      "Automatically search the public web even when external egress is forbidden.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Recovery should select only policy-approved actions. External retrieval changes trust and egress boundaries and is not a universal fallback.",
    source: {
      label: "Corrective RAG",
      url: "curriculum/advanced/01-corrective-rag/README.md",
    },
  },
  {
    id: "a1-q3",
    category: "11 - Corrective RAG",
    prompt: "How does Corrective RAG differ from Adaptive RAG?",
    options: [
      "Corrective RAG evaluates or recovers after retrieval evidence is produced.",
      "Adaptive RAG chooses a retrieval strategy before or around retrieval.",
      "They are identical names for the same control point.",
      "They can be composed as route → retrieve → grade → recover or answer.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Adaptive routing selects a strategy; corrective control evaluates whether the resulting evidence is sufficient and recovers if needed.",
    source: {
      label: "Corrective RAG",
      url: "curriculum/advanced/01-corrective-rag/README.md",
    },
  },

  {
    id: "a2-q1",
    category: "12 - GraphRAG",
    prompt: "When is graph-based retrieval especially valuable?",
    options: [
      "When the information need depends on explicit relationships across entities.",
      "When a bounded multi-hop path is itself part of the evidence.",
      "For every simple definition lookup regardless of corpus structure.",
      "When source-backed relationship provenance is available.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Graph retrieval is most useful for relationship and multi-hop questions. Simple lookup questions often remain better served by ordinary retrieval.",
    source: {
      label: "GraphRAG",
      url: "curriculum/advanced/02-graphrag/README.md",
    },
  },
  {
    id: "a2-q2",
    category: "12 - GraphRAG",
    prompt: "Why can converting a directed knowledge graph to an undirected graph be unsafe?",
    options: [
      "Directional relations such as DEPENDS_ON or OWNS can lose their semantics.",
      "Connected nodes can become traversable in directions the relation does not support.",
      "It always improves factual correctness.",
      "Path validity depends on relation semantics, not connectivity alone.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Direction can be semantically meaningful. Undirected traversal may create connected paths that are not valid relationship explanations.",
    source: {
      label: "GraphRAG",
      url: "curriculum/advanced/02-graphrag/README.md",
    },
  },
  {
    id: "a2-q3",
    category: "12 - GraphRAG",
    prompt: "What should a trustworthy graph edge preserve?",
    options: [
      "Subject, relation, and object.",
      "Source or provenance identifying where the relationship came from.",
      "Relevant version or validity metadata when the relation can change.",
      "Only a human-readable node label.",
    ],
    correct: [0, 1, 2],
    explanation:
      "A graph edge used as evidence should preserve both its relation semantics and enough provenance/version information to verify it.",
    source: {
      label: "GraphRAG",
      url: "curriculum/advanced/02-graphrag/README.md",
    },
  },

  {
    id: "a3-q1",
    category: "13 - Agentic RAG",
    prompt: "When is a deterministic workflow usually preferable to an agent?",
    options: [
      "When the evidence/action sequence is already known.",
      "When predictable behavior and easier testing are valuable.",
      "Whenever the next useful action genuinely depends on previous observations.",
      "When additional autonomy would add variance without measurable task benefit.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Known sequences are usually better expressed as deterministic workflows. Agents are justified when runtime findings genuinely determine the next useful action.",
    source: {
      label: "Agentic RAG",
      url: "curriculum/advanced/03-agentic-rag/README.md",
    },
  },
  {
    id: "a3-q2",
    category: "13 - Agentic RAG",
    prompt: "Which controls should remain outside an agent model's discretion?",
    options: [
      "Tool authorization.",
      "Human approval for material side effects.",
      "Turn, tool-call, cost, and time budgets.",
      "Whether the model feels confident enough to bypass policy.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Model tool selection is not authorization. Application policy and explicit budgets bound what the agent may do.",
    source: {
      label: "Agentic RAG",
      url: "curriculum/advanced/03-agentic-rag/README.md",
    },
  },
  {
    id: "a3-q3",
    category: "13 - Agentic RAG",
    prompt: "What should an agent trace record for auditability?",
    options: [
      "Tool selected and validated arguments.",
      "Evidence/result IDs and policy decisions.",
      "Latency, cost, and terminal reason.",
      "The model's hidden chain-of-thought.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Audit observable decisions, inputs, outputs, policy results, and resource use. Hidden chain-of-thought should not be required or stored.",
    source: {
      label: "Agentic RAG",
      url: "curriculum/advanced/03-agentic-rag/README.md",
    },
  },

  {
    id: "a4-q1",
    category: "14 - Structured & Multimodal RAG",
    prompt: "Which tasks should normally use deterministic structured computation rather than free-form LLM arithmetic?",
    options: [
      "Summing authorized business records.",
      "Calculating an exact account total.",
      "Interpreting a policy paragraph's meaning.",
      "Applying a validated unit conversion to structured values.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Exact calculations over structured data should normally be performed by deterministic code, SQL, or typed tools, while the LLM can explain the result.",
    source: {
      label: "Structured & Multimodal RAG",
      url: "curriculum/advanced/04-structured-multimodal/README.md",
    },
  },
  {
    id: "a4-q2",
    category: "14 - Structured & Multimodal RAG",
    prompt: "Why is arbitrary generated Python execution not the default safe architecture for dataframe questions?",
    options: [
      "Generated code can perform unintended filesystem, network, or process operations if the environment permits them.",
      "A code agent still requires sandboxing and least privilege.",
      "Typed aggregations or constrained query interfaces can provide narrower execution contracts.",
      "Because Python cannot perform exact arithmetic.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Arbitrary code execution greatly expands the attack surface. Constrained data/query operations are easier to validate and govern.",
    source: {
      label: "Structured & Multimodal RAG",
      url: "curriculum/advanced/04-structured-multimodal/README.md",
    },
  },
  {
    id: "a4-q3",
    category: "14 - Structured & Multimodal RAG",
    prompt: "How should OCR-derived evidence be represented for verification?",
    options: [
      "Preserve the asset or document ID.",
      "Preserve page/frame and bounding-box or region information.",
      "Preserve OCR confidence and engine/version where relevant.",
      "Store only the extracted number and discard its location.",
    ],
    correct: [0, 1, 2],
    explanation:
      "OCR evidence should remain traceable to a source region, and confidence/extraction metadata helps distinguish observation quality from later inference.",
    source: {
      label: "Structured & Multimodal RAG",
      url: "curriculum/advanced/04-structured-multimodal/README.md",
    },
  },

  {
    id: "a5-q1",
    category: "15 - Adaptive RAG",
    prompt: "Which components can implement an Adaptive RAG router?",
    options: [
      "Deterministic rules.",
      "A classifier.",
      "A structured LLM decision.",
      "Only a large language model; rules and classifiers are not adaptive.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Adaptive routing is a system behavior, not a specific model implementation. Rules, classifiers, and structured LLM decisions can all implement routing.",
    source: {
      label: "Adaptive RAG",
      url: "curriculum/advanced/05-adaptive-rag/README.md",
    },
  },
  {
    id: "a5-q2",
    category: "15 - Adaptive RAG",
    prompt: "Which signals can be useful for route selection?",
    options: [
      "Whether the question requires private/internal evidence.",
      "Whether the answer requires fresh external information.",
      "Whether the task is an exact structured calculation or relationship query.",
      "Only the number of words in the user's question.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Information need, freshness, data modality, and source requirements are stronger routing signals than superficial query length alone.",
    source: {
      label: "Adaptive RAG",
      url: "curriculum/advanced/05-adaptive-rag/README.md",
    },
  },
  {
    id: "a5-q3",
    category: "15 - Adaptive RAG",
    prompt: "How should an adaptive router be evaluated?",
    options: [
      "Route accuracy on labelled cases.",
      "High-risk misroute rate.",
      "Downstream quality, latency, cost, and route distribution.",
      "Only whether the router produces syntactically valid JSON.",
    ],
    correct: [0, 1, 2],
    explanation:
      "Router quality is about choosing safe, effective paths and improving downstream outcomes, not only producing valid output.",
    source: {
      label: "Adaptive RAG",
      url: "curriculum/advanced/05-adaptive-rag/README.md",
    },
  },

  {
    id: "a6-q1",
    category: "16 - Production Operations",
    prompt: "Why are stage-level traces more useful than only end-to-end latency?",
    options: [
      "They can distinguish authorization, retrieval, reranking, generation, and verification delays.",
      "They help localize regressions to specific dependencies.",
      "End-to-end latency alone always identifies the slow component.",
      "They can carry version and policy attributes for incident reconstruction.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Stage-level spans localize performance and policy failures and make versioned incident reconstruction possible.",
    source: {
      label: "Production Operations",
      url: "curriculum/advanced/06-production-operations/README.md",
    },
  },
  {
    id: "a6-q2",
    category: "16 - Production Operations",
    prompt: "Which items should be versioned together as part of a RAG release bundle?",
    options: [
      "Prompt and generation model.",
      "Chunking, embedding, retrieval, and reranking configuration.",
      "Corpus/index and policy versions.",
      "Only the UI release version.",
    ],
    correct: [0, 1, 2],
    explanation:
      "RAG behavior depends on multiple coupled artifacts. Versioning them together supports reproducibility, canary analysis, rollback, and incident investigation.",
    source: {
      label: "Production Operations",
      url: "curriculum/advanced/06-production-operations/README.md",
    },
  },
  {
    id: "a6-q3",
    category: "16 - Production Operations",
    prompt: "What is a safe degradation principle for production RAG?",
    options: [
      "Reduce optional capability while preserving authorization and evidence controls.",
      "Disable optional reranking if necessary while keeping required safety checks.",
      "Skip authorization to preserve availability during an outage.",
      "Abstain when required verification or evidence cannot be established.",
    ],
    correct: [0, 1, 3],
    explanation:
      "Safe degradation can reduce quality or optional features but must not weaken core authorization or evidence-verification invariants.",
    source: {
      label: "Production Operations",
      url: "curriculum/advanced/06-production-operations/README.md",
    },
  },
];