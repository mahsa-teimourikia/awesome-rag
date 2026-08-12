# 05 — Evidence-first research synthesis

**Level:** Intermediate  
**Time:** 2–3 hours  
**Prerequisites:** [RAG evaluation and release gates](../04-evaluation/README.md)

## Learning objectives

After this lesson you will be able to:

- explain why research synthesis requires different retrieval and composition
  strategies than a single-document lookup;
- design a bounded question decomposition that produces diverse evidence views
  without unconstrained scope expansion;
- select evidence by source authority, independence, and temporal relevance;
- build a claim-evidence map that makes every assertion traceable before prose is written;
- detect and explicitly represent temporal conflicts, contradictions, and evidence gaps;
- apply calibrated language proportional to the strength of evidence;
- evaluate a synthesis for coverage, redundancy, source diversity, claim support,
  citation completeness, and abstention correctness; and
- define which claims require human review before a synthesis is shared.

## Outcome

Design a research-style RAG workflow that decomposes a question, retrieves diverse
evidence, preserves source provenance, separates findings from limitations, represents
uncertainty, and produces a reviewable cited synthesis.

## Guided notebook

Open [`research_synthesis.ipynb`](research_synthesis.ipynb). The reusable, credential-free implementation is [`lab.py`](lab.py).

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

A research question is usually broader than a lookup. Asking only one query can
anchor retrieval to its first framing; concatenating the top passages can amplify
duplicates, hide conflict, and turn absence of evidence into a confident conclusion.
Synthesis should be treated as an evidence-management task before it becomes a
writing task.

The core difference between lookup RAG and synthesis RAG:

| Dimension | Lookup RAG | Synthesis RAG |
|---|---|---|
| Query count | One | Multiple focused views |
| Evidence relationship | Independent, ranking-based | Structured: supporting, conflicting, uncertain |
| Provenance need | Source ID per answer | Source ID per claim |
| Conflict handling | N/A (single source) | Explicit representation of disagreement |
| Gap handling | Abstain | Record open question |
| Output form | Single grounded answer | Claim-evidence map → cited synthesis |
| Human review trigger | High-risk individual claims | All synthesis outputs above a risk threshold |

---

## Step 1: Bound and decompose the question

Record *before retrieval*:
- the decision the synthesis supports
- the intended audience and their authorized scope
- scope boundaries (product, region, time window, tenant)
- definitions of key terms
- what counts as credible evidence for this question

Then plan several focused retrieval *views* from different angles:

| View | Purpose | Example query |
|---|---|---|
| Direct evidence | Primary claims and findings | "hybrid retrieval precision improvements" |
| Limitations and counterevidence | Scope constraints and trade-offs | "hybrid retrieval limitations and failure cases" |
| Operational trade-offs | Cost, latency, complexity | "hybrid retrieval latency cost production" |
| Temporal range | Time-bound evidence | "hybrid retrieval performance 2023 2024" |
| Conflicts and disagreements | Where sources disagree | "BM25 vs dense retrieval conflicting results" |
| Open questions | Areas without evidence | "hybrid retrieval sparse corpora" |

**Key constraint:** an LLM query planner must return structured output and cannot
invent sources, relax access policy, or generate new evidence. The question plan
must be inspectable and logged.

---

## Step 2: Select evidence deliberately by authority

Not all evidence is equal. Source quality depends on the claim being made.

### Authority ranking

| Source type | Best for | Limitations |
|---|---|---|
| Primary research (peer-reviewed) | Factual claims about measured phenomena | May be narrow, domain-specific, or dated |
| Official standards and specifications | Compliance and definitional claims | May lag current practice |
| System documentation (official) | Implementation and operational claims | May not reflect deployed reality |
| Operational records (dated) | Incident and performance claims | Specific to one environment |
| Secondary explainers / blog posts | Orientation and background | Should not be sole evidence for a high-impact claim |
| Community forums | Known patterns and workarounds | Unvalidated; wide variance in quality |

**Principle:** prefer primary research, official standards, original system
documentation, and dated operational records for factual claims. Use secondary
sources for orientation, not as the only evidence behind a high-impact conclusion.

### Evidence fields to capture per source

| Field | Purpose |
|---|---|
| Source ID + stable URL | Traceability and reproducibility |
| Title, author, publisher | Attribution |
| Publication/update date | Temporal validity |
| Version identifier | Distinguishes document revision |
| Authority level | Informs confidence weighting |
| Access scope (tenant/ACL) | Authorizes use in synthesis |
| Exact supporting span | The specific text that supports the claim |
| Retrieval timestamp | When evidence was retrieved (may differ from publication date) |

---

## Step 3: Build a claim-evidence map before writing prose

The most important structural discipline in research synthesis: **build the
claim-evidence map before writing any prose**. Do not start with a conclusion
and then find supporting sources — that reverses the evidence direction.

### Claim types

| Claim type | How to represent | Example |
|---|---|---|
| **Finding** | State narrowly with source IDs and confidence | "Hybrid retrieval improves Recall@10 by 8–15% on BEIR [source-1, source-2]" |
| **Limitation** | Qualify the finding with scope constraints | "The improvement is smaller on short-document corpora [source-2]" |
| **Conflict** | Show both supported views; compare scope, method, date | "Source-3 reports no improvement on synonym-heavy queries; source-4 shows 12% gain — different corpora" |
| **Open question** | Record as unknown; request research or abstain | "No evidence found for sparse multilingual corpora; this requires further investigation" |

### Handling temporal conflicts

Sources from different dates may make contradictory claims. This is not the same
as a logical contradiction — it often reflects real change over time.

**Detection:** compare `publication_date` of conflicting sources. If dates differ
significantly, the conflict may be temporal, not logical.

**Representation options:**
1. Report both findings with dates: "Source-1 (2022) reports X; source-2 (2024) reports Y — this may reflect model improvements"
2. Prefer the more recent source with explicit date qualification
3. Request updated evidence before drawing a conclusion

**Never silently average or ignore a temporal conflict.** A synthesis that
presents a 2022 finding as current is a freshness failure that looks like a
factual claim.

### Handling logical contradictions

When sources make directly contradictory factual claims:

1. Verify the sources are making the same claim (same corpus, same metric, same conditions)
2. Compare scope, methodology, and sample size
3. If the conflict cannot be resolved: present both positions, state the disagreement explicitly, and either request expert review or abstain on the conflicting point

**Citation laundering:** one common failure is citing Source B, which itself only
cites Source A, without noting that both trace to the same underlying evidence.
Two citations to the same primary study are one data point, not two independent
confirmations.

### Evidence clustering

When many sources make the same point, grouping them by claim rather than by source
prevents the synthesis from amplifying a single well-cited result into an apparent
consensus:

```
Claim: "Hybrid retrieval outperforms BM25 on semantic queries"
  Supporting: [source-1, source-3, source-7]
  Constraining: [source-4 — only on English corpora]
  Contradicting: [source-9 — no improvement on technical jargon]
  Gaps: [no evidence for low-resource languages]
```

---

## Step 4: Draft with provenance and calibrated language

### Calibrated language

Use language that is proportional to evidence strength. Systematic overstatement
is a synthesis failure even when every cited source is real.

| Evidence quality | Appropriate language |
|---|---|
| Strong consensus, multiple independent primary sources | "shows", "demonstrates", "establishes" |
| Single high-quality study or strong signal with one source | "suggests", "indicates", "finds" |
| Mixed or limited evidence | "may", "appears to", "some evidence suggests" |
| Expert opinion, single source, or secondary only | "according to [source]", "one analysis argues" |
| Not established in indexed corpus | "is not established in available evidence", "remains an open question" |

### Provenance near the claim

Citations must appear adjacent to the specific claim they support, not collected
in a footnotes section. A paragraph containing three factual claims with one
collective footnote is not a properly cited synthesis.

```
❌  "Hybrid retrieval improves precision and reduces latency, with some
     trade-offs in complexity. [source-1, source-2, source-3]"

✓   "Hybrid retrieval improves Recall@10 by 8–15% on BEIR benchmarks
     [source-1]. This improvement is smaller on sparse corpora [source-2].
     Operational latency increases by 30–80ms at p95 when a reranker is added
     [source-3]."
```

### Source content is data

Never let retrieved text alter the synthesis policy. The question plan, scope,
and authorization constraints were set before retrieval. Retrieved content is
evidence to be evaluated — it cannot expand scope, relax access control, or
change the reviewer requirement.

---

## Step 5: Evaluate the synthesis path

| Dimension | What to measure | Failure signal |
|---|---|---|
| Source diversity | Fraction of sources that are independent | All evidence traces to one primary study |
| Citation completeness | Fraction of claims with at least one citation | Assertions without provenance |
| Claim support | Fraction of claims supported by cited evidence | Claims that overstate or misrepresent sources |
| Conflict coverage | Are all detected conflicts explicitly represented? | Conflicts silently averaged or ignored |
| Evidence gaps | Are open questions recorded? | Absence of evidence treated as evidence of absence |
| Abstention accuracy | Does the synthesis decline unanswerable synthesis questions? | Confident synthesis built on thin or conflicting evidence |
| Temporal currency | Are time-sensitive claims qualified with dates? | Recent-looking synthesis citing old evidence |
| Human review trigger | Are high-impact outputs routed for review? | Synthesis with legal/financial/medical impact released without review |

---

## Practical patterns and failure modes

| Pattern | Value | Guardrail |
|---|---|---|
| Multi-view retrieval | Reduces single-framing bias | Cap query count; authorize all queries before running |
| Claim-evidence map | Makes citations reviewable before prose | Every claim has supporting IDs or an explicit uncertainty label |
| Counterevidence retrieval | Surfaces limitations | Do not force false balance where evidence is genuinely one-sided |
| Source diversity check | Avoids amplifying one study as a consensus | Verify independence, not just count |
| Temporal conflict detection | Prevents outdated evidence from appearing current | Compare publication dates; prefer recent and state the difference |
| Human review gate | Handles high-impact nuance | Use a versioned rubric; resolve disagreements; log decisions |

Avoid: citation laundering, source-count voting (more sources ≠ stronger claim),
generated references, hidden conflicts, broad conclusions from narrow evidence,
mixing tenant scopes, and confusing retrieval recency with source authority.

---

## Checkpoint

1. Why is a counterargument retrieval view useful even when initial evidence seems unanimous?
2. What metadata is required to determine whether two conflicting sources disagree
   logically or temporally?
3. When should a limitation become an open question rather than a qualifying clause?
4. Why is deduplication (removing duplicate chunks) not the same as source diversity?
5. A synthesis cites 12 sources. On inspection, 10 cite the same primary study.
   What is this failure called, and how would you detect it?
6. Which claims in your application domain require human review regardless of
   automated evaluation scores?
7. What is the correct response when two primary sources make directly contradictory
   factual claims about the same phenomenon?

## References

- Lewis et al., [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) — original RAG formulation.
- Es et al., [Ragas](https://arxiv.org/abs/2309.15217) — evaluation dimensions across retrieval and generation.
- NIST, [Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — governance and risk context.
- Gao et al., [RAG survey](https://arxiv.org/abs/2312.10997) — systems and evaluation overview.
- Anthropic, [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) — multi-view evidence retrieval.
