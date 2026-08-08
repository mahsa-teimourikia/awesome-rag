from __future__ import annotations

def recall_at_k(ranked_ids: list[str], relevant_ids: list[str], k: int = 5) -> float:
    top = ranked_ids[:k]
    return len(set(top) & set(relevant_ids)) / max(len(set(relevant_ids)), 1)

def precision_at_k(ranked_ids: list[str], relevant_ids: list[str], k: int = 5) -> float:
    top = ranked_ids[:k]
    return len(set(top) & set(relevant_ids)) / max(len(top), 1)

def mrr(ranked_ids: list[str], relevant_ids: list[str]) -> float:
    rel = set(relevant_ids)
    for i, rid in enumerate(ranked_ids, start=1):
        if rid in rel or any(rid.startswith(r + "#") for r in rel):
            return 1 / i
    return 0.0

def evaluate_case(ranked_chunk_ids: list[str], relevant_doc_ids: list[str]) -> dict:
    mapped = [rid.split('#')[0] for rid in ranked_chunk_ids]
    return {"recall@5": recall_at_k(mapped, relevant_doc_ids, 5), "precision@5": precision_at_k(mapped, relevant_doc_ids, 5), "mrr": mrr(mapped, relevant_doc_ids)}

def cost_per_successful_task(total_cost: float, successes: int) -> float:
    return round(total_cost / max(successes, 1), 4)
