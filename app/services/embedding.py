"""Embedding generation service using OpenAI API"""

from typing import List
import numpy as np
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, EMBEDDINGS_MODEL, EMBEDDINGS_BATCH_SIZE, FAISS_DIMENSION
from app.core.logging_config import logger


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = EMBEDDINGS_MODEL):
        if not api_key:
            logger.error("OPENAI_API_KEY not set in environment")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimension = FAISS_DIMENSION
        logger.info(f"EmbeddingService initialized with model: {model}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided to get_embedding")
                return [0.0] * self.dimension
            
            # Truncate text if too long (OpenAI has limits)
            text = text[:8191]
            
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)}")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided to get_embeddings_batch")
            return []
        
        all_embeddings = []
        
        # Process in batches to avoid rate limiting
        for i in range(0, len(texts), EMBEDDINGS_BATCH_SIZE):
            batch = texts[i:i + EMBEDDINGS_BATCH_SIZE]
            
            # Filter out empty texts
            batch = [t for t in batch if t and t.strip()]
            
            if not batch:
                continue
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                # Sort by index to maintain order
                batch_embeddings = sorted(response.data, key=lambda x: x.index)
                
                for item in batch_embeddings:
                    all_embeddings.append(item.embedding)
                
                logger.info(f"Generated embeddings for batch {i//EMBEDDINGS_BATCH_SIZE + 1}")
            
            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {str(e)}")
                raise
        
        logger.info(f"Generated {len(all_embeddings)} embeddings total")
        return all_embeddings
    
    def get_embeddings_as_numpy(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings and return as numpy array
        
        Args:
            texts: List of texts to embed
            
        Returns:
            NumPy array of embeddings
        """
        embeddings = self.get_embeddings_batch(texts)
        return np.array(embeddings, dtype=np.float32)


# Create singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create EmbeddingService singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_embedding(text: str) -> List[float]:
    """Convenience function to get single embedding"""
    service = get_embedding_service()
    return service.get_embedding(text)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to get multiple embeddings"""
    service = get_embedding_service()
    return service.get_embeddings_batch(texts)
