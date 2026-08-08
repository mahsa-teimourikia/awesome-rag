from __future__ import annotations

from collections import Counter, defaultdict
import math
import re
from .corpus import Chunk

SYNONYMS = {
    "rose": "increased", "growth": "increased", "quarter": "q", "parental": "parent", "leave": "policy",
    "vendor": "supplies", "supplier": "supplies", "eu": "european", "europe": "european", "auth": "authorization",
}

def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return [SYNONYMS.get(t, t) for t in tokens]

def bm25_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    q = tokenize(query)
    docs = [tokenize(c.text) for c in chunks]
    df = Counter(t for doc in docs for t in set(doc))
    avgdl = sum(len(d) for d in docs) / max(len(docs), 1)
    scores = {}
    for chunk, terms in zip(chunks, docs):
        counts = Counter(terms); score = 0.0
        for t in q:
            if not df[t]: continue
            idf = math.log(1 + (len(docs) - df[t] + .5) / (df[t] + .5))
            score += idf * (counts[t] * 2.2) / (counts[t] + 1.2 * (1 - .75 + .75 * len(terms) / max(avgdl, 1)))
        scores[chunk.id] = score
    return scores

def semantic_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    q = set(tokenize(query))
    scores = {}
    for c in chunks:
        t = set(tokenize(c.text + " " + c.metadata.get("section", "")))
        overlap = len(q & t) / max(len(q | t), 1)
        scores[c.id] = overlap
    return scores

def _rank(scores: dict[str, float], chunks: list[Chunk], top_k: int) -> list[tuple[Chunk, float]]:
    by_id = {c.id: c for c in chunks}
    return [(by_id[cid], score) for cid, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k] if score > 0]

def retrieve(query: str, chunks: list[Chunk], method: str = "bm25", top_k: int = 5) -> list[tuple[Chunk, float]]:
    scores = semantic_scores(query, chunks) if method == "dense" else bm25_scores(query, chunks)
    return _rank(scores, chunks, top_k)

def reciprocal_rank_fusion(rankings: list[list[tuple[Chunk, float]]], k: int = 60) -> dict[str, float]:
    fused = defaultdict(float)
    for ranking in rankings:
        for rank, (chunk, _) in enumerate(ranking, start=1):
            fused[chunk.id] += 1 / (k + rank)
    return dict(fused)

def hybrid_retrieve(query: str, chunks: list[Chunk], top_k: int = 5) -> list[tuple[Chunk, float]]:
    bm25 = retrieve(query, chunks, "bm25", top_k=20)
    dense = retrieve(query, chunks, "dense", top_k=20)
    fused = reciprocal_rank_fusion([bm25, dense])
    return _rank(fused, chunks, top_k)
