import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# FAISS Configuration
FAISS_INDEX_PATH = DATA_DIR / "vector.index"
FAISS_DIMENSION = 1536  # OpenAI embedding dimension

# SQLite Configuration
DATABASE_PATH = DATA_DIR / "database.db"

# Embedding Configuration
EMBEDDINGS_MODEL = "text-embedding-3-small"
EMBEDDINGS_BATCH_SIZE = 100

# Chunking Configuration
CHUNK_SIZE = 800  # Characters
CHUNK_OVERLAP = 100  # Characters

# Search Configuration
TOP_K = 5  # Number of similar chunks to retrieve
SIMILARITY_THRESHOLD = 0.3  # Optional: filter results by similarity

# LLM Configuration
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7
MAX_CONTEXT_LENGTH = 4000

# API Configuration
API_TITLE = "Custom Data Chat System"
API_VERSION = "1.0.0"
API_DESCRIPTION = "RAG Engine for custom data analysis"

# File Upload Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_FILE_TYPES = ["pdf", "txt", "jpg", "jpeg", "png", "gif"]

# OpenAI API Key (from environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
