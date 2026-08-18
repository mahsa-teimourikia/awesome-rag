# Intermediate RAG Curriculum

**Track goal:** Turn a basic RAG pipeline into a measurable, permission-aware retrieval system that can choose better candidates, rerank them, evaluate failures, synthesize evidence, and operate against a real vector database.

```text
01 Retrieval Strategies
        ↓
02 Metadata & Permissions
        ↓
03 Query Planning & Reranking
        ↓
04 RAG Evaluation
        ↓
05 Research Synthesis
        ↓
06 Qdrant Local
```

The intermediate track is where RAG stops being a demo and becomes an engineered retrieval subsystem.

## Prerequisites

Before starting, you should be comfortable with:

- the retrieval → context → generation loop;
- embeddings and top-k retrieval;
- chunking trade-offs;
- source provenance;
- citations and abstention;
- inspecting retrieval results independently from the final answer.

## What you will be able to do

By the end of the track, you should be able to:

- combine lexical and semantic retrieval;
- use query expansion without losing control of provenance;
- enforce metadata and tenant restrictions before ranking;
- distinguish filtering from relevance;
- plan multi-part retrieval tasks;
- rerank candidates with a stronger relevance model;
- evaluate retrieval and generation separately;
- build labelled RAG evaluation datasets;
- synthesize multiple evidence items without losing source identity;
- implement local vector retrieval with Qdrant;
- define release gates for retrieval changes; and
- justify architectural complexity with measured improvement.

---

# Course sequence

| Course | Core question | Practical focus | Enterprise concern |
|---|---|---|---|
| **01 — Retrieval Strategies** | How do we improve candidate recall? | Dense, lexical, hybrid retrieval, query expansion, fusion | Coverage and retrieval robustness |
| **02 — Metadata & Permissions** | Which evidence is the user allowed to retrieve? | Filters, tenant scope, classification, authorization boundaries | Data isolation and least privilege |
| **03 — Query Planning & Reranking** | How do we turn a broad query into better evidence? | Query decomposition, candidate generation, reranking | Precision, latency, cost |
| **04 — RAG Evaluation** | How do we know a change improved the system? | Retrieval metrics, answer support, citations, regression tests | Release quality |
| **05 — Research Synthesis** | How do we combine evidence across sources? | Evidence tables, contradiction handling, synthesis | Traceability and source diversity |
| **06 — Qdrant Local** | How does the design map to a real vector database? | Collections, payloads, filters, search, local operations | Implementation and operational boundaries |

---

# 01 — Retrieval Strategies

A single dense retriever is not sufficient for every query type.

Compare:

```text
lexical retrieval
dense retrieval
hybrid retrieval
query expansion
fusion
```

The objective is **candidate recall before expensive precision stages**.

Exact identifiers, product codes, acronyms, names, and error strings often benefit from lexical retrieval. Semantic paraphrases often benefit from dense retrieval.

Hybrid retrieval combines complementary signals rather than assuming one retriever dominates all query classes.

**Exit criterion:** you can compare retrieval strategies on a labelled dataset and explain why one wins for a particular query class.

---

# 02 — Metadata & Permissions

Authorization is not a reranking feature.

The safe order is conceptually:

```text
authenticated identity
        ↓
authorized scope
        ↓
candidate retrieval
        ↓
ranking
```

Do not retrieve a broad cross-tenant candidate set and hope a later model removes unauthorized evidence.

Study:

- tenant filters;
- document classification;
- source type;
- effective dates;
- payload metadata;
- authorization-aware retrieval;
- filter selectivity.

**Exit criterion:** you can prove that unauthorized candidates never enter the model context.

---

# 03 — Query Planning & Reranking

Some questions need multiple retrieval operations.

Example:

```text
"Compare policy A and policy B and explain the exception."
```

A planner may decompose the information need, retrieve candidates, then rerank them.

Keep the stages distinct:

```text
plan
  ↓
candidate retrieval
  ↓
rerank
  ↓
context selection
```

Reranking improves ordering. It does not fix candidates that were never retrieved.

**Exit criterion:** you can measure candidate recall before reranking and ranking quality after reranking.

---

# 04 — RAG Evaluation

Evaluation is the control system for the rest of the curriculum.

Separate:

### Retrieval

- Recall@k;
- Precision@k;
- MRR;
- nDCG where appropriate.

### Answer/evidence

- claim support;
- citation correctness;
- answerability;
- abstention behavior;
- task success.

### Operations

- latency;
- cost;
- route distribution;
- failure rate.

A single "RAG score" hides too much.

**Exit criterion:** you have a reproducible evaluation set and can block a regression before release.

---

# 05 — Research Synthesis

Research-style questions require more than retrieving one passage.

A disciplined synthesis pipeline can look like:

```text
question
   ↓
sub-questions
   ↓
source-backed evidence
   ↓
evidence table
   ↓
conflict / gap analysis
   ↓
synthesis with citations
```

Important concerns:

- source diversity;
- duplicated evidence;
- contradictions;
- evidence freshness;
- unsupported synthesis claims.

**Exit criterion:** every material synthesis claim can be traced to one or more evidence records.

---

# 06 — Qdrant Local

Use a real vector database to connect retrieval theory to implementation.

Study:

- collections;
- vectors;
- payload metadata;
- filtering;
- local persistence;
- similarity search;
- index configuration;
- retrieval diagnostics.

Qdrant is an implementation vehicle, not the definition of RAG.

The design principles from earlier courses—authorization, provenance, evaluation, and filtering—remain the architecture.

**Exit criterion:** you can build a local collection, retrieve with payload filters, and evaluate the result rather than merely demonstrate that search returns something.

---

# Cross-track architecture

By the end of Intermediate, the baseline should resemble:

```text
request
   ↓
identity + authorization
   ↓
query analysis
   ↓
hybrid candidate retrieval
   ↓
reranking
   ↓
evidence selection
   ↓
generation / synthesis
   ↓
citation validation
   ↓
answer or abstention
```

Every major stage should be independently testable.

---

# Evaluation discipline

Do not add an advanced technique because it is fashionable.

For every change:

```text
baseline
   ↓
labelled evaluation set
   ↓
candidate architecture
   ↓
quality + latency + cost + risk comparison
   ↓
keep / reject
```

Examples:

- hybrid retrieval should improve candidate recall for a defined query class;
- reranking should improve ranking metrics;
- query expansion should not increase irrelevant retrieval beyond acceptable bounds;
- filters should preserve authorization invariants;
- synthesis should improve task success without increasing unsupported claims.

---

# Track completion challenge

Build an enterprise-style retrieval service that:

- supports lexical + dense candidate generation;
- enforces metadata/tenant restrictions;
- optionally reranks authorized candidates;
- preserves evidence IDs and source metadata;
- evaluates retrieval with labelled relevance;
- evaluates answer support separately;
- performs one multi-source synthesis task;
- stores/searches vectors in local Qdrant; and
- compares the improved system against the beginner baseline.

The final report should explain **what improved, what did not, and what the additional complexity cost**.

---

# Next track

## Advanced RAG

The advanced track introduces **bounded corrective recovery, relationship retrieval, agentic evidence selection, structured/multimodal evidence, adaptive routing, and production operations**.

> **Progression principle:** advanced architecture is justified by a measured failure mode—not by the availability of a framework.
