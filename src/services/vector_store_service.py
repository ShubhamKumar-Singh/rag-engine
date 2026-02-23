from pathlib import Path
from typing import Dict, List, Tuple, Optional
import faiss
import numpy as np
import json
from src.config import settings
from app.core.logging_config import logger


class VectorStore:
    def __init__(self, index_path: Path = None, dim: int = settings.FAISS_DIMENSION):
        self.index_path = index_path or settings.FAISS_INDEX
        self.dim = dim
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict[str, Dict] = {}
        self._load_or_create()

    def _load_or_create(self):
        # Load metadata
        try:
            if settings.METADATA_JSON.exists():
                with open(settings.METADATA_JSON, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
        except Exception:
            logger.warning("Failed to load metadata.json; starting fresh")

        # Load or create FAISS index
        if self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                logger.info(f"Loaded FAISS index ({self.index.ntotal} vectors)")
            except Exception as e:
                logger.warning(f"Failed to read FAISS index: {e}; creating new flat index")
                self.index = faiss.IndexFlatL2(self.dim)
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            logger.info("Created new FAISS IndexFlatL2")

    def save(self):
        try:
            # Save index
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            # Save metadata
            with open(settings.METADATA_JSON, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info("Saved FAISS index and metadata")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def _product_already_indexed(self, product: Dict) -> Optional[int]:
        """Return the existing index id if product (by id) has same embedding_hash and model_version."""
        for idx, meta in self.metadata.items():
            try:
                if meta.get("id") == product.get("id"):
                    # if embedding_hash matches and model version matches, it's already indexed
                    if meta.get("embedding_hash") == product.get("embedding_hash") and meta.get("model_version") == settings.MODEL_VERSION:
                        return int(idx)
            except Exception:
                continue
        return None

    def add_products(self, products: List[Dict], embeddings: np.ndarray) -> List[int]:
        """Add product embeddings and record metadata. Returns list of assigned indices."""
        if embeddings.shape[0] == 0:
            return []

        if embeddings.shape[1] != self.dim:
            raise ValueError("Embedding dimension mismatch")

        assigned: List[int] = []

        # Iterate and add only those not already present (keeps alignment between products and embeddings)
        to_add_embeddings = []
        to_add_products = []
        for prod, emb in zip(products, embeddings):
            existing = self._product_already_indexed(prod)
            if existing is not None:
                assigned.append(existing)
            else:
                to_add_products.append(prod)
                to_add_embeddings.append(emb)

        if to_add_embeddings:
            arr = np.vstack(to_add_embeddings).astype(np.float32)
            start = self.index.ntotal
            self.index.add(arr)
            new_assigned = list(range(start, int(self.index.ntotal)))

            # Store metadata for newly added
            for idx, prod in zip(new_assigned, to_add_products):
                # add model version to metadata for future checks
                prod_meta = dict(prod)
                prod_meta["model_version"] = settings.MODEL_VERSION
                self.metadata[str(idx)] = prod_meta
                assigned.append(idx)

        return assigned

    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[float], List[Dict]]:
        if self.index.ntotal == 0:
            return [], []

        q = np.asarray([query_vector], dtype=np.float32)
        k = min(k, int(self.index.ntotal))
        distances, indices = self.index.search(q, k)
        distances = distances[0].tolist()
        ids = [str(i) for i in indices[0].tolist()]
        results = [self.metadata.get(i, {}) for i in ids]
        return distances, results


_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
