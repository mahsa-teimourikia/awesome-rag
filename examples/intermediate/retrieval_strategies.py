"""Inspectable lexical, dense-adapter, and hybrid retrieval strategies."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str


def terms(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class BM25:
    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1, self.b = k1, b
        self.term_frequencies = [Counter(terms(doc.text)) for doc in documents]
        self.lengths = [sum(freq.values()) for freq in self.term_frequencies]
        self.average_length = sum(self.lengths) / max(len(self.lengths), 1)
        self.document_frequency = Counter(term for freq in self.term_frequencies for term in freq)

    def search(self, query: str, top_k: int = 3) -> list[tuple[Document, float]]:
        query_terms = set(terms(query))
        scored = []
        count = len(self.documents)
        for doc, frequencies, length in zip(self.documents, self.term_frequencies, self.lengths):
            score = 0.0
            for term in query_terms:
                if term not in frequencies:
                    continue
                df = self.document_frequency[term]
                idf = math.log(1 + (count - df + 0.5) / (df + 0.5))
                tf = frequencies[term]
                norm = tf + self.k1 * (1 - self.b + self.b * length / max(self.average_length, 1))
                score += idf * (tf * (self.k1 + 1) / norm)
            if score:
                scored.append((doc, score))
        return sorted(scored, key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]


def reciprocal_rank_fusion(*rankings: list[Document], k: int = 60, top_k: int = 3) -> list[tuple[Document, float]]:
    scores: dict[str, tuple[Document, float]] = {}
    for ranking in rankings:
        for rank, document in enumerate(ranking, start=1):
            current = scores.get(document.doc_id, (document, 0.0))
            scores[document.doc_id] = (document, current[1] + 1 / (k + rank))
    return sorted(scores.values(), key=lambda pair: (-pair[1], pair[0].doc_id))[:top_k]
