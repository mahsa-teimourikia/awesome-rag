# 04 — Retrieval evaluation lab

**Level:** Intermediate  \
**Time:** 45 minutes  \
**Prerequisites:** [query rewriting and reranking](../03-query-reranking/README.md)

## Outcome

Create a small golden dataset, calculate retrieval metrics, and use thresholds to detect regressions when a retriever changes.

## Guided notebook

Open [`evaluation.ipynb`](evaluation.ipynb). The reusable metric functions are [`evaluation.py`](../../../examples/intermediate/evaluation.py).

```mermaid
flowchart LR
  G[Golden queries + relevant IDs] --> R[Run retriever]
  R --> M[Recall@k, precision@k, MRR]
  M --> C{Regression gate}
  C -->|pass| S[Ship experiment]
  C -->|fail| D[Inspect retrieved evidence]
```

Retrieval metrics do not prove answer faithfulness. They answer a narrower question: did the retriever return labeled relevant evidence? Pair them with groundedness, citation coverage, latency, cost, and security tests.

## Exercise

Add a no-answer query, a permission-boundary query, and a paraphrase. Set a minimum recall and MRR threshold, then make a deliberately bad ranking fail the gate.
