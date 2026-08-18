# Intermediate 06 — Local Qdrant: Collections, Payload Filters, and Versioned Vector Operations

**Level:** Intermediate  
**Estimated time:** 2–3 hours  
**Notebook:** [`06_qdrant_local.ipynb`](06_qdrant_local.ipynb)  
**Prerequisites:** Metadata & Permissions; Retrieval; Evaluation

---

## Why this lesson exists

Earlier courses used Chroma to keep vector retrieval simple.

This notebook introduces Qdrant using:

```python
QdrantClient(":memory:")
```

and the maintained LangChain integration:

```python
from langchain_qdrant import QdrantVectorStore
```

The lab focuses on:

- local in-memory Qdrant;
- payload metadata;
- tenant filtering;
- document updates and stale-vector risk.

![Qdrant architecture](assets/qdrant-architecture.svg)

The old README described Docker, `lab.py`, payload-index creation, caching, migrations, performance tuning, and several production procedures as though they were runnable in the course. They are useful extensions, but the actual notebook is intentionally smaller.

---

## Learning objectives

After this lesson you should be able to:

- explain what a Qdrant collection stores;
- distinguish vector representation from payload metadata;
- use payload filters during search;
- understand why stable point IDs matter;
- explain the stale-vector problem when documents are updated;
- design version metadata for indexed chunks;
- distinguish in-memory lab mode from production deployment;
- understand where hybrid search and payload indexes fit; and
- define a safe reindex/update lifecycle.

---

# 1. Collection anatomy

A vector collection contains:

```text
point ID
vector(s)
payload metadata
```

For RAG, payload commonly carries:

```text
source
chunk_id
tenant
version
document_type
validity
```

![Point anatomy](assets/point-anatomy.svg)

The vector is used for similarity search.

The payload supports filtering, provenance, lifecycle, and application logic.

---

# 2. In-memory lab mode

The notebook runs Qdrant in memory and does not require Docker.

That makes the lesson reproducible and credential-free.

Do not confuse:

```python
QdrantClient(":memory:")
```

with a production deployment.

Production adds:

- persistent storage;
- authentication;
- TLS/network controls;
- backups/snapshots;
- replication/capacity planning;
- monitoring.

---

# 3. Payload filtering

The notebook creates a native Qdrant filter:

```python
Filter(
    must=[
        FieldCondition(
            key="metadata.tenant",
            match=MatchValue(value="acme")
        )
    ]
)
```

and passes it to:

```python
similarity_search(..., filter=acme_filter)
```

This correctly demonstrates that tenant constraints belong in the vector query rather than after generation.

---

# 4. Qdrant + LangChain metadata shape

When using `QdrantVectorStore.from_documents`, LangChain stores document metadata in payload structure managed by the integration.

The notebook filters on:

```text
metadata.tenant
```

because the metadata is nested by the integration.

When using the Qdrant client directly, payload schemas may be flatter.

Do not copy a field path without verifying the actual payload structure in your integration.

---

# 5. Stable point IDs

The notebook intentionally demonstrates a bad update:

```text
old Acme gateway document remains
new V2 document is added
```

Now the index contains contradictory evidence.

![Update lifecycle](assets/update-lifecycle.svg)

Production ingestion should know which points belong to each source document.

Use stable IDs or a source→point mapping so an update can:

1. identify old chunks;
2. delete/tombstone them;
3. insert new chunks;
4. verify the new version;
5. invalidate caches.

---

# 6. Version metadata

Useful fields:

```text
document_id
chunk_id
document_version
source_checksum
embedding_model
chunking_version
indexed_at
valid_from
valid_to
```

A vector index is not only vectors.

It is a versioned representation of a specific corpus under a specific chunking and embedding configuration.

---

# 7. Collection versioning

If you change:

- embedding model;
- vector dimensions;
- distance metric;
- major chunking strategy;

prefer a new collection or named-vector migration rather than silently mixing incompatible representations.

A safe model migration is:

```text
build new index
   ↓
evaluate in shadow
   ↓
canary
   ↓
promote
   ↓
retain rollback window
```

---

# 8. Hybrid retrieval

Current Qdrant supports dense and sparse query representations with server-side fusion such as Reciprocal Rank Fusion.

That is an extension to this notebook, not something the current lab implements.

Use it when the evaluation data from Intermediate 01 shows that dense-only retrieval misses exact lexical evidence.

---

# 9. Payload indexes

At scale, fields used frequently in filters should be indexed appropriately.

Examples:

```text
tenant
classification
document_type
date
```

Payload indexing is an operational performance concern.

The teaching notebook's two documents do not require it.

---

# 10. Deletion semantics

Deleting a source document means deleting or revoking **all chunks derived from it**.

If one PDF produced 50 points, removing only one point is incomplete.

Maintain:

```text
source_document_id → point IDs
```

or use payload-based deletion with a stable source identifier.

---

# 11. Security

Never expose an unauthenticated local Qdrant server to an untrusted network.

For production:

- authenticate;
- encrypt transport;
- restrict network access;
- isolate tenants appropriately;
- validate filter construction from caller identity;
- avoid putting secrets in payloads merely for convenience.

---

# 12. Evaluation

After moving to a vector database, rerun retrieval evaluation.

Infrastructure migration can change:

- filtering behavior;
- similarity semantics;
- ANN recall;
- latency;
- ordering.

Measure, do not assume parity.

---

# 13. Exercises

1. Add Acme and Globex documents with identical text; prove tenant isolation.
2. Add stable point IDs.
3. Update a source and remove the old vectors before inserting V2.
4. Add version metadata and show both historical and current filtering.
5. Inspect actual Qdrant payload structure.
6. Design a blue/green collection migration for a new embedding model.
7. Compare dense-only retrieval with Qdrant hybrid search as an extension.

---

# 14. Checkpoint

1. What is the difference between vector data and payload metadata?
2. Why do stable point IDs matter?
3. Why is adding V2 without deleting V1 unsafe?
4. Why should tenant filtering happen inside search?
5. What changes require a reindex or collection migration?
6. What is different about in-memory Qdrant vs production?
7. Why must evaluation be rerun after infrastructure changes?

---

## References

- Qdrant — [Documentation](https://qdrant.tech/documentation/)
- Qdrant — [Filtering](https://qdrant.tech/documentation/concepts/filtering/)
- Qdrant — [Hybrid search](https://qdrant.tech/documentation/search/text-search/hybrid-search/)
- Qdrant — [Hybrid queries / RRF](https://qdrant.tech/documentation/search/hybrid-queries/)
- LangChain — [Qdrant integration](https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant)

---

## Key takeaway

**A vector database is part of your retrieval contract. Manage vectors, payloads, IDs, filters, and versions as production data—not as disposable embeddings.**
