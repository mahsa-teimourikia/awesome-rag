"""Tiny entity graph retriever for relationship-heavy questions."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Fact:
    fact_id: str
    subject: str
    relation: str
    object: str
    source: str


class EntityGraph:
    def __init__(self, facts: list[Fact]):
        self.facts = facts
        self.by_entity: dict[str, list[Fact]] = defaultdict(list)
        for fact in facts:
            self.by_entity[fact.subject.lower()].append(fact)
            self.by_entity[fact.object.lower()].append(fact)

    def entities_in(self, query: str) -> set[str]:
        words = set(re.findall(r"[a-z0-9-]+", query.lower()))
        return {entity for entity in self.by_entity if entity in words}

    def neighborhood(self, query: str, hops: int = 1) -> list[Fact]:
        frontier = deque((entity, 0) for entity in self.entities_in(query))
        visited = set()
        selected: dict[str, Fact] = {}
        while frontier:
            entity, depth = frontier.popleft()
            if entity in visited or depth > hops:
                continue
            visited.add(entity)
            for fact in self.by_entity.get(entity, []):
                selected[fact.fact_id] = fact
                if depth < hops:
                    frontier.append((fact.subject.lower(), depth + 1))
                    frontier.append((fact.object.lower(), depth + 1))
        return list(selected.values())
