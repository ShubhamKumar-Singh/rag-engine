import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """
    Central configuration class for the RAG Engine.
    All project-wide constants and environment configs defined here.
    """

    # ==============================
    # Base Paths
    # ==============================

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"

    # Ensure required directories exist
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)

    # ==============================
    # Environment
    # ==============================

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # ==============================
    # API metadata
    # ==============================
    API_TITLE: str = os.getenv("API_TITLE", "RAG Engine (Local)")
    API_VERSION: str = os.getenv("API_VERSION", "0.1.0")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "Retrieval-Augmented Generation Engine with local models")

    # ==============================
    # Local model configuration (free, local inference)
    # ==============================

    # Embeddings model (sentence-transformers)
    EMBEDDINGS_MODEL: str = os.getenv(
        "EMBEDDINGS_MODEL",
        "all-MiniLM-L6-v2"
    )

    # Batch size used for local embedding generation
    EMBEDDINGS_BATCH_SIZE: int = int(
        os.getenv("EMBEDDINGS_BATCH_SIZE", 64)
    )

    # Local LLM model for generation (text2text). Choose a small model for CPU.
    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "google/flan-t5-small"
    )

    LLM_TEMPERATURE: float = float(
        os.getenv("LLM_TEMPERATURE", 0.7)
    )

    MAX_CONTEXT_LENGTH: int = int(
        os.getenv("MAX_CONTEXT_LENGTH", 4000)
    )

    # ==============================
    # FAISS Configuration
    # ==============================

    FAISS_INDEX_PATH: Path = DATA_DIR / "vector.index"
    # Default dimension for all-MiniLM-L6-v2 is 384
    FAISS_DIMENSION: int = int(
        os.getenv("FAISS_DIMENSION", 384)
    )

    FAISS_INDEX_TYPE: str = os.getenv(
        "FAISS_INDEX_TYPE",
        "flat"  # options: flat, ivf
    )

    FAISS_NLIST: int = int(
        os.getenv("FAISS_NLIST", 100)
    )

    # ==============================
    # SQLite Configuration
    # ==============================

    DATABASE_PATH: Path = DATA_DIR / "database.db"

    # ==============================
    # Chunking Configuration
    # ==============================

    CHUNK_SIZE: int = int(
        os.getenv("CHUNK_SIZE", 800)
    )

    CHUNK_OVERLAP: int = int(
        os.getenv("CHUNK_OVERLAP", 100)
    )

    MAX_CHUNKS_PER_DOCUMENT: int = int(
        os.getenv("MAX_CHUNKS_PER_DOCUMENT", 1000)
    )

    # ==============================
    # Search Configuration
    # ==============================

    TOP_K: int = int(
        os.getenv("TOP_K", 5)
    )

    SIMILARITY_THRESHOLD: float = float(
        os.getenv("SIMILARITY_THRESHOLD", 0.3)
    )

    # ==============================
    # File Upload Configuration
    # ==============================

    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB

    ALLOWED_FILE_TYPES = [
        "pdf",
        "txt",
        "jpg",
        "jpeg",
        "png",
        "gif"
    ]

    # ==============================
    # OCR Configuration
    # ==============================

    TESSERACT_CMD: str = os.getenv(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # ==============================
    # Logging Configuration
    # ==============================

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: Path = DATA_DIR / "app.log"

    # ==============================
    # Rate Limiting (Future Use)
    # ==============================

    RATE_LIMIT_PER_MINUTE: int = int(
        os.getenv("RATE_LIMIT_PER_MINUTE", 60)
    )


# Create a global settings object
settings = Settings()
