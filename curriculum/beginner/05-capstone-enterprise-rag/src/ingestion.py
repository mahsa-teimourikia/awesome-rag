import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document

def load_knowledge_base(data_dir: str) -> list[Document]:
    """Loads markdown documents from the synthetic enterprise corpus."""
    loader = DirectoryLoader(data_dir, glob="**/*.md", show_progress=False)
    docs = loader.load()
    
    # Enrich metadata manually for the capstone context
    for doc in docs:
        source_path = doc.metadata.get("source", "")
        doc.metadata["document_id"] = os.path.basename(source_path).replace(".md", "")
        doc.metadata["department"] = os.path.basename(os.path.dirname(source_path))
    
    return docs
