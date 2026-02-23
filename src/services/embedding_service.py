from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import settings
from app.core.logging_config import logger


class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDINGS_MODEL):
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.batch_size = settings.EMBEDDINGS_BATCH_SIZE

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, settings.FAISS_DIMENSION)

        embeddings = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=False)
        return np.array(embeddings, dtype=np.float32)


_emb = None


def get_embedding_service() -> EmbeddingService:
    global _emb
    if _emb is None:
        _emb = EmbeddingService()
    return _emb
