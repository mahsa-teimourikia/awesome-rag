# 06 — Local Qdrant and embeddings

**Level:** Intermediate  \
**Time:** 60 minutes  \
**Prerequisites:** [retrieval evaluation](../04-evaluation/README.md)

## Outcome

Replace the dependency-free retrieval baseline with local Sentence Transformers embeddings and Qdrant vector search, while keeping payload metadata and tenant filters.

## Setup

```bash
pip install -e '.[qdrant]'
docker compose up -d qdrant
```

Open [`qdrant_local.ipynb`](qdrant_local.ipynb). The reusable functions are [`lab.py`](lab.py).

The example is optional: the conceptual and dependency-free labs remain runnable without Docker or a model download.
