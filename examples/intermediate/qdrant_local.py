"""Optional local Qdrant + Sentence Transformers retrieval example.

Install with `pip install -e '.[qdrant]'` and run Qdrant via Docker Compose.
The functions are kept small so the notebook can explain each boundary.
"""

from __future__ import annotations

from typing import Iterable


def index_documents(client, collection_name: str, documents: Iterable[dict], encoder, vector_size: int) -> None:
    from qdrant_client.models import Distance, PointStruct, VectorParams

    if not client.collection_exists(collection_name):
        client.create_collection(collection_name, vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE))
    points = [PointStruct(id=doc["id"], vector=encoder.encode(doc["text"]).tolist(), payload={"text": doc["text"], "source": doc["source"], **doc.get("metadata", {})}) for doc in documents]
    client.upsert(collection_name, points=points)


def search(client, collection_name: str, query: str, encoder, limit: int = 3, tenant_id: str | None = None):
    query_filter = None
    if tenant_id:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        query_filter = Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])
    return client.search(collection_name, query_vector=encoder.encode(query).tolist(), query_filter=query_filter, limit=limit)
