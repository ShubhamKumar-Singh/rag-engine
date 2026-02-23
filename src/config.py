from pydantic import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    PRODUCTS_JSON: Path = DATA_DIR / "products.json"
    METADATA_JSON: Path = DATA_DIR / "metadata.json"
    FAISS_INDEX: Path = DATA_DIR / "vector.index"

    # Embeddings
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDINGS_BATCH_SIZE: int = 64
    FAISS_DIMENSION: int = 384
    # Model version for embeddings; bump when retraining or switching model
    MODEL_VERSION: str = "emb-v1"

    # Search
    TOP_K: int = 5

    # Optional OpenAI key for filter extraction / LLM improvements
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()

# Ensure folders exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
