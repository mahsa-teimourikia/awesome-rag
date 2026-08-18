# Advanced 05 — Adaptive RAG: Pre-Retrieval Routing and Strategy Selection

**Level:** Advanced  
**Estimated time:** 2–3 hours  
**Notebook:** [`06_adaptive_rag.ipynb`](06_adaptive_rag.ipynb)  
**Prerequisite:** retrieval strategies, Corrective RAG, Agentic RAG

> **Repository note:** the folder is `05-adaptive-rag`, but the actual notebook is named `06_adaptive_rag.ipynb`. This README points to the existing file rather than inventing a different path.

---

## Why this lesson exists

A fixed RAG system sends every request through one retrieval path.

That can waste work or choose the wrong evidence mechanism.

Adaptive RAG adds a strategy-selection stage:

```text
query
  ↓
route decision
  ↓
direct / internal / external / structured / graph ...
```

![Adaptive routing](assets/adaptive-routing.svg)

The notebook demonstrates three simple routes:

- `direct_answer`;
- `web_search`;
- `internal_search`;

using a mock router and a LangGraph `StateGraph`.

---

## Learning objectives

After this lesson you should be able to:

- explain pre-retrieval routing;
- distinguish Adaptive RAG from Corrective RAG;
- define explicit route labels;
- build conditional routing with `StateGraph`;
- explain why an LLM is only one possible router;
- separate route selection from authorization;
- bound external-search routes;
- evaluate router errors with a confusion matrix;
- measure route-specific cost/latency/quality; and
- decide when routing complexity is justified.

---

# 1. What the notebook actually implements

Part 1 simulates structured routing output with:

```text
direct_answer
web_search
internal_search
```

Part 2 uses deterministic keyword rules to choose the same routes inside a LangGraph state machine.

The "web search" node returns a fixed string.

It does not perform live web retrieval.

The "internal search" node also returns a fixed mock result.

So the notebook teaches **routing mechanics**, not production search integrations.

---

# 2. An LLM router is not required

The old README says Adaptive RAG "solves this by inserting an LLM Router."

That is too narrow.

A router can be:

- deterministic rules;
- a small classifier;
- a structured LLM decision;
- a learned complexity model;
- a policy combining several signals.

Use the simplest router that performs well on your route-labelled dataset.

---

# 3. Route by information need, not linguistic complexity

These queries are short:

```text
"What is Python?"
"Which Python version is approved internally?"
```

Only the second necessarily needs enterprise retrieval.

Useful routing signals include:

```text
private/internal entity
freshness requirement
exact identifier
structured calculation
relationship query
source request
risk level
```

---

# 4. Adaptive vs Corrective

![Adaptive vs corrective](assets/adaptive-vs-corrective.svg)

### Adaptive

Before/around retrieval:

```text
Which strategy should we use?
```

### Corrective

After retrieval:

```text
Did the selected strategy produce sufficient evidence?
```

A robust architecture can use both:

```text
route → retrieve → grade → recover/answer
```

---

# 5. Route selection is not authorization

If a router chooses:

```text
internal_search
```

the internal search still needs:

- authenticated tenant;
- allowed collections;
- classification policy;
- source freshness.

If it chooses:

```text
web_search
```

the application still decides whether external egress is permitted.

The router proposes a route; policy authorizes it.

---

# 6. Structured output

A production route decision should look like data:

```json
{
  "route": "internal_search",
  "reason_code": "company_policy",
  "confidence_band": "high"
}
```

Avoid requiring hidden reasoning text.

A concise reason code is enough for traceability and evaluation.

---

# 7. Current LangGraph note

The notebook uses `StateGraph`, which remains part of LangGraph v1's stable core graph API.

This course does not rely on the deprecated `create_react_agent`.

Its state/node/conditional-edge architecture remains a good representation for explicit routing.

---

# 8. Add route budgets

Each route has different cost and risk.

Example:

| Route | Guardrail |
|---|---|
| direct | only supported low-risk classes |
| internal | authorization + index freshness |
| external | allowlisted egress/sources |
| graph | hop/fact budget |
| SQL | constrained typed query |
| agentic | turn/tool/cost budget |

Adaptive does not mean unconstrained.

---

# 9. Router evaluation

Build labelled route cases.

Confusion matrix examples:

```text
internal → incorrectly direct
external → incorrectly internal
direct → unnecessarily retrieved
structured → incorrectly text search
```

Measure:

- route accuracy;
- high-risk misroute rate;
- downstream answer quality;
- average/p95 latency;
- cost;
- route distribution.

A router that saves 15% cost but sends internal-policy questions to `direct_answer` is not an improvement.

---

# 10. Adaptive-RAG research context

The Adaptive-RAG paper routes among:

- no retrieval;
- single-step retrieval;
- iterative retrieval;

based on predicted question complexity.

That research is useful context, but production systems can adapt on a broader set of signals such as source type, freshness, authorization, and operation type.

---

# 11. Exercises

1. Replace the router's free-form `reasoning` with a `reason_code`.
2. Add a `structured_query` route.
3. Add route authorization separate from the router.
4. Create a route-labelled test set.
5. Measure cost saved by direct routing.
6. Add Corrective RAG grading after the internal-search route.
7. Add a case where external search is forbidden.
8. Track route distribution over time.

---

# 12. Checkpoint

1. What does Adaptive RAG decide?
2. Why is an LLM not required for routing?
3. What is the difference between Adaptive and Corrective RAG?
4. Why is route selection not authorization?
5. What signals are better than query length alone?
6. Which LangGraph API pattern does this notebook use?
7. How do you evaluate route errors?
8. When is routing complexity worth adding?

---

## What comes next

### [Advanced 06 — Production Operations](../06-production-operations/README.md)

Operate the full system with traceability, release gates, reliability budgets, and rollback controls.

---

## References

- Jeong et al. — [Adaptive-RAG](https://arxiv.org/abs/2403.14403)
- Yan et al. — [CRAG](https://arxiv.org/abs/2401.15884)
- Asai et al. — [Self-RAG](https://arxiv.org/abs/2310.11511)
- LangGraph — [v1 release notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)

---

## Key takeaway

**Adaptive RAG is strategy selection. Route the request to the minimum evidence mechanism that can satisfy quality, freshness, authorization, and risk requirements.**
