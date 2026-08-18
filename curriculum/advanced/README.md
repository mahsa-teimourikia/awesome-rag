# Advanced RAG Curriculum

**Track goal:** Design RAG systems that can recover from retrieval failure, traverse relationships, select evidence tools dynamically, combine structured and multimodal evidence, route queries adaptively, and operate safely in production.

```text
01 Corrective RAG
       ↓
02 GraphRAG
       ↓
03 Agentic RAG
       ↓
04 Structured & Multimodal RAG
       ↓
05 Adaptive RAG
       ↓
06 Production Operations
```

This track is not about making RAG "more autonomous" for its own sake.

It is about introducing **bounded control mechanisms** only where the simpler retrieval architecture has a measured limitation.

## Prerequisites

You should already be able to:

- build and inspect a conventional RAG pipeline;
- compare lexical, dense, and hybrid retrieval;
- enforce metadata/permission boundaries;
- use query planning and reranking;
- evaluate retrieval separately from answer quality;
- preserve source provenance;
- synthesize multiple sources; and
- work with a vector database.

## What you will be able to do

By the end of the track, you should be able to:

- detect insufficient retrieval evidence and recover safely;
- define finite corrective policies;
- model relationship evidence with provenance;
- retrieve bounded multi-hop graph paths;
- distinguish deterministic workflows from agents;
- separate tool selection from authorization;
- combine deterministic structured computation, OCR, text, and visual evidence;
- route requests to different evidence strategies;
- evaluate routing and agent trajectories;
- define operational traces, release gates, canaries, and rollback criteria; and
- design degraded modes that reduce capability without weakening safety.

---

# Course sequence

| Course | Core question | Main control boundary | Production concern |
|---|---|---|---|
| **01 — Corrective RAG** | What should happen when retrieval is weak? | Evidence grading + bounded recovery | False answers, retries, fallback risk |
| **02 — GraphRAG** | What if the answer depends on relationships? | Entity/relation/path provenance | Multi-hop correctness |
| **03 — Agentic RAG** | When should a model choose the next evidence tool? | Tool permissions + trajectory budgets | Autonomy and side effects |
| **04 — Structured & Multimodal RAG** | What if evidence is numeric, tabular, OCR, or visual? | Modality-specific evidence contracts | Determinism and provenance |
| **05 — Adaptive RAG** | Which retrieval strategy should run for this request? | Pre-retrieval routing + policy | Cost, latency, misrouting |
| **06 — Production Operations** | How do we release and operate the complete system? | Observability + release/rollback controls | Reliability and recoverability |

---

# 01 — Corrective RAG

Corrective RAG adds an explicit decision after retrieval:

```text
retrieve
   ↓
grade evidence
   ├─ sufficient → answer
   └─ insufficient → approved recovery
                         ↓
                     verify
                         ↓
                 answer / abstain
```

Recovery must be finite.

Possible routes include:

- query rewrite;
- alternate retriever;
- clarification;
- approved external source;
- abstention.

External search is not a universal fallback. It changes the trust and egress boundary.

**Exit criterion:** the system terminates safely when sufficient authorized evidence cannot be recovered within budget.

---

# 02 — GraphRAG

Graph retrieval is useful when relationships themselves are the information need.

A trustworthy graph fact needs:

```text
subject
relation
object
source
version
authorization scope
```

Study:

- entity extraction;
- entity resolution;
- typed relationships;
- directed traversal;
- bounded hops;
- graph + source-text retrieval;
- local vs corpus-level graph search patterns.

Do not treat connectivity as semantic correctness.

**Exit criterion:** a multi-hop answer can be traced through valid directional edges back to supporting sources.

---

# 03 — Agentic RAG

An agent is justified when the next useful evidence action genuinely depends on what the system just discovered.

Prefer deterministic workflows when the path is already known.

```text
model proposes tool
        ↓
schema validation
        ↓
authorization / policy
        ↓
optional approval
        ↓
execution
        ↓
receipt / evidence
```

Tool selection is not authorization.

Separate:

- read;
- propose;
- execute.

Bound:

- turns;
- tool calls;
- time;
- cost;
- allowed tools.

**Exit criterion:** the agent cannot expand its own permissions and can terminate with answer, clarification, abstention, escalation, or approval-required.

---

# 04 — Structured & Multimodal RAG

Different evidence types need different contracts.

```text
numeric calculation → deterministic code / SQL
text lookup         → retrieval
OCR field           → extracted text + region
visual interpretation → multimodal model + locator
```

Do not use an LLM as a calculator when deterministic computation is available.

Do not treat arbitrary generated Python execution as the default structured-data query architecture.

Distinguish:

- **computed** facts;
- **observed** facts;
- **inferred** interpretations.

**Exit criterion:** every material claim carries evidence semantics appropriate to its modality.

---

# 05 — Adaptive RAG

Adaptive RAG chooses the strategy before or around retrieval:

```text
query
   ↓
route
   ├─ direct
   ├─ internal retrieval
   ├─ structured query
   ├─ graph
   └─ approved external retrieval
```

The router can be:

- rules;
- classifier;
- structured LLM output;
- learned model;
- combined policy.

An LLM router is an implementation option, not the definition of Adaptive RAG.

Combine Adaptive and Corrective RAG when appropriate:

```text
route → retrieve → grade → recover / answer
```

**Exit criterion:** route selection improves measured quality/cost/latency without violating authorization or high-risk routing constraints.

---

# 06 — Production Operations

The final course treats RAG as an operated system.

Observe:

```text
request
 ├─ authorization
 ├─ routing
 ├─ retrieval
 ├─ reranking
 ├─ tool/data access
 ├─ generation
 └─ verification
```

Track a release bundle:

```text
prompt
chunking
embedding model
retriever config
reranker
corpus snapshot
index
policy
evaluator
generation model
```

Separate:

- readiness;
- freshness;
- offline quality;
- online behavior.

Safe degradation reduces capability without weakening authorization, provenance, or verification requirements.

**Exit criterion:** you can identify a bad release, reconstruct what ran, rollback safely, and convert the incident into a regression test.

---

# Advanced architecture principles

## 1. Bounded autonomy

Every dynamic controller needs:

```text
allowed actions
budgets
terminal states
authorization
traceability
```

## 2. Evidence before fluency

A sophisticated model does not compensate for weak evidence.

## 3. Authorization outside model discretion

The model may request an operation. Trusted application policy decides whether the operation is allowed.

## 4. Provenance through every modality

Graph edges, database rows, OCR regions, retrieved passages, and tool outputs all need durable evidence identifiers.

## 5. Evaluate trajectories, not only answers

For dynamic systems measure:

- route correctness;
- recovery success;
- tool-call correctness;
- repeated actions;
- unauthorized attempts;
- latency;
- cost;
- final evidence support.

## 6. Complexity must earn its place

Compare each advanced architecture to the simpler baseline.

If GraphRAG, an agent, corrective recovery, or adaptive routing does not materially improve the target task under realistic constraints, do not deploy it.

---

# End-to-end reference architecture

```text
request
   ↓
identity + authorization
   ↓
adaptive route
   ├───────────────────────────────────────────────┐
   ↓                                               ↓
retrieval / graph / structured / multimodal    direct path
   ↓
evidence grading
   ↓
corrective recovery if permitted
   ↓
optional bounded agentic evidence gathering
   ↓
evidence ledger
   ↓
generation / synthesis
   ↓
claim + citation verification
   ↓
answer / abstain / clarify / escalate
   ↓
trace + evaluation + operational metrics
```

Not every application needs every box.

The architecture should be assembled from measured requirements.

---

# Track completion challenge

Design and evaluate a governed enterprise RAG system for a realistic domain.

It should include only the advanced components justified by the task, but the design review must consider:

- adaptive routing;
- corrective recovery;
- graph retrieval;
- structured/multimodal evidence;
- bounded agentic tools;
- authorization;
- provenance;
- evaluation;
- latency/cost budgets;
- observability;
- release/rollback;
- safe degradation.

Your final architecture review should answer:

1. Which failure mode does each advanced component solve?
2. What simpler baseline was tested first?
3. What evidence proves the component helps?
4. What new risk does it introduce?
5. Which deterministic control contains that risk?
6. How will the system fail safely?
7. How will you detect regression after release?

---

# Completion standard

Finishing the advanced track should mean more than being able to implement several RAG patterns.

You should be able to decide:

> **which pattern should not be used.**

That judgment—supported by evaluation, provenance, authorization, operational evidence, and explicit trade-offs—is the difference between a RAG demo and an enterprise RAG architecture.
