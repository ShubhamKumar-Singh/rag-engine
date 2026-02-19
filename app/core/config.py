import os
from pathlib import Path
from dotenv import load_dotenv
import sqlite3

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

    # Quick integrity check: if the database file exists but is corrupted,
    # switch to a recovered DB path to allow the app to start.
    try:
        if DATABASE_PATH.exists():
            conn = sqlite3.connect(str(DATABASE_PATH))
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            row = cur.fetchone()
            conn.close()
            if row and row[0] != 'ok':
                RECOVERED = DATA_DIR / "database_recovered.db"
                print(f"WARNING: {DATABASE_PATH} appears corrupted ({row}). Using {RECOVERED} instead.")
                DATABASE_PATH = RECOVERED
    except Exception as _:
        RECOVERED = DATA_DIR / "database_recovered.db"
        print(f"Warning checking database integrity: switching to {RECOVERED}")
        DATABASE_PATH = RECOVERED

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

# Expose common settings as module-level constants for backward compatibility
BASE_DIR = settings.BASE_DIR
DATA_DIR = settings.DATA_DIR
UPLOADS_DIR = settings.UPLOADS_DIR

ENVIRONMENT = settings.ENVIRONMENT
DEBUG = settings.DEBUG

API_TITLE = settings.API_TITLE
API_VERSION = settings.API_VERSION
API_DESCRIPTION = settings.API_DESCRIPTION

EMBEDDINGS_MODEL = settings.EMBEDDINGS_MODEL
EMBEDDINGS_BATCH_SIZE = settings.EMBEDDINGS_BATCH_SIZE

LLM_MODEL = settings.LLM_MODEL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
MAX_CONTEXT_LENGTH = settings.MAX_CONTEXT_LENGTH

FAISS_INDEX_PATH = settings.FAISS_INDEX_PATH
FAISS_DIMENSION = settings.FAISS_DIMENSION
FAISS_INDEX_TYPE = settings.FAISS_INDEX_TYPE
FAISS_NLIST = settings.FAISS_NLIST

DATABASE_PATH = settings.DATABASE_PATH

CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP
MAX_CHUNKS_PER_DOCUMENT = settings.MAX_CHUNKS_PER_DOCUMENT

TOP_K = settings.TOP_K
SIMILARITY_THRESHOLD = settings.SIMILARITY_THRESHOLD

MAX_FILE_SIZE = settings.MAX_FILE_SIZE
ALLOWED_FILE_TYPES = settings.ALLOWED_FILE_TYPES

TESSERACT_CMD = settings.TESSERACT_CMD

LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE_PATH = settings.LOG_FILE_PATH

RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
