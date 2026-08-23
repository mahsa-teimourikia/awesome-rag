import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def create_embeddings():
    """Abstracted embedding model creation."""
    from src.config import EMBEDDING_MODEL
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def get_vector_store(persist_directory: str, collection_name: str) -> Chroma:
    """Gets or creates the Chroma vector store."""
    embeddings = create_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def index_documents(docs: list[Document], persist_directory: str, collection_name: str):
    """Indexes chunks into Chroma."""
    print(f"Indexing {len(docs)} chunks into {persist_directory}...")
    embeddings = create_embeddings()
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    print("Indexing complete.")

def retrieve_base(query: str, vector_store: Chroma, top_k: int) -> list[Document]:
    """Baseline Vector Search."""
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    return retriever.invoke(query)

def retrieve_expanded(query: str, vector_store: Chroma, top_k: int) -> list[Document]:
    """Multi-Query Expansion using an LLM."""
    from langchain_classic.retrievers.multi_query import MultiQueryRetriever
    from src.generation import create_llm
    
    llm = create_llm()
    # Pulls more candidates to compensate for expansion
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k * 3}) 
    mq_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)
    
    return mq_retriever.invoke(query)

def retrieve_reranked(query: str, candidates: list[Document], top_k: int) -> list[Document]:
    """Cross-Encoder Reranking."""
    from sentence_transformers import CrossEncoder
    
    # Using a fast, local cross-encoder
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
    pairs = [[query, doc.page_content] for doc in candidates]
    scores = model.predict(pairs)
    
    # Zip docs with scores, sort descending, and return top_k
    scored_docs = zip(candidates, scores)
    sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
    
    return [doc for doc, score in sorted_docs[:top_k]]

def retrieve_filtered(query: str, vector_store: Chroma, top_k: int) -> list[Document]:
    """Metadata Filtering (Pre-Retrieval) using LLM intent extraction."""
    from src.generation import extract_query_filter
    
    filter_dict = extract_query_filter(query)
    
    if filter_dict:
        print(f"  [Filter Applied: {filter_dict}]")
        retriever = vector_store.as_retriever(search_kwargs={"k": top_k, "filter": filter_dict})
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
        
    return retriever.invoke(query)

def retrieve_candidates(query: str, vector_store: Chroma, top_k: int) -> list[Document]:
    """Default legacy function, mapping to base for compatibility."""
    return retrieve_base(query, vector_store, top_k)
