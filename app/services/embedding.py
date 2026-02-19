"""Local embedding service using sentence-transformers"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import EMBEDDINGS_MODEL, EMBEDDINGS_BATCH_SIZE, FAISS_DIMENSION
from app.core.logging_config import logger


class EmbeddingService:
    """Service for generating embeddings using a local SentenceTransformer model"""

    def __init__(self, model_name: str = EMBEDDINGS_MODEL):
        self.model_name = model_name
        logger.info(f"Loading local embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = FAISS_DIMENSION
            logger.info(f"Embedding model loaded: {model_name} (dim={self.dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{model_name}': {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            logger.warning("Empty text provided to get_embedding")
            return [0.0] * self.dimension

        # SentenceTransformer handles truncation internally; encode returns numpy array
        vec = self.model.encode(text, show_progress_bar=False)
        return vec.tolist()

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            logger.warning("Empty text list provided to get_embeddings_batch")
            return []

        # Filter and keep mapping to preserve order
        valid_texts = [t if t and t.strip() else "" for t in texts]
        embeddings = self.model.encode(valid_texts, batch_size=EMBEDDINGS_BATCH_SIZE, show_progress_bar=False)
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()

        logger.info(f"Generated {len(embeddings)} embeddings total (local)")
        return embeddings

    def get_embeddings_as_numpy(self, texts: List[str]) -> np.ndarray:
        embeddings = self.get_embeddings_batch(texts)
        return np.array(embeddings, dtype=np.float32)


# Singleton
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_embedding(text: str) -> List[float]:
    service = get_embedding_service()
    return service.get_embedding(text)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    service = get_embedding_service()
    return service.get_embeddings_batch(texts)
