from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents_naive(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """
    Naive fixed-size chunking. Splits strictly by character count without regard for structure.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    final_chunks = []
    for doc in docs:
        chunks = text_splitter.split_documents([doc])
        for i, chunk in enumerate(chunks):
            chunk.metadata["ordinal"] = i
            chunk.metadata["chunk_id"] = f"{chunk.metadata['document_id']}#naive-{i}"
            chunk.metadata["chunking_strategy"] = "naive"
        final_chunks.extend(chunks)
        
    return final_chunks

def chunk_documents_sentence(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """
    Sentence-window chunking. Uses standard sentence separators.
    """
    # We use RecursiveCharacterTextSplitter but prioritize sentence-ending punctuation.
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[". ", "? ", "! ", "\n\n", "\n", " ", ""],
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    final_chunks = []
    for doc in docs:
        chunks = text_splitter.split_documents([doc])
        for i, chunk in enumerate(chunks):
            chunk.metadata["ordinal"] = i
            chunk.metadata["chunk_id"] = f"{chunk.metadata['document_id']}#sentence-{i}"
            chunk.metadata["chunking_strategy"] = "sentence"
        final_chunks.extend(chunks)
        
    return final_chunks

def chunk_documents_structured(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """
    Structure-aware chunking.
    First splits by Markdown headers to preserve structure, then bounds oversized sections.
    """
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    final_chunks = []
    
    for doc in docs:
        # 1. Structure-aware split
        md_chunks = markdown_splitter.split_text(doc.page_content)
        
        # 2. Add original metadata back to the structural chunks
        for chunk in md_chunks:
            chunk.metadata.update(doc.metadata)
            
            # Construct a hierarchical section name
            section = " > ".join([v for k, v in chunk.metadata.items() if k.startswith("Header")])
            if section:
                chunk.metadata["section"] = section
        
        # 3. Bound oversized sections
        sized_chunks = text_splitter.split_documents(md_chunks)
        
        # 4. Add chunk_id and ordinal
        for i, chunk in enumerate(sized_chunks):
            chunk.metadata["ordinal"] = i
            chunk.metadata["chunk_id"] = f"{chunk.metadata['document_id']}#structured-{i}"
            chunk.metadata["chunking_strategy"] = "structured"
            
        final_chunks.extend(sized_chunks)
        
    return final_chunks
