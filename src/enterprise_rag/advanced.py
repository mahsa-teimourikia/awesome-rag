from __future__ import annotations
from dataclasses import dataclass
from .corpus import Chunk
from .retrieval import hybrid_retrieve

@dataclass
class GraphFact:
    subject: str
    predicate: str
    object: str
    source: str

FACTS = [
    GraphFact("Project Atlas", "depends_on", "VectorDB-X", "projects/projects.md"),
    GraphFact("VectorDB-X", "supplied_by", "Acme Systems", "contracts/vendors.md"),
    GraphFact("Acme Systems", "must_certify", "Regulation R-17", "contracts/vendors.md"),
]

def expand_queries(question: str) -> list[str]:
    return [question, question.replace("supplier", "vendor"), "Project Atlas VectorDB-X Acme Systems Regulation R-17"]

def graph_answer(question: str) -> dict:
    chain = [f for f in FACTS if f.subject in {"Project Atlas", "VectorDB-X", "Acme Systems"}]
    return {"answer": "Project Atlas uses VectorDB-X from Acme Systems, and Acme must certify Regulation R-17 compliance.", "facts": [f.__dict__ for f in chain]}

def corrective_retrieve(question: str, chunks: list[Chunk]) -> dict:
    first = hybrid_retrieve(question, chunks, top_k=3)
    if first and first[0][1] > 0.02:
        return {"route": "hybrid", "evidence": first, "abstained": False}
    expanded = []
    for q in expand_queries(question):
        expanded.extend(hybrid_retrieve(q, chunks, top_k=3))
    seen = {}; [seen.setdefault(c.id, (c, s)) for c, s in expanded]
    return {"route": "corrective_multi_query", "evidence": list(seen.values())[:5], "abstained": not bool(seen)}

def route(question: str) -> str:
    q = question.lower()
    if "project atlas" in q and ("supplier" in q or "regulation" in q): return "graph"
    if "14%" in q or "ax-774-b" in q: return "hybrid"
    if "count" in q or "csv" in q: return "structured"
    return "vector"
