"""Inspectable GraphRAG primitives with bounded traversal and provenance.

This intentionally avoids a graph database and model calls so each learner can
inspect entity matching, authorization, traversal, and evidence construction.
Replace the storage/retrieval adapter in production, not these controls.
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable


TOKEN = re.compile(r"[a-z0-9-]+")


@dataclass(frozen=True)
class Fact:
    fact_id: str
    subject: str
    relation: str
    object: str
    source: str
    tenant: str = "northstar"
    confidence: float = 1.0
    revision: str = "v1"


@dataclass(frozen=True)
class GraphPolicy:
    max_hops: int = 2
    max_facts: int = 12
    permitted_tenants: frozenset[str] = frozenset({"northstar"})
    min_confidence: float = 0.7


@dataclass(frozen=True)
class GraphEvidence:
    facts: tuple[Fact, ...]
    seed_entities: tuple[str, ...]
    hops: int
    truncated: bool
    reason: str

    def citations(self) -> list[dict[str, str]]:
        return [
            {"fact_id": fact.fact_id, "source": fact.source, "revision": fact.revision}
            for fact in self.facts
        ]


def _normalize(value: str) -> str:
    return " ".join(TOKEN.findall(value.lower()))


class EntityGraph:
    def __init__(self, facts: list[Fact]):
        self.facts = facts
        self.by_entity: dict[str, list[Fact]] = defaultdict(list)
        for fact in facts:
            self.by_entity[_normalize(fact.subject)].append(fact)
            self.by_entity[_normalize(fact.object)].append(fact)

    def entities_in(self, query: str) -> set[str]:
        """Exact normalized entity matching; log ambiguity in real entity resolution."""
        normalized = _normalize(query)
        return {entity for entity in self.by_entity if re.search(rf"\b{re.escape(entity)}\b", normalized)}

    def _authorized(self, fact: Fact, policy: GraphPolicy) -> bool:
        return fact.tenant in policy.permitted_tenants and fact.confidence >= policy.min_confidence

    def neighborhood(self, query: str, hops: int = 1) -> list[Fact]:
        """Backwards-compatible unfiltered local neighborhood for early exercises."""
        return list(self.retrieve(query, GraphPolicy(max_hops=hops, min_confidence=0.0, permitted_tenants=frozenset({f.tenant for f in self.facts}))).facts)

    def retrieve(self, query: str, policy: GraphPolicy = GraphPolicy()) -> GraphEvidence:
        seeds = tuple(sorted(self.entities_in(query)))
        if not seeds:
            return GraphEvidence((), (), 0, False, "no-resolved-entity")
        frontier = deque((entity, 0) for entity in seeds)
        visited: set[str] = set()
        selected: dict[str, Fact] = {}
        truncated = False
        while frontier:
            entity, depth = frontier.popleft()
            if entity in visited or depth > policy.max_hops:
                continue
            visited.add(entity)
            for fact in self.by_entity.get(entity, []):
                if not self._authorized(fact, policy):
                    continue
                selected.setdefault(fact.fact_id, fact)
                if len(selected) >= policy.max_facts:
                    truncated = bool(frontier)
                    break
                if depth < policy.max_hops:
                    frontier.append((_normalize(fact.subject), depth + 1))
                    frontier.append((_normalize(fact.object), depth + 1))
            if len(selected) >= policy.max_facts:
                break
        facts = tuple(sorted(selected.values(), key=lambda fact: fact.fact_id))
        return GraphEvidence(facts, seeds, policy.max_hops, truncated, "bounded-authorized-neighborhood" if facts else "no-authorized-facts")

    def paths(self, start: str, end: str, policy: GraphPolicy = GraphPolicy()) -> list[tuple[Fact, ...]]:
        """Return simple, authorized paths up to max_hops for relationship answers."""
        start, end = _normalize(start), _normalize(end)
        queue = deque([(start, (), {start})])
        paths: list[tuple[Fact, ...]] = []
        while queue:
            entity, path, seen = queue.popleft()
            if len(path) >= policy.max_hops:
                continue
            for fact in self.by_entity.get(entity, []):
                if not self._authorized(fact, policy):
                    continue
                next_entity = _normalize(fact.object if _normalize(fact.subject) == entity else fact.subject)
                next_path = path + (fact,)
                if next_entity == end:
                    paths.append(next_path)
                elif next_entity not in seen:
                    queue.append((next_entity, next_path, seen | {next_entity}))
        return paths


def linearize(evidence: GraphEvidence) -> str:
    """Create model context with fact-level provenance, not anonymous triples."""
    return "\n".join(
        f"[{fact.fact_id} | {fact.source}@{fact.revision}] {fact.subject} --{fact.relation}--> {fact.object}"
        for fact in evidence.facts
    )
