"""Database models for storing document metadata"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """Document metadata model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, jpg, etc.
    original_text = Column(Text, nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document(id={self.id}, file_name={self.file_name}, chunks={self.chunk_count})>"


class Chunk(Base):
    """Text chunks for vector storage"""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in original document
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    faiss_id = Column(String(100), unique=True, nullable=True)  # FAISS vector ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, faiss_id={self.faiss_id})>"


class SearchLog(Base):
    """Log for search queries and results"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    result_count = Column(Integer, default=0)
    top_similarity = Column(Float, nullable=True)
    response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SearchLog(id={self.id}, query_len={len(self.query)}, results={self.result_count})>"
