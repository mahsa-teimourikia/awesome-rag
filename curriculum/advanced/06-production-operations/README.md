# Advanced 06 — Production RAG Operations: Observe, Release, Degrade, and Recover

**Level:** Advanced  
**Estimated time:** 2–3 hours  
**Notebook:** [`05_production_operations.ipynb`](05_production_operations.ipynb)  
**Prerequisite:** complete the preceding advanced modules

> **Repository note:** this folder is `06-production-operations`, but the existing notebook is named `05_production_operations.ipynb`. This README intentionally links to the real file.

---

## Why this lesson exists

A RAG system can be grounded and still be operationally unsafe.

Examples:

- index freshness is outside policy;
- retrieval latency spikes;
- a new embedding version reduces recall;
- a fallback loop multiplies cost;
- citation verification is unavailable;
- telemetry leaks sensitive text.

Production quality combines:

```text
retrieval quality
answer support
authorization
freshness
latency
cost
observability
recoverability
```

![Production operating loop](assets/production-operating-loop.svg)

The notebook demonstrates a small subset of this: callback-based LLM timing and simulated cost accounting around a mock LCEL pipeline.

---

## Learning objectives

After this lesson you should be able to:

- separate service reliability from RAG quality;
- define service-level objectives and release thresholds;
- instrument stage-level latency and cost;
- understand what the notebook's callback does and does not measure;
- define release gates and canary rollback criteria;
- distinguish readiness, freshness, and answer quality;
- design safe degraded modes;
- version retrieval/model/prompt/index artifacts together; and
- turn incidents into regression tests.

---

# 1. What the notebook actually implements

The notebook:

- defines example SLO concepts;
- defines a "cost per grounded answer" idea;
- creates `ProductionMetricsCallback`;
- measures LLM callback latency;
- estimates cost from **character length** using simulated prices;
- runs a mock retrieval + prompt + fake LLM pipeline.

This is useful instrumentation training.

It is not production billing or complete distributed tracing.

---

# 2. Important instrumentation limitation

`mock_retrieve` is a plain Python function.

It does not emit LangChain retriever callback events.

Therefore the custom callback does **not** actually record retrieval latency as a retriever span.

The notebook also accumulates:

```text
total LLM latency
```

rather than true end-to-end latency.

For production, capture explicit spans:

```text
request
 ├─ authorization
 ├─ retrieval
 ├─ reranking
 ├─ context build
 ├─ generation
 └─ verification
```

![Trace spans](assets/trace-spans.svg)

---

# 3. Cost estimates are simulated

The notebook estimates token cost from character lengths and hard-coded example rates.

Do not use those values for financial planning.

Production accounting should use:

- actual provider usage metadata where available;
- actual local-inference resource accounting;
- current model/provider pricing;
- infrastructure cost allocation;
- external-tool/API costs.

Pricing changes over time.

---

# 4. Define cost per successful supported answer directly

A robust composite metric is:

```python
cost_per_success = total_cost / successful_supported_answers
```

where `successful_supported_answers` is counted from evaluated outcomes.

Avoid multiplying several aggregate rates together and assuming independence:

```text
n × faithfulness_rate × citation_rate × grounded_rate
```

Those metrics may overlap and be statistically dependent.

Count successful cases directly whenever possible.

---

# 5. SLOs are application-specific

The notebook's values such as:

```text
p95 < 3 seconds
99.9% availability
```

are examples.

They are not universal RAG standards.

Set SLOs from:

- user workflow;
- business impact;
- dependency reliability;
- risk class;
- cost envelope.

Also separate:

### Service SLO

```text
availability / latency
```

from:

### Quality release threshold

```text
retrieval recall
citation validity
false-answer rate
```

Model-quality metrics do not behave exactly like traditional service availability SLOs.

---

# 6. Readiness vs freshness vs quality

![Operational signals](assets/operational-signals.svg)

### Readiness

Can required dependencies serve requests?

### Freshness

Is the corpus/index current enough for this answer class?

### Offline quality

Should this configuration be promoted?

### Online behavior

Is production traffic behaving as expected?

A healthy HTTP endpoint does not mean the knowledge base is current.

---

# 7. Version the release bundle

Track together:

```text
prompt version
chunking version
embedding model
retriever config
reranker config
corpus snapshot
index version
policy version
evaluator version
generation model
```

Without this bundle, rollback and incident reconstruction become guesswork.

---

# 8. Release gate

A useful release gate can combine:

```text
retrieval metric thresholds
citation invariants
abstention behavior
security tests
latency budget
cost budget
freshness
```

Hard safety constraints such as cross-tenant isolation should not be averaged with softer quality metrics.

---

# 9. Canary and rollback

Before a release, define:

```text
canary population
monitoring window
rollback thresholds
previous stable version
cache compatibility
index compatibility
owner
```

Do not invent fixed percentages or monitoring durations as universal rules.

Choose them according to traffic volume and risk.

---

# 10. Safe degradation

When dependencies fail, degrade capability rather than policy.

Possible safe modes:

```text
disable optional reranking
disable external retrieval
serve dated read-only evidence
disable side-effecting tools
abstain when verification unavailable
```

Unsafe degradation:

```text
skip authorization
skip citation validation
silently use stale data
```

---

# 11. Telemetry and privacy

Trace enough to diagnose:

```text
trace ID
route
version bundle
candidate IDs
source versions
latency
token usage
policy result
terminal reason
```

Do not automatically log:

- full private documents;
- secrets;
- raw tool credentials;
- unnecessary user PII;
- hidden model reasoning.

Use redaction and retention policies.

---

# 12. Incident loop

```text
detect
  ↓
classify
  ↓
contain
  ↓
investigate
  ↓
recover
  ↓
verify
  ↓
add regression case
```

Production incidents should improve the evaluation suite.

---

# 13. Exercises

1. Add explicit timers around retrieval and generation.
2. Compute true end-to-end latency.
3. Replace character-based token estimates with a real tokenizer or provider usage record.
4. Define `successful_supported_answer` as a per-case boolean and compute cost per success.
5. Simulate stale-index policy and safe degradation.
6. Define a release bundle with all relevant versions.
7. Create a canary rollback condition.
8. Redesign the trace schema to avoid storing raw sensitive text.

---

# 14. Checkpoint

1. What does the notebook callback actually measure?
2. Why is character count not reliable billing data?
3. How should cost per successful supported answer be calculated?
4. What is the difference between readiness and freshness?
5. Why are example SLO numbers not universal?
6. Which failures should hard-block a release?
7. What should safe degradation preserve?
8. What information is required for rollback?

---

# References

- OpenTelemetry — [Documentation](https://opentelemetry.io/docs/)
- Google SRE — [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- Qdrant — [Production documentation](https://qdrant.tech/documentation/guides/installation/)
- NIST — [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- OWASP — [Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## Key takeaway

**Production RAG is an operated system, not a prompt. Observe every important stage, release versioned artifacts deliberately, and degrade capability without degrading safety.**
