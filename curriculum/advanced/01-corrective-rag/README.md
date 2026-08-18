# Advanced 01 — Corrective RAG: Bounded Recovery After Retrieval Failure

**Level:** Advanced  
**Estimated time:** 2–3 hours  
**Notebook:** [`01_corrective_rag.ipynb`](01_corrective_rag.ipynb)  
**Prerequisite:** complete the intermediate retrieval and evaluation track

---

## Why this lesson exists

A fixed RAG pipeline often assumes:

```text
retrieve → generate
```

That assumption fails when retrieval is empty, irrelevant, stale, incomplete, or filtered down by authorization.

**Corrective RAG (CRAG)** adds an explicit evidence-quality decision after retrieval:

```text
retrieve
   ↓
grade evidence
   ↓
accept / recover / abstain
```

The notebook demonstrates this twice:

1. a transparent Python controller; and
2. a LangGraph `StateGraph` with conditional routing.

![Corrective RAG control loop](assets/corrective-control-loop.svg)

The important idea is not "always fall back to web search." It is:

> **When evidence is inadequate, choose only from a bounded, policy-approved recovery set.**

---

## Learning objectives

After this lesson you should be able to:

- explain why retrieval quality is a control decision;
- distinguish corrective routing from ordinary reranking;
- define strong, weak, and insufficient evidence states;
- build a finite recovery graph;
- separate internal retrieval failure from source unavailability;
- explain why external search is not a universally safe fallback;
- define retry, latency, and cost budgets;
- preserve route/evidence traces;
- distinguish Corrective RAG from Adaptive RAG and Agentic RAG; and
- evaluate whether correction improves outcomes over a fixed baseline.

---

# 1. What the notebook actually implements

The course folder contains:

```text
README.md
01_corrective_rag.ipynb
```

There is no `lab.py`, and the notebook is not named `corrective_rag.ipynb`.

The notebook first implements:

```text
Retrieve → Grade → Web-search mock → Final context
```

with `ManualCRAG`.

It then implements a LangGraph graph:

```text
retrieve
   ↓
grade_documents
   ├─ relevant → generate
   └─ weak     → web_search → generate
```

The "web search" in the notebook is a **mock function returning a fixed string**. It does not perform real internet retrieval.

---

# 2. Correction is a policy, not "try again"

A production controller needs:

```text
allowed routes
route-specific authorization
max attempts
max elapsed time
max cost
terminal states
reason codes
```

![Finite recovery policy](assets/recovery-policy.svg)

A useful terminal state is often:

```text
insufficient_authorized_evidence
```

rather than another unbounded retry.

---

# 3. Grade evidence, not model confidence

A retrieval grade should answer:

> Is the available evidence sufficient for this task?

Possible signals include:

- candidate relevance;
- coverage of required concepts;
- source authority;
- freshness;
- authorization;
- conflict;
- redundancy.

Do not interpret a single similarity score or reranker score as calibrated answer confidence.

For high-risk systems, tune decision thresholds on labelled validation data and separately measure:

- false accept: weak evidence accepted;
- false abstain: strong evidence rejected.

---

# 4. Recovery routes

| Failure | Candidate recovery |
|---|---|
| Vocabulary mismatch | rewrite query |
| Exact identifier missed | lexical/hybrid retriever |
| Relevant result poorly ranked | reranker |
| Wrong internal index queried | approved alternate internal source |
| Missing critical parameter | clarification |
| Internal corpus legitimately incomplete | approved external source |
| Evidence remains weak | abstain / escalate |

A recovery route must not silently widen:

- tenant scope;
- data classification;
- network access;
- tool permissions.

---

# 5. External retrieval is a trust-boundary change

The notebook's web-search node is useful pedagogically because it makes routing visible.

In production, external retrieval introduces additional risks:

- source authority;
- stale or poisoned content;
- indirect prompt injection;
- egress/privacy exposure;
- SSRF-style tool risks;
- retention and citation requirements.

Therefore:

> "Internal retrieval failed" does **not** automatically imply "search the web."

The route must be explicitly permitted for the task and data class.

---

# 6. LangGraph update

The notebook's `StateGraph` approach remains a valid low-level control-flow pattern in LangGraph v1.

LangGraph v1 kept the graph primitives—state, nodes, edges, conditional edges—as stable core APIs.

For agent construction, however, the old `langgraph.prebuilt.create_react_agent` API used later in this curriculum is deprecated in LangGraph v1 in favor of LangChain's `create_agent`.

This CRAG notebook uses `StateGraph` directly, so the core orchestration idea remains current.

---

# 7. Important notebook limitation: retry state is not enforced

The notebook defines:

```python
retries: int
```

in `GraphState`.

But the graph does **not** increment or enforce that field.

So the current notebook demonstrates conditional recovery, but not a complete bounded retry loop.

A production implementation should explicitly implement something like:

```text
attempt += 1
if attempt >= MAX_ATTEMPTS:
    abstain
```

Do not claim loop protection merely because a `retries` field exists.

---

# 8. Corrective vs Adaptive vs Agentic RAG

![RAG routing patterns](assets/routing-patterns.svg)

### Corrective RAG

Decision happens **after evidence retrieval**:

```text
Did retrieval succeed?
```

### Adaptive RAG

Decision happens **before or around retrieval strategy selection**:

```text
Which route should this query use?
```

### Agentic RAG

The system grants a model more runtime discretion to choose among tools/steps.

These patterns can be combined, but should not be conflated.

---

# 9. Evaluate the controller

Compare fixed RAG and corrective RAG on the same dataset.

Measure:

- answerable-query success;
- unsupported-answer rate;
- false-abstention rate;
- retrieval recovery rate;
- attempts per query;
- route distribution;
- p95 latency;
- cost per supported answer;
- unauthorized-route attempts.

Correction is worthwhile only when the quality/risk improvement justifies added latency and complexity.

---

# 10. Exercises

1. Replace the mock relevance test with three evidence grades: `strong`, `weak`, `empty`.
2. Add an explicit `attempts` counter and terminate after two recovery attempts.
3. Add a clarification route rather than always using external search.
4. Add a lexical fallback for exact identifiers.
5. Record the selected route and evidence IDs in state.
6. Create one case where web retrieval is forbidden by policy.
7. Compare fixed RAG and CRAG on 20 labelled cases.

---

# 11. Checkpoint

1. What failure does Corrective RAG address?
2. Why is a recovery route different from a retry?
3. Why is external search not a default fallback?
4. What should a retrieval grader measure?
5. Why is a reranker score not truth confidence?
6. Which LangGraph concept does the notebook use?
7. Does the notebook currently enforce its `retries` state?
8. How would you prove correction is worth the extra cost?

---

## What comes next

### [Advanced 02 — GraphRAG](../02-graphrag/README.md)

Move from correcting retrieval failures to retrieving explicit relationships across multiple evidence items.

---

## References

- Yan et al. — [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884)
- Asai et al. — [Self-RAG](https://arxiv.org/abs/2310.11511)
- LangGraph — [v1 migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1)
- LangGraph — [What's new in v1](https://docs.langchain.com/oss/python/releases/langgraph-v1)

---

## Key takeaway

**Corrective RAG is a bounded evidence-recovery controller. If recovery cannot establish sufficient authorized evidence within policy and budget, the correct outcome is abstention—not another guess.**
