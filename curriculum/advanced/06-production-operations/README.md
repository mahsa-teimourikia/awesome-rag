# Advanced 06 — Production RAG Operations: Observe, Release, Degrade, and Recover

**Level:** Advanced  
**Estimated time:** 4–5 hours
**Notebook:** [`06_production_operations.ipynb`](06_production_operations.ipynb)
**Prerequisite:** complete the preceding advanced modules

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

The notebook turns these ideas into a credential-free Day-2 operations simulation: a versioned RAG release moves through offline gates, shadow traffic, a canary, rollback, degraded modes, incident analysis, and a new regression test.

---

## Learning objectives

After this lesson you should be able to:

- separate service reliability from RAG quality;
- define service-level objectives and release thresholds;
- instrument stage-level latency and cost;
- build parent/child traces for every important RAG stage;
- compute quality, safety, freshness, latency, and cost signals from the same request records;
- define release gates and canary rollback criteria;
- distinguish readiness, freshness, and answer quality;
- design safe degraded modes;
- version retrieval/model/prompt/index artifacts together; and
- turn incidents into regression tests.

---

# Deep dive — Production RAG operations

## Production RAG is a distributed evidence system

A production RAG request can cross many components:

```text
API/auth
  ↓
router
  ↓
retriever / database / graph / tools
  ↓
reranker
  ↓
context builder
  ↓
LLM
  ↓
verification
  ↓
response
```

Each component can fail independently. Traditional API health metrics are necessary but insufficient because a system can return HTTP 200 responses while retrieval quality, freshness, or grounding has silently degraded.

Production operations therefore needs both **software reliability telemetry** and **AI/evidence quality telemetry**.

## Observability model

A useful trace hierarchy is:

```text
rag.request
 ├─ auth.check
 ├─ route.select
 ├─ retrieval.search
 │   ├─ sparse.search
 │   └─ vector.search
 ├─ rerank
 ├─ context.build
 ├─ gen_ai.chat
 └─ answer.verify
```

Each span should record low-cardinality operational attributes and stable identifiers for deeper investigation.

Useful attributes include:

```text
trace_id
route
model/version
retriever version
index/corpus version
candidate count
selected evidence IDs
latency
token usage
policy result
terminal reason
```

Avoid turning traces into uncontrolled copies of private prompts and documents.

## OpenTelemetry and GenAI telemetry

OpenTelemetry's evolving GenAI semantic conventions provide vendor-neutral names for model operations, usage, tools, and related telemetry. The specification is still developing, so pin the convention version you implement. Prompt, message, and retrieved-document content can be sensitive and should be opt-in rather than a default trace payload.

This is a useful direction for vendor-neutral observability: instrument the application once and export traces/metrics through standard telemetry infrastructure rather than coupling operational evidence to one model vendor.

## Four operational planes

A useful production model separates:

### 1. Service reliability

- availability;
- request latency;
- dependency errors;
- saturation;
- timeouts.

### 2. Retrieval/data health

- index freshness;
- ingestion lag;
- embedding failures;
- empty retrieval rate;
- candidate count distribution;
- authorization-filter drop rate.

### 3. AI quality

- retrieval recall on sampled/labelled traffic;
- claim support;
- citation correctness;
- abstention quality;
- route correctness.

### 4. Economics

- tokens/request;
- retrieval/tool cost;
- cost by route;
- cost per successful supported task;
- cache effectiveness.

A dashboard that shows only model latency is not RAG observability.

## SLI, SLO, and release threshold

Traditional service SLOs and model-quality thresholds should be related but not conflated.

Example:

```text
Service SLO:
  99.9% requests complete within availability policy

Latency SLO:
  p95 end-to-end latency < application target

Freshness invariant:
  policy documents indexed within X minutes of publication

Quality release gate:
  Recall@k and citation support must not regress beyond tolerance
```

Quality may be measured offline or through sampled online evaluation rather than every request.

## Freshness architecture

Freshness is a first-class RAG reliability property.

Track:

```text
source_updated_at
ingested_at
embedded_at
index_published_at
query_time
```

This allows calculation of source-to-index lag. Different source classes can have different freshness requirements.

A retriever returning a perfectly relevant but obsolete policy is a production failure.

## Versioning and reproducibility

A RAG answer depends on more than the model name. Treat the deployed configuration as a release bundle:

```text
application version
prompt version
embedding model
chunker/parser version
retriever parameters
reranker model
corpus snapshot
index version
policy version
agent/tool definitions
evaluator version
generation model
```

Attach the bundle ID to traces. When a regression appears, you need to reconstruct exactly which evidence system produced the answer.

## Offline evaluation as CI/CD

A RAG release pipeline should run evaluation before promotion.

```text
change
  ↓
unit/component tests
  ↓
retrieval benchmark
  ↓
end-to-end evaluation
  ↓
safety/authorization tests
  ↓
latency/cost benchmark
  ↓
release decision
```

Hard invariants such as cross-tenant leakage should fail the release immediately. They should not be averaged into a composite quality score.

## Online evaluation

Offline datasets cannot capture every production query. Online quality monitoring can use:

- sampled human review;
- user feedback with careful interpretation;
- automated claim/evidence checks;
- route anomaly detection;
- shadow evaluation;
- production failure clustering.

LLM-as-judge can be useful for scalable signals, but it should be calibrated against human labels and not become the sole arbiter of high-risk correctness.

## Canary and shadow releases

### Canary

Send a small controlled portion of eligible traffic to the candidate release and compare:

- errors;
- latency;
- cost;
- retrieval distributions;
- quality signals.

### Shadow

Run the candidate in parallel without serving its answer. This is useful for comparing retrieval/model changes with low user risk, although it increases infrastructure/model cost and requires careful privacy handling.

## Rollback design

Rollback must consider compatibility between components.

Rolling back only the application while leaving a new incompatible index can fail. Define rollback units for:

```text
code
prompt
model
index
schema
policy
cache
```

Keep the last known-good release bundle and test rollback procedures before incidents. A rollback action is not proof of recovery: rerun the affected case and verify its terminal state, latency, authorization, and freshness behavior against the known-good contract.

## Safe degradation

Design degraded modes in advance.

Examples:

```text
reranker unavailable → use authorized base retrieval
external search unavailable → internal-only + freshness warning/abstain
verification unavailable → abstain for high-risk task
agent tool unavailable → read-only answer
fresh index unavailable → refuse freshness-sensitive query
```

Never degrade by bypassing authorization or silently removing safety checks.

## Capacity and latency engineering

End-to-end latency is a sum of stage latencies plus queueing and retries.

Important techniques include:

- parallel independent retrieval;
- bounded candidate counts;
- asynchronous I/O;
- embedding caches;
- response/prompt caching where semantics permit;
- model tiering;
- timeout budgets per dependency;
- backpressure;
- circuit breakers.

Set a latency budget per stage rather than allowing every dependency to consume the full request timeout.

## Cost engineering

Cost includes more than output tokens:

```text
ingestion parsing
embeddings
vector/graph storage
retrieval compute
reranking
LLM input/output
agent loops
tool/API calls
evaluation
observability
```

Measure cost by route and task outcome. Average cost/request can hide a small class of agentic queries that dominate spend.

## Privacy-aware telemetry

Prompts, retrieved documents, tool outputs, and traces may contain sensitive information.

Define:

- what content is logged;
- redaction rules;
- retention period;
- access controls;
- sampling;
- data residency;
- incident access procedures.

Prefer stable evidence IDs and metadata over full raw content when that is sufficient for diagnosis.

## Incident taxonomy

Classify incidents by subsystem:

```text
retrieval relevance
index freshness
authorization
model behavior
citation/provenance
routing
agent/tool execution
latency/availability
cost anomaly
```

The classification determines containment. For example, a stale index may require disabling freshness-sensitive answers, while a tenant-filter defect may require immediate shutdown of the affected route.

## Incident-to-evaluation loop

Every meaningful production failure should become a regression case:

```text
production failure
   ↓
minimal reproducible case
   ↓
root cause
   ↓
fix
   ↓
new automated evaluation/test
   ↓
release gate
```

This is how the evaluation suite evolves from synthetic examples into an operational memory of real failure modes.

## Production readiness review

Before launch, answer:

1. What is the authoritative evidence source for each route?
2. How is authorization enforced before model access?
3. What is the freshness requirement?
4. Which versions are attached to each trace?
5. What are the quality release gates?
6. What happens when each dependency fails?
7. What is the rollback unit?
8. What telemetry may contain sensitive data?
9. What is the cost/latency budget?
10. Who owns incidents and evaluation regressions?

Production RAG maturity is the ability to answer these questions consistently—not the number of frameworks in the stack.

---

# Notebook companion

The notebook is a standalone, locally runnable Day-2 operations workshop. It uses a fictional Meridian Policy Assistant and deterministic fixtures so learners can inspect every control without credentials or network calls. The numbers are reproducible teaching signals, not claims about a hosted model or vector database.

# 1. Follow one release through its operating lifecycle

The lab follows one coherent sequence:

```text
known-good V1 → candidate diff → 36-case offline gate
      → shadow comparison → frozen canary policy
      → latency incident → full-bundle rollback
      → incident-derived regression → V2.1 verification
```

The workload includes normal lookup, multi-evidence questions, freshness-sensitive requests, identifiers, no-answer cases, authorization boundaries, high-risk policies, latency outliers, and missing reranker/verifier dependencies. V1 and V2 use the same ordered dataset so comparisons are meaningful.

---

# 2. Inspect an explicit request trace

Every run captures a parent request plus child stages:

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

The lab uses `perf_counter()` around the complete request and every child stage. This is real elapsed time for simulated operations, not a fabricated latency column. Tiny waits keep the full notebook fast.

Trace attributes default to metadata-only mode. Stable evidence IDs, release versions, policy results, counts, terminal reasons, `authorization_ok`, and `freshness_violation` are retained; raw prompts and documents are not. Authorization attempts, cross-tenant evidence exposure, and forbidden-route execution remain separate signals so blocked attacks are observable without being confused with successful bypasses. The debug mode is explicitly local/testing-only and does not normalize full-payload production logging.

---

# 3. Separate usage records from prices

The notebook uses deterministic token-usage fixtures rather than character-count estimates. A full route cost includes input/output tokens, model calls, retrieval, reranking, verification, external access, and retries.

The results are labelled **synthetic cost units**. Do not use them for financial planning. A deployed system should use provider usage metadata, local-inference resource accounting, current external-service charges, infrastructure allocation, and telemetry costs.

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

# 5. Keep SLOs and release thresholds application-specific

The notebook's latency, quality, and error-budget values are teaching policy, not universal RAG standards. Set them from user workflow, business impact, risk class, dependency behavior, and cost envelope.

Keep service objectives separate from quality release thresholds:

```text
p95 < 3 seconds
99.9% availability
```

are examples.

They are not universal RAG standards.

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

The notebook represents this as a typed `ReleaseBundle` and prints the complete V1→V2 diff before promotion. Rollback restores the recorded last-known-good bundle rather than changing only the model or application version.

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

The lab's typed gate returns blockers and warnings under four visible categories: hard invariants, quality blockers, operating limits, and regression warnings. Controlled retrieval-loss, latency, and authorization-bypass mutations prove that failed candidates are rejected. Thresholds are evaluated both absolutely and, where appropriate, relative to the known-good baseline.

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

The teaching canary uses stable-hash assignment and prints its frozen policy before execution. For reproducibility, the failure-injection exercise intentionally chooses a long-query case ID that belongs to the canary cohort. This demonstrates rollback mechanics, not the probability that random production sampling will discover a rare failure. A real canary needs sufficient cohort size, a justified observation window, representative route/risk slices, and named decision ownership.

Shadow traffic is exercised first: V2 runs beside V1 but its answer is never served. This reduces exposure, not duplicated cost or privacy obligations.

When rollback is requested, the notebook reports the incompatible components—such as prompt, index, or cache—rather than a generic rejection. It then reruns the affected canary case on V1 and verifies behavior before declaring recovery.

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

The notebook tests a predeclared dependency matrix for reranker, external source, verifier, and fresh-index failures across low- and high-risk requests. It also exposes retry amplification and a circuit-breaker decision so dependency failure cannot become an unbounded loop.

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

Prefer metadata-only telemetry by default. Keep raw prompts and documents behind a distinct, audited debug mode. Also avoid high-cardinality metric labels; stable identifiers belong in traces or controlled logs.

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

The canary failure becomes a structured incident record and then a long-query regression case. V2.1 must pass the expanded dataset before it can be reconsidered. This gives the evaluation suite operational memory instead of leaving the lesson at “write a postmortem.”

---

# 13. Exercises

1. Add a retrieval timeout budget and prove it cannot consume the generation budget.
2. Introduce an index/schema mismatch and extend rollback compatibility checks.
3. Add a fourth release failure: an invalid citation on a critical route.
4. Calculate retry amplification by dependency and terminal reason.
5. Add route-specific thresholds without hiding global security invariants.
6. Add a test that fails when raw document text enters metadata-only telemetry.
7. Replace the in-memory collector with OpenTelemetry spans while preserving the trace schema.
8. Design a canary sample size and observation window for an expected production traffic volume.
9. Add cache namespaces and prove incompatible V1/V2 entries cannot collide.
10. Turn an authorization incident into a regression case that hard-blocks release.

---

# 14. Checkpoint

1. Why must a release bundle contain more than the model name?
2. Which signals are hard blockers, and which are operational warnings?
3. What risk does shadow traffic reduce, and which costs and risks remain?
4. Why must canary thresholds be frozen before inspecting candidate outcomes?
5. How does cost per successful supported answer differ from average request cost?
6. Why can readiness be green while freshness is red?
7. What must a safe degraded mode always preserve?
8. How can retries increase both latency and incident severity?
9. What makes a rollback bundle compatible?
10. What durable artifact should every production incident add to the release process?

---

# References

- OpenTelemetry — [Semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- OpenTelemetry — [Generative AI attribute registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
- Google SRE — [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- Google SRE Workbook — [Canarying Releases](https://sre.google/workbook/canarying-releases/)
- Arize Phoenix — [Tracing documentation](https://arize.com/docs/phoenix/tracing)
- LangSmith — [Observability documentation](https://docs.langchain.com/langsmith/observability)
- Grafana Cloud — [AI agent observability](https://grafana.com/docs/grafana-cloud/observe-and-act/agent-observability/)
- Datadog — [LLM Observability](https://docs.datadoghq.com/llm_observability/)
- Qdrant — [Production documentation](https://qdrant.tech/documentation/guides/installation/)
- NIST — [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- OWASP — [Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

## Key takeaway

**Production RAG is an operated system, not a prompt. Observe every important stage, release versioned artifacts deliberately, and degrade capability without degrading safety.**

## Continue to the advanced capstone

Apply these operational controls across text, structured, graph, multimodal, external, and bounded-agent evidence paths in **[Course 07 — Enterprise RAG Platform Capstone](../07-enterprise-rag-capstone/README.md)**.
