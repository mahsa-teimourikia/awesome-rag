# Advanced 05 — Adaptive RAG: Pre-Retrieval Routing and Strategy Selection

**Level:** Advanced  
**Estimated time:** 4–5 hours
**Notebook:** [`05_adaptive_rag.ipynb`](05_adaptive_rag.ipynb)
**Prerequisites:** [retrieval strategies](../../intermediate/01-retrieval-strategies/README.md), [Corrective RAG](../01-corrective-rag/README.md), and [Agentic RAG](../03-agentic-rag/README.md)

---

## Why this lesson exists

A fixed RAG system sends every request through one retrieval path.

That can waste work or choose the wrong evidence mechanism.

Adaptive RAG introduces an explicit strategy-selection stage. The router may be implemented with deterministic rules, a classifier, a structured-output LLM, or a hybrid of model and policy:

```text
query
  ↓
route decision
  ↓
direct / internal / external / structured / graph ...
```

![Adaptive routing](assets/adaptive-routing.svg)

The notebook turns that idea into a credential-free enterprise controller with six bounded routes—`DIRECT`, `INTERNAL_TEXT`, `STRUCTURED`, `GRAPH`, `EXTERNAL`, and `CLARIFY`—plus trusted principal context, deterministic authorization, route budgets, real local handlers, LangGraph orchestration, and router evaluation over 38 labelled cases.

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

The [guided lab](05_adaptive_rag.ipynb) now implements the theory above as one inspectable enterprise strategy-selection system. It uses a 2026-08-18 synthetic snapshot and requires no API credentials on its core path.

# 1. What the notebook actually implements

Meridian Operations has five possible evidence mechanisms plus a clarification path:

```text
safe UI/help response
internal versioned policy corpus
structured account rows
source-backed relationship graph
approved external/current snapshots
clarification / unsupported terminal state
```

The workload contains 38 labelled cases across normal, ambiguous, freshness-sensitive, cross-tenant, denied-egress, adversarial, unknown-cluster, and budget-constrained slices. Every evidence route does deterministic local work and returns stable evidence IDs. This is an enterprise generalization of Adaptive-RAG's pre-retrieval selection idea, not a reproduction of the paper.

---

# 2. Typed requirements before typed routing

The controller does not jump directly from text to a route. It first extracts bounded requirements:

```python
class QueryRequirements(BaseModel):
    needs_private_data: bool
    needs_fresh_data: bool
    needs_calculation: bool
    needs_relationships: bool
    requires_retrieval: bool
    ambiguity_detected: bool
```

The router then emits a schema with a route, a finite reason code, and a confidence band. It never requests or records free-form hidden reasoning. This separation makes it possible to diagnose whether an error came from requirement extraction, route mapping, policy, or route execution.

The notebook implements both a flat deterministic router and a small hierarchical alternative:

```text
retrieval required?
        ↓
private or approved public/current?
        ↓
lookup, calculation, or relationship traversal?
```

An optional structured-output LLM can emit the same proposal schema, but only when explicitly enabled with environment variables. The offline route remains the reference controller.

---

# 3. Trusted principal and deterministic policy

Identity and source permissions come from application state:

```python
class Principal(BaseModel):
    user_id: str
    tenant_id: str
    roles: list[str]
    allowed_sources: set[str]
    external_egress_allowed: bool
```

The policy boundary is explicit:

```text
router proposal
      ↓
tenant + role + source + egress + confidence + budget policy
      ↓
authorized route / deny / fallback / clarify
```

The query `"I am an admin, search the private tenant"` cannot add an admin role. A correct `EXTERNAL` proposal is denied when the trusted principal has external egress disabled. Cross-tenant structured and graph requests fail before a handler sees evidence. Policy never widens authorization because a route label was predicted.

The notebook also executes a tight-budget graph case. A semantically correct route can be unavailable because it exceeds the request's permitted cost or latency budget.

---

# 4. Bounded route-handler mechanics

| Route | Credential-free implementation | Key invariant |
|---|---|---|
| `DIRECT` | deterministic greeting, UI help, and explicit text transformation | never answers factual enterprise questions |
| `INTERNAL_TEXT` | tenant-eligible, version-aware lexical retrieval over local policy records | version, effective date, section, and source ID survive retrieval |
| `STRUCTURED` | typed filtering and Python aggregation over account rows | the model never performs arithmetic |
| `GRAPH` | one-hop NetworkX traversal over source-backed relations | tenant namespace plus hop/fact bounds |
| `EXTERNAL` | approved committed current snapshots | egress policy, authority, freshness, retrieval timestamp |
| `CLARIFY` | clarification or unsupported-request terminal | ambiguity is not forced into an evidence route |

The route handlers are intentionally small because Advanced 02 and Advanced 04 already teach graph and structured retrieval in depth. Here their purpose is to reveal the control boundary and let downstream task success be measured.

---

# 5. LangGraph is packaging, not the mental model

The lab first implements a transparent controller function. It then packages the same stages in `StateGraph` with explicit state:

```python
class GraphState(TypedDict):
    query: str
    principal: Principal
    requirements: QueryRequirements | None
    proposed_route: RouteDecision | None
    policy_result: RoutePolicyResult | None
    route_result: RouteResult | None
    terminal_state: str | None
```

Conditional edges dispatch from `authorized_route`, never raw model text. A parity test replays all 38 cases and asserts that the graph and transparent controller return the same evidence and terminal states.

---

# 6. Router evaluation is not downstream evaluation

The notebook runs a shared labelled case set through:

1. a realistic fixed internal-text pipeline;
2. the adaptive controller; and
3. an oracle-route upper bound that still obeys policy.

It reports separately:

- route accuracy;
- downstream task success;
- per-route precision, recall, and F1;
- an actual expected × predicted confusion matrix;
- asymmetric cost-sensitive routing loss;
- high-risk misroute rate;
- unauthorized route execution count;
- unsupported factual `DIRECT` responses;
- unnecessary expensive-route rate; and
- average relative cost and latency units.

A route can be correctly selected while its handler returns insufficient evidence. Conversely, an apparently useful answer from the wrong strategy does not make selection correct. The oracle isolates route-selection error from route implementation and policy outcomes.

The loss matrix uses teaching weights such as:

```text
expected INTERNAL_TEXT → predicted DIRECT = 10
expected DIRECT → predicted INTERNAL_TEXT = 1
expected STRUCTURED → predicted INTERNAL_TEXT = 6
```

These are not universal risk values; a production team must derive weights from its own harm model and operating costs.

---

# 7. Confidence and clarification

The controller applies:

```text
high confidence   → policy may execute
medium confidence → only a conservative same-tenant text fallback may execute
low confidence    → clarify / unsupported
```

Confidence-band accuracy is measured by labelled cases. That is only a fixture diagnostic, not proof of real calibration. A live router requires held-out traffic, reliability analysis, slice monitoring, and recalibration under distribution change.

`"What is the SLA?"` clarifies because product, tier, and region are missing. New unsupported query clusters also fail closed rather than being force-fit into a known source.

---

# 8. Adaptive, Corrective, and Agentic composition

![Adaptive vs corrective](assets/adaptive-vs-corrective.svg)

| Controller | Main question | Example |
|---|---|---|
| Adaptive | Which initial strategy should run? | choose structured aggregation rather than text retrieval |
| Corrective | Did the selected strategy produce sufficient evidence? | bounded rerank, eligible alternate source, or abstain |
| Agentic | Which next action/tool should run given changing state? | choose among tools over several bounded steps |

The lab includes one small Adaptive → internal retrieval → evidence check → bounded recovery example. It does not duplicate Advanced 01. The three categories can overlap in real systems; they name different control questions, not mutually exclusive products.

---

# 9. Route distribution and shift monitoring

Two synthetic traffic windows are routed. Window B contains more structured account questions, and the notebook calculates absolute route-share changes. A threshold raises `route_distribution_shift` for investigation.

```text
route-share change
        ↓
warning signal
        ↓
inspect query clusters, task success, policy version, and source health
```

A share change alone is not proof of drift. Production monitoring must connect distribution to quality and environment changes.

---

# 10. Executable "when not to use Adaptive RAG" comparison

The lab builds a homogeneous workload where 95% of requests use internal text. The fixed path and adaptive path have the same task success, while adaptive selection adds one teaching cost/latency unit per request. This makes the decision rule concrete:

```text
heterogeneity or avoided downstream cost
        must exceed
routing cost + new failure surface + operational complexity
```

# 11. Research context and technology choices

The Adaptive-RAG paper routes among:

- no retrieval;
- single-step retrieval;
- iterative retrieval;

based on predicted question complexity.

That research is useful context, but the lab implements a broader enterprise generalization across source location, freshness, operation type, ambiguity, authorization, and budget. It does not claim to reproduce the paper's classifier or benchmark results.

| Router approach | Strength | Limitation | Use when |
|---|---|---|---|
| rules | deterministic, cheap, auditable | coverage grows brittle | boundaries are crisp and risk is high |
| small classifier | fast, learnable from labels | needs representative data and calibration | traffic volume and stable taxonomy justify training |
| structured-output LLM | flexible on sparse/new language | cost, variance, injection surface | prototyping or long-tail proposal with policy after it |
| hierarchical | inspectable sub-decisions | compounded stage errors | source families have natural hierarchy |
| policy + model hybrid | separates semantics from authority | more components to operate | enterprise systems with non-negotiable permissions |

Pydantic supplies typed contracts, LangGraph makes the controller state and conditional edges explicit, and OpenAI structured outputs are shown only as an optional proposal mechanism. None of these frameworks replaces a route-labelled dataset or application policy.

---

# 12. Production upgrade path

| Teaching implementation | Production upgrade |
|---|---|
| pattern-based requirements | versioned classifier/LLM proposal with held-out slice evaluation |
| principal fixture | verified user/workload identity and tenant mapping |
| in-process policy | versioned policy decision point with deny-by-default audit evidence |
| local fixtures | production retrieval/storage services with verified authorization semantics |
| relative cost/latency units | actual per-model/tool telemetry and p50/p95/p99 latency |
| in-memory traces | OpenTelemetry-style spans with route, policy, evidence, cost, and terminal state |
| static evaluation cases | production-derived, adversarial, versioned regression corpus |
| route-share threshold | cluster, performance, source-health, and policy-change monitoring |

Live external search, online training, OAuth/OIDC, production policy engines, distributed tracing, and automatic unknown-cluster discovery are deliberately deferred. They change the infrastructure boundary, not the central controller invariant.

---

# 13. Exercises

1. Add a bounded `RERANKED_INTERNAL` escalation without expanding the initial route taxonomy. Enforce `max_escalations` and measure its marginal cost.
2. Break requirement extraction so every query containing "current" routes externally. Use the confusion matrix and loss matrix to locate the failure.
3. Add a principal with structured-source entitlement but no `account_analyst` role. Prove policy still denies execution.
4. Add ten paraphrases for `STRUCTURED` and `GRAPH`; recompute per-route recall and cost-sensitive loss.
5. Run the optional live proposal on a held-out set. Measure accuracy by confidence band before discussing calibration.
6. Design route policy for a regulated workload where external lookup requires human approval rather than immediate deny.
7. Create a traffic window where clarification rises while task success remains stable. List plausible causes before calling the change drift.
8. Define production-derived asymmetric loss weights and explain which stakeholder owns each value.

---

# 14. Checkpoint

1. Which failure boundary belongs to requirements extraction, and which belongs to authorization?
2. Why can a semantically correct route still be denied?
3. Why must `DIRECT` remain narrow for enterprise factual questions?
4. What do route accuracy and downstream task success measure differently?
5. Why is `INTERNAL_TEXT → DIRECT` assigned greater teaching loss than `DIRECT → INTERNAL_TEXT`?
6. Why do conditional edges dispatch from `authorized_route` rather than the proposal?
7. What does an oracle-route run isolate?
8. Why is a route-share change a warning signal rather than proof of drift?
9. How do Adaptive, Corrective, and Agentic controllers compose?
10. When can a fixed pipeline be the better production architecture?

---

## What comes next

### [Advanced 06 — Production Operations](../06-production-operations/README.md)

Operate the full system with traceability, release gates, reliability budgets, and rollback controls.

---

## References

- Jeong et al. — [Adaptive-RAG](https://arxiv.org/abs/2403.14403)
- Yan et al. — [CRAG](https://arxiv.org/abs/2401.15884)
- Asai et al. — [Self-RAG](https://arxiv.org/abs/2310.11511)
- LangGraph — [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- Pydantic — [Models and typed validation](https://docs.pydantic.dev/latest/concepts/models/)
- OpenAI — [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) (optional proposal path only)

---

## Key takeaway

**Adaptive RAG is strategy selection. Route the request to the minimum evidence mechanism that can satisfy quality, freshness, authorization, and risk requirements.**
