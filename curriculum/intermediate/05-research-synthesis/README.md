# 05 — Research synthesis

**Level:** Intermediate  \
**Time:** 60 minutes  \
**Prerequisites:** [the evaluation lab](../04-evaluation/README.md)

## Outcome

Use multiple focused queries, deduplicate evidence, and preserve claim-level citations for a research-style answer.

## Guided notebook

Open [`research_synthesis.ipynb`](research_synthesis.ipynb). The reusable implementation is [`lab.py`](lab.py).

```mermaid
flowchart LR
  Q[Research question] --> M[Multiple focused queries]
  M --> R[Retrieve each query]
  R --> D[Deduplicate sources]
  D --> C[Claims with source IDs]
  C --> S[Synthesis with citations]
```

One query often overfits to the first framing of a question. Evidence, findings, limitations, and counterarguments should be retrieved separately. Deduplication prevents repeated copies of the same source from dominating the context.

## Exercise

Add two documents supporting a claim and one document presenting a limitation. Extend `Claim` to carry confidence and a claim type such as `finding`, `limitation`, or `open-question`.
