"""Optional Qdrant + Sentence Transformers adapter with safe payload contracts.

The pure helpers are used by tests and the notebook without Docker.  Qdrant is
imported only inside adapter functions so local course material stays runnable.
"""

from __future__ import annotations

from typing import Iterable


REQUIRED_PAYLOAD = frozenset({"text", "source", "tenant_id", "chunk_id", "source_version"})


def validate_document(document: dict) -> dict:
    """Fail closed when provenance or tenant metadata is missing."""

    payload = {"text": document.get("text"), "source": document.get("source"), **document.get("metadata", {})}
    missing = REQUIRED_PAYLOAD - payload.keys()
    if missing or not document.get("id"):
        raise ValueError(f"document is missing required fields: {sorted(missing | ({'id'} if not document.get('id') else set()))}")
    return {"id": document["id"], "payload": payload}


def payload_filter(tenant_id: str, *, required_tags: set[str] | None = None) -> dict:
    """Describe the server-side filter; callers derive tenant from verified identity."""

    conditions = [{"key": "tenant_id", "match": {"value": tenant_id}}]
    for tag in sorted(required_tags or set()):
        conditions.append({"key": "tags", "match": {"value": tag}})
    return {"must": conditions}


def collection_contract(vector_size: int) -> dict:
    """Return the reviewable collection and payload-index contract."""

    if vector_size <= 0:
        raise ValueError("vector_size must be positive")
    return {
        "vectors": {"size": vector_size, "distance": "cosine"},
        "payload_indexes": {"tenant_id": "keyword", "tags": "keyword", "source_version": "keyword"},
    }


def index_documents(client, collection_name: str, documents: Iterable[dict], encoder, vector_size: int) -> None:
    from qdrant_client.models import Distance, PointStruct, VectorParams

    contract = collection_contract(vector_size)
    if not client.collection_exists(collection_name):
        client.create_collection(collection_name, vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE))
        # Index high-cardinality filter fields before production-scale ingestion.
        for field_name in contract["payload_indexes"]:
            client.create_payload_index(collection_name, field_name, field_schema="keyword")
    points = []
    for raw in documents:
        validated = validate_document(raw)
        points.append(PointStruct(id=validated["id"], vector=encoder.encode(validated["payload"]["text"]).tolist(), payload=validated["payload"]))
    client.upsert(collection_name, points=points, wait=True)


def search(client, collection_name: str, query: str, encoder, limit: int = 3, tenant_id: str | None = None):
    if not tenant_id:
        raise ValueError("tenant_id must come from verified identity")
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    query_filter = Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])
    return client.query_points(collection_name, query=encoder.encode(query).tolist(), query_filter=query_filter, with_payload=True, limit=limit).points
