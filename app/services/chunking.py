"""Text chunking utility for splitting documents into manageable pieces"""

from typing import List
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.logging_config import logger


class TextChunker:
    """Handles text chunking with overlap"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            logger.warning("Empty text provided to chunk_text")
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Extract chunk
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.overlap
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        logger.info(f"Chunked text into {len(chunks)} chunks (size: {self.chunk_size}, overlap: {self.overlap})")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common problematic characters
        text = text.replace("\x00", "")  # Null characters
        text = text.replace("\ufffd", "")  # Invalid Unicode
        
        return text


# Create singleton instance
chunker = TextChunker()


def chunk_text(text: str) -> List[str]:
    """
    Convenience function to chunk text
    
    Args:
        text: The text to chunk
        
    Returns:
        List of text chunks
    """
    return chunker.chunk_text(text)
