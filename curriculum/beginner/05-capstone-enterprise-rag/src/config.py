import os
from dotenv import load_dotenv

load_dotenv()

# Configuration Layer
LLM_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = 0.0

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_STORE_PATH = "./chroma_db"
COLLECTION_NAME = "northstar_kb"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 5
