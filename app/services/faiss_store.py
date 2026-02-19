"""FAISS vector store for similarity search"""

import faiss
import numpy as np
from typing import List, Tuple
from pathlib import Path
from app.core.config import FAISS_INDEX_PATH, FAISS_DIMENSION
from app.core.logging_config import logger


class FAISSStore:
    """Manages FAISS index for vector similarity search"""
    
    def __init__(self, index_path: str = str(FAISS_INDEX_PATH), dimension: int = FAISS_DIMENSION):
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index = None
        self.id_map = {}  # Map of FAISS vector ID to document ID
        
        # Load existing index or create new one
        if self.index_path.exists():
            self.load_index()
        else:
            self.create_index()
    
    def create_index(self):
        """Create a new FAISS index"""
        try:
            # Create a flat index (simple brute-force search)
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"Created new FAISS index with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise
    
    def add_vectors(self, vectors: np.ndarray, doc_ids: List[str]) -> List[int]:
        """
        Add vectors to the index
        
        Args:
            vectors: NumPy array of shape (n_vectors, dimension)
            doc_ids: List of document IDs corresponding to vectors
            
        Returns:
            List of FAISS indices assigned to the vectors
        """
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")
        
        if len(vectors) != len(doc_ids):
            raise ValueError("Number of vectors must match number of doc_ids")
        
        try:
            # Get starting index
            start_idx = self.index.ntotal
            
            # Add vectors
            vectors = np.asarray(vectors, dtype=np.float32)
            self.index.add(vectors)
            
            # Map indices to doc IDs
            end_idx = self.index.ntotal
            for i, doc_id in enumerate(doc_ids):
                self.id_map[start_idx + i] = doc_id
            
            logger.info(f"Added {len(vectors)} vectors to FAISS index (total: {self.index.ntotal})")
            return list(range(start_idx, end_idx))
        
        except Exception as e:
            logger.error(f"Error adding vectors to FAISS: {str(e)}")
            raise
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[float], List[str]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector as numpy array or list
            k: Number of nearest neighbors to retrieve
            
        Returns:
            Tuple of (distances, document_ids)
        """
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return [], []
        
        try:
            # Ensure correct format
            if isinstance(query_vector, list):
                query_vector = np.array([query_vector], dtype=np.float32)
            else:
                query_vector = np.asarray([query_vector], dtype=np.float32)
            
            # Adjust k if fewer vectors in index
            k = min(k, self.index.ntotal)
            
            # Search
            distances, indices = self.index.search(query_vector, k)
            
            # Convert to output format
            distances = distances[0].tolist()
            doc_ids = [self.id_map.get(idx, f"unknown_{idx}") for idx in indices[0].tolist()]
            
            logger.info(f"FAISS search returned {len(doc_ids)} results with distances: {distances}")
            return distances, doc_ids
        
        except Exception as e:
            logger.error(f"Error searching FAISS: {str(e)}")
            raise
    
    def save_index(self):
        """Save index to disk"""
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            logger.info(f"Saved FAISS index to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    def load_index(self):
        """Load index from disk"""
        try:
            self.index = faiss.read_index(str(self.index_path))
            logger.info(f"Loaded FAISS index from {self.index_path} (total vectors: {self.index.ntotal})")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            # Create new index if loading fails
            self.create_index()
    
    def get_stats(self) -> dict:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "file_path": str(self.index_path),
            "exists": self.index_path.exists()
        }


# Create singleton instance
_faiss_store = None


def get_faiss_store() -> FAISSStore:
    """Get or create FAISSStore singleton"""
    global _faiss_store
    if _faiss_store is None:
        _faiss_store = FAISSStore()
    return _faiss_store
