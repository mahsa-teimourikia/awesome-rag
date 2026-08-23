from src.generation import RAGDecision

def validate_decision(decision: RAGDecision, evidence_map: dict) -> list[str]:
    """Deterministic validation of the RAG decision and citations."""
    errors = []
    
    if decision.decision == "answer":
        if not decision.answer:
            errors.append("Decision is 'answer' but no answer text was provided.")
        if not decision.citations:
            errors.append("Decision is 'answer' but no citations were provided.")
            
        for citation in decision.citations:
            if citation not in evidence_map:
                errors.append(f"Invented Citation: '{citation}' does not exist in the evidence map.")
                
    elif decision.decision == "insufficient_evidence":
        if decision.answer:
            errors.append("Decision is 'insufficient_evidence' but an answer was provided.")
            
    return errors

def render_response(decision: RAGDecision, evidence_map: dict):
    """Converts a validated decision into a human-readable presentation."""
    print("=== FINAL ANSWER ===")
    if decision.decision == "insufficient_evidence":
        print("I don't have enough information in the knowledge base to answer that safely.")
    elif decision.decision == "conflicting_evidence":
        print("The retrieved documents contain conflicting information. Please verify with a human.")
        if decision.reason:
            print(f"Reasoning: {decision.reason}")
    elif decision.decision == "answer":
        print(decision.answer)
        print("\nSOURCES:")
        for citation in set(decision.citations):
            doc = evidence_map[citation]
            print(f" - [{citation}] {doc.metadata.get('document_id')} (Section: {doc.metadata.get('section', 'N/A')})")
    print("====================")
