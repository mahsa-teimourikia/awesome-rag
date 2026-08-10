from examples.advanced.graph_rag import EntityGraph, Fact, GraphPolicy


FACTS = [Fact("f1", "Acme", "owns", "Atlas", "one.md"), Fact("f2", "Atlas", "uses", "Qdrant", "two.md"), Fact("f3", "Qdrant", "supports", "hybrid", "three.md")]


def test_entity_neighborhood_traverses_bounded_hops():
    graph = EntityGraph(FACTS)
    assert {fact.fact_id for fact in graph.neighborhood("How does Acme use hybrid?", hops=2)} == {"f1", "f2", "f3"}


def test_unknown_entity_has_no_evidence():
    assert EntityGraph(FACTS).neighborhood("What does Contoso own?") == []


def test_one_hop_does_not_return_unbounded_graph():
    result = EntityGraph(FACTS).neighborhood("Acme", hops=1)
    assert {fact.fact_id for fact in result} == {"f1", "f2"}


def test_policy_filters_other_tenant_facts_before_traversal():
    graph = EntityGraph(FACTS + [Fact("private", "Atlas", "owned_by", "Secret Team", "private.md", tenant="other")])
    result = graph.retrieve("Atlas", GraphPolicy(permitted_tenants=frozenset({"northstar"})))
    assert "private" not in {fact.fact_id for fact in result.facts}


def test_path_is_bounded_and_citable():
    graph = EntityGraph(FACTS)
    paths = graph.paths("Acme", "hybrid", GraphPolicy(max_hops=3))
    assert [[fact.fact_id for fact in path] for path in paths] == [["f1", "f2", "f3"]]
