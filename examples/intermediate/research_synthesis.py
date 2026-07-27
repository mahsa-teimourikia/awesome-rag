"""Multi-query retrieval and claim-level evidence grouping."""

from __future__ import annotations

from dataclasses import dataclass

from .retrieval_strategies import BM25, Document


@dataclass(frozen=True)
class Claim:
    text: str
    source_ids: tuple[str, ...]


def research_queries(question: str) -> list[str]:
    question = " ".join(question.split())
    return [question, f"evidence and findings about {question}", f"limitations and counterarguments for {question}"]


def retrieve_unique(question: str, documents: list[Document], top_k: int = 3) -> list[Document]:
    unique: dict[str, Document] = {}
    index = BM25(documents)
    for query in research_queries(question):
        for document, _ in index.search(query, top_k=top_k):
            unique[document.doc_id] = document
    return list(unique.values())


def make_claims(question: str, documents: list[Document]) -> list[Claim]:
    evidence = retrieve_unique(question, documents)
    return [Claim(document.text, (document.doc_id,)) for document in evidence]
