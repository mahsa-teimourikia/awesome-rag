# 05 — Evidence-first research synthesis

**Level:** Intermediate<br>
**Time:** 2–3 hours<br>
**Prerequisites:** [RAG evaluation and release gates](../04-evaluation/README.md)

## Outcome

Design a research-style RAG workflow that decomposes a question, retrieves
diverse evidence, preserves source provenance, separates findings from
limitations, represents uncertainty, and produces a reviewable cited synthesis.

## Guided notebook

Open [`research_synthesis.ipynb`](research_synthesis.ipynb). The reusable,
credential-free implementation is [`research_synthesis.py`](../../../examples/intermediate/research_synthesis.py).

```mermaid
flowchart LR
  Q[Research question] --> P[Question plan]
  P --> R[Retrieve focused evidence views]
  R --> D[Deduplicate + preserve provenance]
  D --> C[Claim-evidence map]
  C --> X[Findings, limitations, unknowns]
  X --> S[Cited synthesis or abstention]
```

## Why synthesis needs a different workflow

A research question is usually broader than a lookup. Asking only one question
can anchor retrieval to its first framing; concatenating the top passages can
amplify duplicates, hide conflict, and turn absence of evidence into a confident
conclusion. Synthesis should be treated as an evidence-management task before it
becomes a writing task.

## Step-by-step training

### 1. Bound and decompose the question

Record the decision the synthesis supports, audience, scope, time window,
definitions, and what counts as credible evidence. Plan several focused views:
direct evidence, limitations/counterarguments, operational trade-offs, and gaps.
Keep a bounded query plan and retain the original wording; an LLM planner must
return structured output and cannot invent a source or relax access policy.

### 2. Select evidence deliberately

Source quality depends on the claim. Prefer primary research, official standards,
original system documentation, and dated operational records for factual claims.
Use secondary explainers for orientation, not as the only evidence behind a
high-impact conclusion. Capture source ID, title, author/publisher, date,
version, authority, access scope, and exact supporting span.

### 3. Build a claim–evidence map before prose

Each claim has a type, supporting IDs, confidence, limitations, and conflicts.
Do not attach a single citation to a long paragraph containing multiple claims.
When sources conflict, state the disagreement, compare scope/method/date, and
avoid silently averaging them. When evidence is missing, record an open question
or abstain.

| Claim type | Synthesis behavior | Example |
| --- | --- | --- |
| Finding | state narrowly with source IDs | hybrid retrieval preserves exact signals |
| Limitation | qualify the recommendation | reranking adds latency and cost |
| Conflict | show both supported views | results differ by corpus/language |
| Open question | request research or abstain | no evidence for a tenant-specific policy |

### 4. Draft with provenance and calibrated language

Write the conclusion first only when evidence supports it. Then explain evidence,
limitations, alternatives, and unresolved questions. Use wording proportional to
evidence (`shows`, `suggests`, `is not established`) and preserve citations near
the claims. Never let retrieved instructions change the synthesis policy; source
content is data.

### 5. Evaluate the synthesis path

Measure source/claim citation coverage, evidence diversity, contradiction and
gap handling, claim support, abstention correctness, latency, and cost. Review
high-impact outputs with a rubric. Keep the query plan, source IDs, passages,
claim map, model/prompt versions, and reviewer edits in a trace.

## Practical patterns and failure modes

| Pattern | Value | Guardrail |
| --- | --- | --- |
| Multi-view retrieval | reduces single-framing bias | cap query count and deduplicate |
| Claim map | makes citations reviewable | every claim has supporting IDs or an uncertainty label |
| Counterevidence retrieval | surfaces limitations | do not force false balance where evidence is one-sided |
| Source diversity | avoids duplicate-corpus amplification | assess authority and independence |
| Human review | handles high-impact nuance | use a versioned rubric and resolve disagreements |

Avoid citation laundering (citing a source that only repeats another claim),
source-count voting, generated references, hidden conflicts, broad conclusions
from narrow evidence, and mixing tenant scopes. Authorization filters apply
before research retrieval just as they do for answer RAG.

## Checkpoint

1. Why is a counterargument query useful even when initial evidence agrees?
2. What metadata is required to reproduce a synthesis claim?
3. When should a limitation become an open question instead?
4. Why is deduplication not the same as source diversity?
5. Which claims in your application require human review?

## References

- Lewis et al., [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) — original RAG formulation.
- Es et al., [Ragas](https://arxiv.org/abs/2309.15217) — evaluation dimensions across retrieval and generation.
- NIST, [Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — governance and risk context.
- Gao et al., [RAG survey](https://arxiv.org/abs/2312.10997) — systems and evaluation overview.
