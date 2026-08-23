from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.generation import RAGDecision, create_llm

def calculate_recall_at_k(retrieved_candidates: list, expected_doc_ids: list) -> float:
    """
    A simple metric: Did any chunk from the expected documents appear in the retrieved candidates?
    Returns 1.0 if any expected document is present, 0.0 otherwise.
    """
    if not expected_doc_ids:
        return 1.0  # Unanswerable queries: Recall is conceptually 1.0 since nothing is expected
        
    retrieved_doc_ids = [doc.metadata.get("document_id") for doc in retrieved_candidates]
    
    for exp_id in expected_doc_ids:
        exp_basename = exp_id.split("/")[-1].replace(".md", "")
        if exp_basename in retrieved_doc_ids:
            return 1.0
            
    return 0.0

def calculate_mrr(retrieved_candidates: list, expected_doc_ids: list) -> float:
    """
    Mean Reciprocal Rank (MRR): 1 / (rank of first relevant document).
    Measures Context Precision.
    """
    if not expected_doc_ids:
        return 1.0  # N/A for unanswerable
        
    for i, candidate in enumerate(retrieved_candidates):
        candidate_doc_id = candidate.metadata.get("document_id")
        for exp_id in expected_doc_ids:
            exp_basename = exp_id.split("/")[-1].replace(".md", "")
            if candidate_doc_id and exp_basename in candidate_doc_id:
                return 1.0 / (i + 1)
                
    return 0.0

def evaluate_abstention(decision: str, is_answerable: bool) -> str:
    """
    Classifies abstention accuracy.
    """
    if decision == "answer" and is_answerable:
        return "True Answer"
    elif decision in ["insufficient_evidence", "conflicting_evidence"] and not is_answerable:
        return "True Abstention"
    elif decision in ["insufficient_evidence", "conflicting_evidence"] and is_answerable:
        return "False Abstention"
    elif decision == "answer" and not is_answerable:
        return "Unsafe Answer"
    return "Unknown"

class CorrectnessResult(BaseModel):
    is_correct: bool = Field(description="True if the generated answer matches the expected answer semantically.")
    reasoning: str = Field(description="Explanation of the decision.")

def evaluate_correctness(generated_answer: str, expected_answer: str) -> bool:
    """Uses an LLM to judge semantic correctness."""
    if not expected_answer or not generated_answer:
        return False
        
    llm = create_llm().with_structured_output(CorrectnessResult)
    prompt = ChatPromptTemplate.from_template(
        "You are an evaluator. Compare the generated answer to the expected ground-truth answer.\n"
        "Are they semantically equivalent? Ignore minor formatting differences.\n\n"
        "Generated Answer: {generated}\n\n"
        "Expected Answer: {expected}"
    )
    
    result = (prompt | llm).invoke({"generated": generated_answer, "expected": expected_answer})
    return result.is_correct

class GroundednessResult(BaseModel):
    is_grounded: bool = Field(description="True if ALL claims in the generated answer are fully supported by the provided evidence.")
    reasoning: str = Field(description="Explanation of what claim is unsupported, if any.")

def evaluate_groundedness(generated_answer: str, citations: list, evidence_map: dict) -> bool:
    """Uses an LLM to verify if the answer is strictly grounded in the cited evidence."""
    if not citations or not generated_answer:
        return False
        
    # Build cited context
    cited_context = ""
    for cid in set(citations):
        if cid in evidence_map:
            cited_context += f"Evidence [{cid}]: {evidence_map[cid].page_content}\n\n"
            
    llm = create_llm().with_structured_output(GroundednessResult)
    prompt = ChatPromptTemplate.from_template(
        "You are an evaluator checking for hallucinations.\n"
        "Look at the generated answer and the provided cited evidence.\n"
        "Is EVERY claim in the generated answer completely supported by the cited evidence?\n\n"
        "Cited Evidence:\n{context}\n\n"
        "Generated Answer: {generated}"
    )
    
    result = (prompt | llm).invoke({"context": cited_context, "generated": generated_answer})
    return result.is_grounded
