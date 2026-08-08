from __future__ import annotations
from .corpus import Chunk

def naive_answer(question: str) -> str:
    if "14%" in question or "increased" in question.lower():
        return "European enterprise revenue increased by 14%."
    return "I can answer from general knowledge, but I have no citations."

def answer_with_citations(question: str, evidence: list[tuple[Chunk, float]], min_score: float = 0.01) -> dict:
    if not evidence or evidence[0][1] < min_score:
        return {"answer": "I do not have enough retrieved evidence to answer.", "citations": [], "supported": False}
    cited = []
    text = " ".join(c.text for c, _ in evidence[:3])
    if "14%" in text:
        answer = "European enterprise revenue increased by 14% quarter over quarter in Q2 2025."
    elif "AX-774-B" in text:
        answer = "AX-774-B means a payment authorization timeout in the EU checkout region."
    elif "Acme Systems" in text and "Regulation R-17" in text:
        answer = "Project Atlas depends on VectorDB-X, supplied by Acme Systems; clause 7 requires Regulation R-17 certification."
    else:
        answer = "The retrieved evidence is relevant, but a human should inspect it before forming a final answer."
    for chunk, score in evidence[:3]:
        cited.append({"chunk_id": chunk.id, "source": chunk.document_id, "score": round(score, 4)})
    return {"answer": answer, "citations": cited, "supported": True}
