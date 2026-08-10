# 03 — Query rewriting and reranking

**Level:** Intermediate  \
**Time:** 45 minutes  \
**Prerequisites:** [metadata permissions](../02-metadata-permissions/README.md)

## Outcome

Improve difficult queries by retrieving candidates from multiple focused variants, then applying a second-stage ranker that uses the original question.

## Guided notebook

Open [`query_reranking.ipynb`](query_reranking.ipynb). The reusable implementation is [`lab.py`](lab.py).

```mermaid
flowchart LR
  Q[Original query] --> W[Rewrite and expand]
  W --> R[First-stage retrieval]
  R --> U[Union candidates]
  U --> X[Second-stage reranker]
  X --> K[Top-k context]
```

Rewriting can improve recall but may introduce irrelevant candidates and cost. Reranking is more expensive than first-stage retrieval, so use it on a bounded candidate set. A production reranker may be a cross-encoder or late-interaction model; validate its input length, latency, and score calibration.

## Exercise

Add a paraphrase that the original query misses. Compare recall before and after rewriting, then measure whether reranking improves the first relevant document’s position.
