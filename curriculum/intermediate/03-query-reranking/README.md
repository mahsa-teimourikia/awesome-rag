# Intermediate 03 — Two-Stage Retrieval: Cross-Encoder Reranking

**Level:** Intermediate  
**Estimated time:** 3–4 hours
**Notebook:** [`03_query_reranking.ipynb`](03_query_reranking.ipynb)  
**Prerequisites:** [Retrieval Strategies](../01-retrieval-strategies/README.md); [Metadata and Permissions](../02-metadata-permissions/README.md)

---

## Why this lesson exists

First-stage retrieval is optimized to search a large corpus quickly and achieve high candidate recall.

That does not mean the best evidence will be ranked first.

This notebook demonstrates the classic two-stage architecture:

```text
authorized query
      ↓
first-stage retrieval
      ↓
candidate set
      ↓
cross-encoder reranker
      ↓
context selection
```

> **A reranker improves ordering of retrieved candidates. It cannot recover evidence that never entered the candidate set.**

![Two-stage retrieval](assets/two-stage-retrieval.svg)

The runnable lesson is specifically a **controlled cross-encoder reranking experiment**. Query rewriting, decomposition, HyDE, hybrid retrieval, learned sparse retrieval, and late interaction remain related design guidance rather than competing implementations inside this notebook.

---

## Learning objectives

After this lesson you should be able to:

- distinguish first-stage recall from second-stage precision;
- explain bi-encoder vs cross-encoder scoring;
- rerank a bounded candidate set;
- explain why rerankers cannot recover missing candidates;
- measure candidate recall across retrieval budgets;
- compute MRR, nDCG, Precision@k, any-evidence support, and evidence completeness on one labelled query set;
- inspect per-query rank movement and diagnose regressions;
- measure local median and p95 stage latency;
- distinguish `candidate_k` from downstream `top_n`;
- avoid using reranker scores as calibrated truth probabilities;
- keep authorization filters upstream of reranking; and
- decide from aggregate evidence whether the reranker helps this corpus and workload.

---

## 1. Bi-encoder retrieval

Dense first-stage retrieval independently embeds:

```text
query
document
```

and compares their vectors.

This allows document vectors to be precomputed, which makes search efficient.

The trade-off is limited token-level interaction between the query and candidate at scoring time.

---

## 2. Cross-encoder reranking

A cross-encoder scores:

```text
[query, document]
```

jointly.

That allows attention across both sequences and typically produces a more precise relevance judgement.

More precisely: cross-encoders often improve fine-grained relevance ranking because they jointly process the query and candidate. They do not guarantee improvement, and they add another learned failure mode.

The notebook uses the direct Sentence Transformers interface so every pair remains visible:

```python
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
reranker = CrossEncoder(RERANKER_MODEL)
```

The cross-encoder produces a **model-specific relevance score used for ranking**.

```text
reranker score
≠ probability the answer is correct
≠ calibrated confidence
```

---

## 3. Candidate recall comes first

Suppose the relevant document ranks 3rd.

A reranker can move it to rank 1.

Suppose the relevant document is not returned at all.

A reranker cannot help.

![Reranker boundary](assets/reranker-boundary.svg)

Therefore measure:

```text
Recall@candidate_k
```

before deciding the reranker is the problem.

---

## 4. Candidate and context budgets are different

Do not rerank the entire corpus.

Production architectures bound the expensive second stage:

```text
millions of chunks
      ↓
first-stage retrieval
      ↓
20–100 candidates
      ↓
cross-encoder
      ↓
3–10 final passages
```

The exact numbers must come from representative evaluation and latency budgets. This notebook evaluates `candidate_k = 3, 5, 10, 20` on the same labelled set.

- `candidate_k` controls how much first-stage evidence the reranker may inspect.
- `top_n` controls how many reranked candidates survive for downstream context.

Increasing `top_n` cannot repair evidence missing from `candidate_k`. Increasing `candidate_k` can improve recall, but increases the number of query–candidate pairs scored by the cross-encoder.

---

## 5. Current integrations and teaching models

Install the focused dependencies with:

```bash
pip install langchain-chroma langchain-core sentence-transformers chromadb pandas
```

The notebook uses:

```python
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer, CrossEncoder
```

with explicit teaching baselines:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
```

These local models download from Hugging Face on first use and require no paid API. They are compact, inspectable baselines—not claims about the best model for every domain.

---

## 6. Ranking score is not answer confidence

The notebook reflection says the cross-encoder outputs a relevance score and suggests it can be used for abstention.

That needs a qualification.

Cross-encoder scores are useful ranking signals, but are not automatically:

```text
P(answer is correct)
```

If you want to use a score threshold for abstention:

1. evaluate the score distribution on answerable and unanswerable cases;
2. tune on a validation set;
3. test on held-out data;
4. monitor false-answer and false-abstention rates.

Thresholds must be empirically calibrated using representative answerable and unanswerable validation data. Even a no-answer query still receives a highest-ranked candidate and a highest score; that does not make the question answerable.

### Domain mismatch

The MS MARCO baseline was trained for general web/search relevance. Legal, medical, financial, code, and organization-specific evidence can use different terminology and relevance criteria. Evaluate on domain labels before adoption; fine-tuning and hard-negative training are advanced extensions, not part of this lab.

---

## 7. Authorization order

Safe:

```text
authorization filter
      ↓
first-stage retrieval
      ↓
reranker
      ↓
context
```

Unsafe:

```text
retrieve unauthorized candidates
      ↓
rerank
      ↓
filter afterward
```

The reranker itself receives document text, so it is inside the security boundary and must only see authorized candidates. The notebook uses a small `retrieve_candidates(...)` interface whose filter comes from the trusted principal, then asserts every candidate matches that principal. It intentionally does not duplicate the full authorization policy from Intermediate 02.

---

## 8. Reranking evaluation

Compare baseline vs reranked results on the same cases.

The notebook labels relevance by stable `chunk_id`, not by filenames or keyword guesses. Baseline and reranker are evaluated on the exact same query/candidate occurrences.

Useful metrics:

- Recall@candidate_k — how much relevant evidence entered the candidate set?;
- MRR — did the first relevant result move up? MRR does not measure completeness when a question requires multiple passages;
- nDCG@k — did relevant evidence move toward earlier ranks across the ordered list?;
- Precision@k — how much retained context is relevant?;
- Any-support@k — does final `top_n` contain at least one relevant passage?;
- Evidence-completeness@k — what fraction of all required passages survived into final `top_n`?;
- median/p95 retrieval, reranking, and total local latency.

First-stage distance and cross-encoder score remain in separate columns because they are different scoring functions used at different stages. Do not compare or linearly combine them without a deliberately calibrated and evaluated fusion method.

Do not celebrate a better example ranking without measuring a representative set.

---

## 9. Related query-transformation techniques

Query rewriting, multi-query expansion, HyDE, and decomposition are useful when the correct evidence is **missing from the candidate set**.

Reranking is useful when the evidence is **present but poorly ordered**.

That diagnostic distinction should remain explicit:

| Failure | First intervention |
|---|---|
| Relevant evidence absent | improve retrieval/query representation |
| Relevant evidence present but low-ranked | rerank |
| Wrong tenant/source present | authorization/filtering |
| Correct evidence reaches model but answer is wrong | generation/evaluation |

---

## 10. Controlled Atlas experiment

The notebook expands the original three-passage Atlas example into an enterprise corpus of approximately forty chunks. It includes:

- current and historical R-17 policies;
- internal-system and third-party-provider rules;
- supplier identity and onboarding records;
- security questionnaires, SLAs, incident procedures, and procurement controls;
- exact identifiers, overlapping terminology, near-identical policies, hard negatives, drafts, and unrelated-but-plausible evidence; and
- excluded cross-tenant distractors to preserve the authorization invariant.

Each chunk has stable metadata:

```python
{
    "document_id": "r17-vendor-policy-v2",
    "chunk_id": "r17-vendor-policy-v2#applicability",
    "source": "r17_vendor_policy_v2.md",
    "section": "applicability",
    "tenant_id": "atlas",
}
```

The evaluation set contains answerable, multi-relevant, identifier, lexical-overlap, semantic-hard-negative, version-sensitive, missing-candidate, regression-probe, and no-answer slices. A multi-evidence question labels every passage needed to establish the relationship; no single passage is silently called the complete answer.

Historical and draft records are deliberately left inside this lesson's tenant-authorized candidate space so learners can observe version-confusion hard negatives. That is a controlled ranking experiment, not production lifecycle guidance. For a production **current-policy-only** workflow, lifecycle eligibility should normally remove historical, superseded, expired, or draft records before reranking. Reranking must not decide which policy version is authoritative.

---

## 11. Candidate-budget and `top_n` experiments

For every query and every candidate budget, the lab performs the same sequence:

```text
retrieve candidates
→ retain base ranks/distances
→ score exactly those candidates
→ retain reranker scores/ranks
→ evaluate against stable relevance labels
```

The missing-candidate experiment demonstrates that a relevant passage absent at `candidate_k = 3` cannot be recovered by reranking, then shows whether it becomes available at `candidate_k = 10`.

The separate `top_n = 1, 3, 5` experiment asks how much useful evidence fits in the downstream context budget. It reports both **any-support** and **evidence completeness**: these are identical for a single-source question but differ when several chunks are jointly required. Changing `top_n` does not change first-stage candidate recall.

---

## 12. Rank movement and failure analysis

For every labelled relevant chunk, inspect:

```text
base rank
reranked rank
rank delta
status: improved | unchanged | regressed | missing from candidates
```

A reranker is another learned model. Aggregate gains can coexist with individual regressions, hard-negative promotions, or version confusion. Diagnose failures only after checking candidate recall:

| Failure class | Interpretation / first response |
|---|---|
| Candidate recall failure | relevant evidence never reached stage two; improve retrieval/query representation or corpus coverage |
| Reranker regression | relevant candidate entered stage two but moved down; inspect labels, hard negatives, model/domain fit |
| Hard-negative confusion | overlapping terms outranked the supported passage; add representative negatives/evaluation |
| Version confusion | historical/draft wording displaced current evidence; strengthen lifecycle filters and domain labels |
| Multi-evidence incompleteness | only part of the evidence set survived `top_n`; increase/diversify context selection carefully |
| Authorization scope issue | forbidden evidence entered candidate/reranker state; treat as a hard security failure |
| Expected no-answer | the labelled case is intentionally unsupported; abstaining or reporting insufficient evidence is correct behavior |
| Corpus/source coverage failure | a case expected to be answerable has no indexed supporting source; reranking cannot repair source coverage |

The notebook reports two views that answer different questions: **query-level MRR outcome** tracks the first relevant hit, while **relevant-chunk movement** tracks every labelled passage. A multi-evidence query can therefore improve in MRR while one of its other required chunks regresses. If no natural regression occurs in one environment/model revision, the analysis still reports zero honestly and includes a clearly marked **TEST-ONLY FAILURE INJECTION** to exercise the detector—not a fabricated aggregate improvement.

---

## 13. Local latency, not universal latency

The notebook measures first-stage, reranker, and total two-stage duration per query and reports median and p95. These values describe only that run. Latency depends on model size, candidate count, sequence length, CPU/GPU, batching, model warm-up, and serving architecture. Even after explicit model warm-up, notebook/runtime caching and backend initialization can influence the measurements.

Use the measurements to compare configurations within the same environment. Do not copy them into a universal service-level objective.

---

## 14. Late interaction and advanced alternatives

ColBERT-style late interaction retains token-level representations and performs fine-grained matching. Depending on the index and serving design, a late-interaction model can be used for first-stage retrieval, as a later ranking stage, or in a multi-stage cascade. It is not inherently or always a second-stage reranker.

HyDE, query decomposition, multi-query expansion, hybrid retrieval, learned sparse retrieval, ColBERT implementation, fine-tuning, and calibrated fusion are deliberately deferred. They change candidate generation, model training, or system architecture beyond this focused experiment.

---

## 15. Exercises

1. Add a hard negative to one query slice and measure per-query plus aggregate rank movement.
2. Replace one relevance label with a graded relevance value and extend nDCG transparently.
3. Compare `candidate_k` budgets under a latency objective without declaring one universal optimum.
4. Add a source-diversity rule after reranking and measure multi-evidence completeness.
5. Run the models on CPU and GPU, if available, and explain why the timings are environment-specific.
6. Design answerable/unanswerable validation data for a score threshold; do not choose a threshold by inspection.
7. Replace the teaching reranker with a domain-specific model and test whether regressions move between slices.

---

## 16. Checkpoint

1. Why is first-stage retrieval optimized differently from reranking?
2. Why is a cross-encoder slower than a bi-encoder?
3. What happens if the correct evidence is outside the candidate set?
4. Why must authorization happen before reranking?
5. Why should a cross-encoder logit not be treated as truth confidence?
6. Which metric shows whether reranking moved relevant evidence earlier?
7. When should you use query transformation instead?
8. Why are first-stage distance and reranker score not directly comparable?
9. What does `top_n` change that `candidate_k` does not?
10. Why can the highest reranker score still correspond to an unanswerable query?

---

## What comes next

### [Intermediate 04 — Evaluation](../04-evaluation/README.md)

Measure retrieval and answer behavior separately and build release gates.

---

## References

- Nogueira & Cho — [Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085)
- Sentence Transformers — [Cross-Encoder documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- Sentence Transformers — [Pretrained MS MARCO cross-encoders](https://sbert.net/docs/cross_encoder/pretrained_models.html)
- LangChain — [Retriever integrations](https://docs.langchain.com/oss/python/integrations/retrievers)
- LangChain — [Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma)
- Thakur et al. — [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663)
- Khattab & Zaharia — [ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT](https://arxiv.org/abs/2004.12832)
- Santhanam et al. — [ColBERTv2](https://aclanthology.org/2022.naacl-main.272/)

---

## Key takeaway

**A reranker improves ordering of retrieved candidates. It cannot recover evidence that never entered the candidate set.**
