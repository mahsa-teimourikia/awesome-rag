# RAG Curriculum

A practical, architecture-first curriculum for learning Retrieval-Augmented Generation from first principles through production systems.

The curriculum is organized by **engineering capability**, not by vendor or framework:

```text
BEGINNER
Evidence foundations
     ↓
INTERMEDIATE
Retrieval engineering
     ↓
ADVANCED
Adaptive, agentic & production RAG
```

The goal is not to collect RAG patterns. It is to learn how to decide **which architecture is justified, how to measure it, and how to operate it safely**.

---

## Learning philosophy

Every course follows the same progression:

```text
Concept
  ↓
Why it exists
  ↓
Architecture
  ↓
Implementation
  ↓
Failure modes
  ↓
Evaluation
  ↓
Enterprise trade-offs
```

The **README is the technical training chapter**. The notebook is its practical companion.

This distinction is intentional: learners should understand the architecture and trade-offs before relying on a framework abstraction.

A recurring principle throughout the curriculum is:

> **Add complexity only when evaluation demonstrates the failure mode that complexity is intended to solve.**

---

# Curriculum map

## Beginner — Build the evidence loop

Start with [`beginner/README.md`](beginner/README.md).

The Beginner track develops the mental model and evidence discipline required for everything that follows.

| Course | Main question | Core capability |
|---|---|---|
| [01 — RAG Foundations](beginner/01-rag-foundations/README.md) | What actually happens inside a RAG system? | Understand ingestion, retrieval, context, generation, provenance, and failure decomposition |
| [02 — First Local RAG](beginner/02-first-local-rag/README.md) | Can I build and inspect the complete loop? | Build a transparent local RAG baseline and inspect intermediate artifacts |
| [03 — Chunking Lab](beginner/03-chunking-lab/README.md) | How should documents become retrievable evidence? | Compare chunking and document-representation strategies experimentally |
| [04 — Citations & Abstention](beginner/04-citations-abstention/README.md) | When is an answer actually supported? | Preserve provenance, validate citations, and abstain when evidence is insufficient |

### Beginner progression

```text
RAG system model
      ↓
inspectable implementation
      ↓
document representation
      ↓
evidence + citation discipline
```

**Exit capability:** build a small RAG system whose answers can be traced back through retrieved evidence and whose failures can be classified rather than simply called “hallucinations.”

---

# Intermediate — Engineer retrieval quality

Continue with [`intermediate/README.md`](intermediate/README.md).

Intermediate RAG turns the transparent beginner baseline into a measurable retrieval subsystem.

| Course | Main question | Core capability |
|---|---|---|
| [01 — Retrieval Strategies](intermediate/01-retrieval-strategies/README.md) | How do we improve candidate recall? | Lexical, dense, sparse, hybrid, fusion, multi-representation, late interaction |
| [02 — Metadata & Permissions](intermediate/02-metadata-permissions/README.md) | Which evidence is eligible for this request? | Filtering, tenant isolation, RBAC/ABAC concepts, temporal validity, authorization-aware retrieval |
| [03 — Query Planning & Reranking](intermediate/03-query-reranking/README.md) | How do we improve complex retrieval and ordering? | Decomposition, rewriting, retrieval cascades, cross-encoders, late interaction, reranking |
| [04 — RAG Evaluation](intermediate/04-evaluation/README.md) | How do we know a change actually helped? | Retrieval metrics, groundedness, citations, abstention, judges, regression gates |
| [05 — Research Synthesis](intermediate/05-research-synthesis/README.md) | How do we combine evidence across sources? | Evidence tables, authority, contradiction handling, source diversity, citation-preserving synthesis |
| [06 — Qdrant Local](intermediate/06-qdrant-local/README.md) | How does retrieval architecture map to real infrastructure? | Dense/sparse search, filters, HNSW, hybrid queries, multivectors, multi-stage retrieval |

### Intermediate progression

```text
candidate generation
       ↓
authorized candidate space
       ↓
planning + reranking
       ↓
evaluation
       ↓
multi-source synthesis
       ↓
real retrieval infrastructure
```

**Exit capability:** design and evaluate a permission-aware retrieval pipeline and explain which retrieval stage improved quality, what it cost, and which failure remains.

---

# Advanced — Design bounded dynamic RAG systems

Finish with [`advanced/README.md`](advanced/README.md).

Advanced RAG introduces dynamic control only where the simpler retrieval architecture has a measured limitation.

| Course | Main question | Core capability |
|---|---|---|
| [01 — Corrective RAG](advanced/01-corrective-rag/README.md) | What happens when retrieved evidence is insufficient? | Evidence grading, bounded recovery, rewrite/fallback/abstention policies |
| [02 — GraphRAG](advanced/02-graphrag/README.md) | What if the answer depends on relationships? | Entity/relation modeling, graph traversal, communities, graph + text provenance |
| [03 — Agentic RAG](advanced/03-agentic-rag/README.md) | When should a model choose the next evidence action? | Tool selection, bounded agent loops, authorization, approvals, trajectory evaluation |
| [04 — Structured & Multimodal RAG](advanced/04-structured-multimodal/README.md) | What if evidence is tabular, numeric, visual, or OCR-derived? | Modality-specific retrieval, deterministic computation, multimodal evidence contracts |
| [05 — Adaptive RAG](advanced/05-adaptive-rag/README.md) | Which retrieval strategy should run for this request? | Routing, cascades, route evaluation, Adaptive + Corrective architectures |
| [06 — Production Operations](advanced/06-production-operations/README.md) | How do we safely operate the complete system? | Tracing, quality monitoring, versioning, release gates, canaries, rollback, safe degradation |

### Advanced progression

```text
detect retrieval failure
        ↓
recover safely
        ↓
retrieve relationships
        ↓
bounded tool autonomy
        ↓
multiple evidence modalities
        ↓
adaptive routing
        ↓
production operations
```

**Exit capability:** decide which advanced RAG pattern should—or should not—be deployed, justify it against a simpler baseline, define its control boundary, and operate it with measurable quality and recoverability.

---

# The architecture evolves across the curriculum

## Stage 1 — Basic evidence loop

```text
query
  ↓
retrieve
  ↓
context
  ↓
generate
```

## Stage 2 — Evidence-aware RAG

```text
query
  ↓
authorized retrieval
  ↓
evidence + provenance
  ↓
generation
  ↓
citation validation
  ↓
answer / abstain
```

## Stage 3 — Retrieval engineering

```text
query
  ↓
authorization
  ↓
dense + lexical/sparse retrieval
  ↓
fusion
  ↓
reranking
  ↓
evidence selection
  ↓
generation + verification
```

## Stage 4 — Dynamic enterprise RAG

```text
request
   ↓
identity + authorization
   ↓
adaptive route
   ├─ vector / lexical
   ├─ graph
   ├─ structured data
   ├─ multimodal
   └─ approved external retrieval
            ↓
      evidence grading
            ↓
   corrective recovery
            ↓
 optional bounded agent
            ↓
      evidence ledger
            ↓
 generation / synthesis
            ↓
 claim + citation verification
            ↓
answer / clarify / abstain / escalate
            ↓
 trace + evaluation + operations
```

Not every application needs the final architecture.

A major objective of the curriculum is learning **when to stop adding boxes**.

---

# How to use each course

A recommended workflow is:

1. **Read the README first.** Understand the theory, architecture, alternatives, failure modes, and production considerations.
2. **Study the diagrams.** Use them to understand information flow and control boundaries.
3. **Run the notebook.** Inspect intermediate evidence rather than looking only at the final answer.
4. **Change one variable.** Modify retrieval, chunking, ranking, routing, or another controlled parameter.
5. **Measure the effect.** Compare quality, latency, cost, and failure behavior.
6. **Complete the design questions.** Explain when the technique should and should not be used.
7. **Return to the README.** Revisit the architecture after observing the implementation.

The notebooks are intentionally not treated as the complete course.

---

# Evaluation is a continuous thread

Evaluation begins in the first course and becomes progressively more formal.

```text
Beginner
  inspect evidence and expected retrieval
        ↓
Intermediate
  labelled datasets + IR metrics + groundedness
        ↓
Advanced
  route + trajectory + recovery + operational evaluation
```

Useful evaluation layers include:

| Layer | Examples |
|---|---|
| Corpus / ingestion | coverage, parsing failures, freshness |
| Retrieval | Recall@k, Precision@k, MRR, nDCG |
| Evidence | sufficiency, authority, provenance |
| Generation | correctness, claim support, completeness |
| Citations | correctness, completeness, identity |
| Routing | route accuracy, unnecessary expensive routes |
| Agent trajectory | tool correctness, repeated actions, policy violations |
| Operations | latency, cost, failure rate, drift, rollback readiness |

Avoid reducing the whole system to one opaque “RAG score.”

---

# Enterprise principles used throughout

## Evidence before fluency

A fluent answer is not a successful answer if the required evidence is missing.

## Authorization before relevance

The retriever should rank evidence **inside the authorized candidate space**.

## Provenance from ingestion onward

Source identity should survive chunking, retrieval, reranking, synthesis, and citation.

## Deterministic controls around probabilistic components

Use application policy, schemas, authorization, budgets, validation, and terminal states to bound model behavior.

## Evaluate components separately

Retrieval, ranking, routing, generation, citations, and operations fail differently.

## Complexity must earn its place

GraphRAG, corrective loops, agents, query planners, multimodal models, and adaptive routing should solve measured problems—not decorate the architecture.

---

# Practical learning model

The repository uses notebooks and small scenarios to expose system behavior.

A useful experiment pattern is:

```text
baseline
   ↓
identify failure
   ↓
change one architectural variable
   ↓
run fixed evaluation set
   ↓
compare quality + latency + cost + risk
   ↓
keep or reject
```

This is closer to real RAG engineering than simply assembling framework components until the demo looks convincing.

---

# Reference documentation

The material under [`docs/`](../docs/) provides cross-cutting references rather than a parallel curriculum.

Useful references include:

| Reference | Use it when |
|---|---|
| [What is RAG?](../docs/what-is-rag.md) | Establishing the foundational system model |
| [Technology decisions](../docs/technology-decisions.md) | Comparing implementation approaches |
| [Retrieval patterns](../docs/retrieval-patterns.md) | Designing candidate generation and ranking |
| [Evaluation guide](../docs/evaluation.md) | Building evaluation datasets and release criteria |
| [Adaptive RAG guide](../docs/adaptive-rag.md) | Studying routing and dynamic retrieval |
| [Local development](../docs/local-development.md) | Running the practical material |
| [Tutorial template](../docs/tutorial-template.md) | Contributing a new course |

When a course README and a reference document overlap, use the course README for the learning sequence and the reference document for cross-cutting detail.

---

# Notebook routes

Beginner courses use both adjacent and scenario notebooks. Intermediate and Advanced courses use the practical notebook associated with each lesson.

Specialist notebook tracks can provide longer scenario-based investigations after the corresponding curriculum topic:

- [Evaluation notebooks](../notebooks/evaluation/README.md)
- [Adaptive RAG notebooks](../notebooks/adaptive-rag/README.md)

Always follow the notebook path documented by the individual course README if repository structure changes.

---

# Suggested capstone

After completing the three tracks, design a RAG system for a realistic enterprise scenario.

Start from the simplest architecture and add only components supported by evaluation.

Your design review should answer:

1. What are the user and business tasks?
2. What evidence sources exist?
3. What is the authorization boundary?
4. What retrieval baseline was tested?
5. Which failure modes were observed?
6. Which additional retrieval or control components solve those failures?
7. How is provenance preserved?
8. When does the system abstain?
9. How are retrieval and generation evaluated separately?
10. What are the latency and cost budgets?
11. How will the system be traced in production?
12. What triggers rollback or safe degradation?

A strong capstone is not the architecture with the most components.

It is the architecture whose **complexity can be defended with evidence**.

---

# Start here

New to RAG?

➡️ Begin with **[01 — RAG Foundations](beginner/01-rag-foundations/README.md)**.

Already comfortable building basic vector-search RAG?

➡️ Start with the **[Intermediate track](intermediate/README.md)** and validate your retrieval/evaluation fundamentals.

Already operating production RAG?

➡️ Use the **[Advanced track](advanced/README.md)** as an architecture and control-pattern curriculum, but benchmark every advanced technique against your existing baseline.
