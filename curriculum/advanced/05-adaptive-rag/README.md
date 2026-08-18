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

# Deep dive — Adaptive RAG and retrieval routing

## Why adaptive retrieval exists

Not every question deserves the same pipeline.

```text
"What is 2 + 2?"                         → no retrieval
"What is our current travel policy?"     → internal retrieval
"What happened in today's market?"       → fresh external retrieval
"Total open claims for account X?"       → structured query
"How is service A connected to vendor B?"→ graph retrieval
```

A fixed pipeline pays unnecessary cost on simple questions and can use the wrong evidence mechanism for specialized questions. Adaptive RAG introduces a **routing decision** that selects the appropriate strategy for the current request.

## Research origin

The Adaptive-RAG research framework learns to choose among no retrieval, single-step retrieval, and iterative retrieval based on question complexity. A smaller classifier is trained to predict the appropriate complexity/strategy class.

The enterprise generalization is broader: route based not only on question complexity but on **evidence requirements**.

## Routing dimensions

Useful signals include:

### Knowledge location

```text
parametric/general
private internal corpus
external current information
structured system of record
graph/relationship store
```

### Freshness

```text
stable knowledge
version-specific knowledge
real-time/current knowledge
```

### Operation type

```text
lookup
comparison
aggregation
multi-hop relation
research/synthesis
```

### Risk and policy

```text
public
internal
confidential
regulated
side-effecting
```

### Expected complexity

```text
single-hop
multi-part
iterative investigation
```

A strong router models these dimensions explicitly rather than using vague "easy vs hard" labels alone.

## Router implementations

### Rules

Best when route boundaries are crisp:

```text
if requires_current_web_data → external_search
if asks_for_account_total → structured_query
```

Advantages: deterministic, cheap, auditable. Weakness: brittle on ambiguous language.

### Classifier

A small model predicts a route label. Useful when many labelled examples exist and latency matters.

### LLM structured routing

A general model emits a typed route decision. Flexible and easy to prototype, but more expensive and less deterministic.

### Hierarchical router

Break one difficult decision into several:

```text
public vs private?
   ↓
lookup vs compute vs relationship?
   ↓
which retriever?
```

This can make errors easier to diagnose.

### Policy + model hybrid

Often the best enterprise design:

```text
model proposes route
        ↓
deterministic policy removes forbidden routes
        ↓
execute allowed strategy
```

## Route taxonomy

A production route set should be small enough to evaluate.

Example:

```text
DIRECT
INTERNAL_TEXT
STRUCTURED
GRAPH
EXTERNAL
CLARIFY
```

Avoid dozens of overlapping labels. If two routes are operationally identical, they probably do not need separate router classes.

## Routing vs query planning

Routing chooses **which strategy/system** should handle the request.

Query planning determines **how to execute within that strategy**.

Example:

```text
router → INTERNAL_TEXT
planner → split comparison into policy A + policy B + exception
retriever → fetch candidates
```

Keeping these concerns separate improves observability and evaluation.

## Adaptive + Corrective architecture

Adaptive and Corrective RAG compose naturally:

```text
query
  ↓
adaptive route
  ↓
retrieval strategy
  ↓
evidence grade
  ├─ sufficient → answer
  └─ weak → corrective recovery
```

The adaptive controller chooses the initial strategy; the corrective controller decides what to do when the selected strategy fails.

Do not create an uncontrolled cycle where each controller repeatedly invokes the other.

## Confidence and fallback

A router should have an explicit uncertain state. Forcing every ambiguous request into one route creates silent errors.

Possible policy:

```text
high confidence → execute route
medium confidence → safe broad/internal route
low confidence → clarify
```

Confidence must be calibrated against route correctness, not treated as a model's subjective certainty.

## Cost-aware routing

Adaptive retrieval is partly an economics problem.

Suppose strategies have expected cost and quality:

```text
DIRECT      low cost, limited freshness
VECTOR      moderate cost
RERANKED    higher cost
ITERATIVE   much higher cost
GRAPH       indexing + query cost
```

The objective is not simply maximum quality. It is to choose the least expensive strategy that satisfies the task's quality and risk requirements.

This can be framed as constrained optimization:

```text
minimize expected cost(route)
subject to quality(route, query) ≥ threshold
           policy(route, user) = allowed
           latency(route) ≤ budget
```

## Authorization-aware routing

Never let the router widen access.

The route decision may depend on trusted context such as:

```text
user role
tenant
allowed data sources
network egress policy
```

But those values should come from application state, not user text or model inference.

A route can be valid semantically and forbidden operationally.

## Cascaded retrieval

Another adaptive pattern is progressive escalation:

```text
cheap retriever
   ↓ if insufficient
hybrid + reranker
   ↓ if insufficient
iterative/graph route
```

This resembles corrective retrieval, but the design goal is cost-aware escalation. Keep the number of stages bounded and measure how often each stage is reached.

## Router evaluation

A route-labelled dataset should include ambiguous and adversarial cases.

Measure:

- overall route accuracy;
- per-route precision/recall;
- confusion matrix;
- high-risk misroute rate;
- unnecessary expensive-route rate;
- downstream task success;
- latency/cost by route;
- clarification rate.

Not all errors have equal cost. `DIRECT` instead of `INTERNAL_TEXT` may create an unsupported answer, while `INTERNAL_TEXT` instead of `DIRECT` may only waste latency. Use a cost-sensitive error matrix.

## Distribution shift

Router performance can drift as users, products, and corpora change. Monitor:

```text
route distribution
unknown/clarify rate
per-route quality
route overrides
new query clusters
```

A sudden rise in one route may indicate prompt changes, new user behavior, or a broken classifier.

## When not to use Adaptive RAG

Do not add routing if:

- almost every request needs the same source;
- route labels cannot be defined clearly;
- routing errors are more costly than the saved compute;
- the traffic volume does not justify complexity;
- a deterministic intent check solves the problem.

Adaptive RAG is valuable when workload heterogeneity is real and measurable.

---

# Notebook companion

The sections below connect the theory above to the executable notebook, identify deliberate simplifications, and highlight production gaps.

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
