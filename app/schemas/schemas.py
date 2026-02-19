"""Pydantic schemas for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UploadResponse(BaseModel):
    """Response for file upload"""
    success: bool
    filename: str
    file_type: str
    message: str
    chunks_created: int
    vectors_stored: int
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Request body for asking questions"""
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)


class ChunkInfo(BaseModel):
    """Information about a retrieved chunk"""
    document: str
    chunk_index: int
    text: str
    similarity: float


class QueryResponse(BaseModel):
    """Response for query/ask endpoint"""
    question: str
    answer: str
    sources: List[ChunkInfo]
    response_time_ms: float
    
    class Config:
        from_attributes = True


class DocumentInfo(BaseModel):
    """Information about a stored document"""
    id: int
    file_name: str
    file_type: str
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class IndexStats(BaseModel):
    """Statistics about the RAG system"""
    total_documents: int
    total_chunks: int
    total_vectors: int
    index_type: str
    faiss_stats: dict
    
    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    message: str
    database_initialized: bool
    faiss_initialized: bool
    openai_configured: bool
