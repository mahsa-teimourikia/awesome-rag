import pytest

from examples.intermediate.qdrant_local import collection_contract, payload_filter, validate_document


def test_payload_contract_requires_provenance_and_tenant():
    document = {
        "id": "runbook-1",
        "text": "Investigate checkout latency.",
        "source": "runbooks/checkout.md",
        "metadata": {"tenant_id": "acme", "chunk_id": "runbook-1#0", "source_version": "2026.8", "tags": ["support"]},
    }
    assert validate_document(document)["payload"]["tenant_id"] == "acme"
    with pytest.raises(ValueError):
        validate_document({"id": "missing", "text": "no metadata", "source": "x"})


def test_filter_is_tenant_scoped_and_contract_is_explicit():
    assert payload_filter("acme", required_tags={"support"}) == {
        "must": [
            {"key": "tenant_id", "match": {"value": "acme"}},
            {"key": "tags", "match": {"value": "support"}},
        ]
    }
    assert collection_contract(384)["payload_indexes"]["tenant_id"] == "keyword"
