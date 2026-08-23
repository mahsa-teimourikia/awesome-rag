from typing import Literal, List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

class RAGDecision(BaseModel):
    decision: Literal["answer", "insufficient_evidence", "conflicting_evidence"] = Field(
        description="The type of response being provided."
    )
    answer: Optional[str] = Field(
        default=None, 
        description="The answer to the user's question, if applicable."
    )
    citations: List[str] = Field(
        default_factory=list, 
        description="A list of evidence IDs (e.g., 'E1') that support the answer."
    )
    reason: Optional[str] = Field(
        default=None, 
        description="Internal reasoning for abstention or conflicts."
    )

class QueryFilter(BaseModel):
    department: Optional[str] = Field(
        default=None,
        description="The department this query pertains to (e.g., hr, it, sales, legal, engineering, finance, security, support)."
    )

def extract_query_filter(query: str) -> dict:
    """Extracts metadata filter constraints from the query."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(QueryFilter)
    
    prompt = ChatPromptTemplate.from_template(
        "Analyze the user's query and extract the target department if explicitly mentioned or strongly implied.\n"
        "Valid departments are: hr, it, sales, legal, engineering, finance, security, support.\n"
        "If no specific department applies, return None.\n\n"
        "Query: {query}"
    )
    
    chain = prompt | structured_llm
    result = chain.invoke({"query": query})
    
    filter_dict = {}
    if result.department:
        filter_dict["department"] = result.department.lower()
        
    return filter_dict

def build_evidence_context(candidates: list[Document]) -> tuple[str, dict[str, Document]]:
    """Maps retrieved chunks to request-local IDs (E1, E2) and builds the prompt context."""
    evidence_map = {}
    formatted_evidence = []
    
    for i, chunk in enumerate(candidates):
        e_id = f"E{i+1}"
        evidence_map[e_id] = chunk
        
        # Include metadata to help the LLM with versioning/conflicts
        meta = f"Title: {chunk.metadata.get('document_id', 'Unknown')}\n"
        if "section" in chunk.metadata:
            meta += f"Section: {chunk.metadata['section']}\n"
            
        formatted_evidence.append(f"<EVIDENCE id='{e_id}'>\n{meta}\n{chunk.page_content}\n</EVIDENCE>")
        
    return "\n\n".join(formatted_evidence), evidence_map

def create_llm():
    """Abstracted LLM creation for structured output."""
    from src.config import LLM_MODEL, TEMPERATURE
    return ChatOpenAI(model=LLM_MODEL, temperature=TEMPERATURE)

def generate_decision(query: str, context_str: str) -> RAGDecision:
    """Uses structured output to generate an answer or abstain."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(RAGDecision)
    
    prompt = ChatPromptTemplate.from_template(
        "You are an Enterprise Knowledge Assistant for Northstar Technologies.\n"
        "Your job is to answer the user's question using ONLY the supplied evidence.\n\n"
        "RULES:\n"
        "1. If the evidence does not contain the answer, you must set decision to 'insufficient_evidence'.\n"
        "2. If multiple sources give conflicting answers (and metadata does not resolve it), set decision to 'conflicting_evidence'.\n"
        "3. If you answer, you MUST cite the specific evidence IDs (e.g., 'E1') in the citations list.\n"
        "4. DO NOT use your own prior knowledge. DO NOT invent evidence IDs.\n\n"
        "EVIDENCE:\n{context}\n\n"
        "QUESTION:\n{question}"
    )
    
    chain = prompt | structured_llm
    return chain.invoke({"context": context_str, "question": query})
