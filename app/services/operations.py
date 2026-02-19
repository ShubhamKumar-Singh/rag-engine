"""Business logic for upload and query operations"""

import os
import tempfile
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.file_extraction import FileExtractor, FileValidator
from app.services.chunking import chunk_text
from app.services.embedding import get_embedding_service
from app.services.faiss_store import get_faiss_store
from app.db.models import Document, Chunk
from app.core.logging_config import logger
from app.core.config import LLM_MODEL, LLM_TEMPERATURE, MAX_CONTEXT_LENGTH, TOP_K


class UploadService:
    """Service for handling file uploads and ingestion"""
    
    @staticmethod
    def process_upload(file_content: bytes, filename: str, db: Session) -> dict:
        """
        Process uploaded file: extract text, chunk, embed, and store
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            db: Database session
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Validate file
            file_type = FileExtractor.get_file_type(filename)
            is_valid, error_msg = FileValidator.validate_file(filename, len(file_content))
            
            if not is_valid:
                logger.warning(f"File validation failed: {error_msg}")
                return {"success": False, "message": error_msg}
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                # Extract text
                logger.info(f"Extracting text from {filename}")
                original_text = FileExtractor.extract_text(tmp_path, file_type)
                
                if not original_text or not original_text.strip():
                    return {"success": False, "message": "No text could be extracted from file"}
                
                # Create document record
                document = Document(
                    file_name=filename,
                    file_type=file_type,
                    original_text=original_text,
                    chunk_count=0
                )
                db.add(document)
                db.commit()
                db.refresh(document)
                logger.info(f"Created document record: id={document.id}")
                
                # Chunk text
                chunks = chunk_text(original_text)
                logger.info(f"Created {len(chunks)} chunks")
                
                # Generate embeddings
                embedding_service = get_embedding_service()
                embeddings = embedding_service.get_embeddings_as_numpy(chunks)
                logger.info(f"Generated embeddings: shape {embeddings.shape}")
                
                # Store in FAISS
                faiss_store = get_faiss_store()
                chunk_doc_ids = [f"{document.id}_{i}" for i in range(len(chunks))]
                faiss_ids = faiss_store.add_vectors(embeddings, chunk_doc_ids)
                
                # Store chunks in database
                for i, (chunk_text_content, faiss_id) in enumerate(zip(chunks, faiss_ids)):
                    chunk = Chunk(
                        document_id=document.id,
                        chunk_index=i,
                        chunk_text=chunk_text_content,
                        faiss_id=str(faiss_id)
                    )
                    db.add(chunk)
                
                # Update document chunk count
                document.chunk_count = len(chunks)
                db.commit()
                
                # Save FAISS index
                faiss_store.save_index()
                
                logger.info(f"Upload completed: {filename} ({len(chunks)} chunks, {len(embeddings)} vectors)")
                
                return {
                    "success": True,
                    "message": f"Successfully processed {filename}",
                    "filename": filename,
                    "file_type": file_type,
                    "chunks_created": len(chunks),
                    "vectors_stored": len(embeddings)
                }
            
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        except Exception as e:
            import traceback
            logger.error(f"Error processing upload: {repr(e)}")
            logger.debug(traceback.format_exc())
            db.rollback()
            return {
                "success": False,
                "message": f"Error processing file: {repr(e)}"
            }
    
    @staticmethod
    def process_text_upload(text_content: str, filename: str, db: Session) -> dict:
        """
        Process uploaded text: chunk, embed, and store
        
        Args:
            text_content: Text content as string
            filename: Name for the text document
            db: Database session
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Validate text
            if not text_content or not text_content.strip():
                return {"success": False, "message": "Text content cannot be empty"}
            
            file_type = "text"
            logger.info(f"Processing text upload: {filename}")
            
            # Create document record
            document = Document(
                file_name=filename,
                file_type=file_type,
                original_text=text_content,
                chunk_count=0
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            logger.info(f"Created document record: id={document.id}")
            
            # Chunk text
            chunks = chunk_text(text_content)
            logger.info(f"Created {len(chunks)} chunks from text")
            
            # Generate embeddings
            embedding_service = get_embedding_service()
            embeddings = embedding_service.get_embeddings_as_numpy(chunks)
            logger.info(f"Generated embeddings: shape {embeddings.shape}")
            
            # Store in FAISS
            faiss_store = get_faiss_store()
            chunk_doc_ids = [f"{document.id}_{i}" for i in range(len(chunks))]
            faiss_ids = faiss_store.add_vectors(embeddings, chunk_doc_ids)
            
            # Store chunks in database
            for i, (chunk_text_content, faiss_id) in enumerate(zip(chunks, faiss_ids)):
                chunk = Chunk(
                    document_id=document.id,
                    chunk_index=i,
                    chunk_text=chunk_text_content,
                    faiss_id=str(faiss_id)
                )
                db.add(chunk)
            
            # Update document chunk count
            document.chunk_count = len(chunks)
            db.commit()
            
            # Save FAISS index
            faiss_store.save_index()
            
            logger.info(f"Text upload completed: {filename} ({len(chunks)} chunks, {len(embeddings)} vectors)")
            
            return {
                "success": True,
                "message": f"Successfully processed {filename}",
                "filename": filename,
                "file_type": file_type,
                "chunks_created": len(chunks),
                "vectors_stored": len(embeddings)
            }
        
        except Exception as e:
            import traceback
            logger.error(f"Error processing text upload: {repr(e)}")
            logger.debug(traceback.format_exc())
            db.rollback()
            return {
                "success": False,
                "message": f"Error processing text: {repr(e)}"
            }


class QueryService:
    """Service for handling queries against the RAG system"""
    
    @staticmethod
    def answer_question(question: str, top_k: int = TOP_K, db: Session = None) -> dict:
        """
        Answer a question using the RAG system
        
        Args:
            question: User question
            top_k: Number of top chunks to retrieve
            db: Database session
            
        Returns:
            Dictionary with answer and source information
        """
        try:
            # Generate embedding for question
            embedding_service = get_embedding_service()
            question_embedding = embedding_service.get_embedding(question)
            logger.info(f"Generated embedding for question: {question[:50]}...")
            
            # Search FAISS
            faiss_store = get_faiss_store()
            distances, doc_ids = faiss_store.search(question_embedding, k=top_k)
            
            if not doc_ids:
                return {
                    "success": False,
                    "question": question,
                    "answer": "No relevant documents found in the knowledge base.",
                    "sources": [],
                    "response_time_ms": 0,
                    "message": "No matching documents"
                }
            
            # Retrieve chunk texts from database
            chunks_info = []
            context_text = ""
            
            if db:
                for i, (distance, doc_id) in enumerate(zip(distances, doc_ids)):
                    # Parse doc_id format: "doc_id_chunk_index"
                    try:
                        doc_id_parts = doc_id.rsplit('_', 1)
                        doc_num = int(doc_id_parts[0])
                        
                        # Get document and chunk info
                        document = db.query(Document).filter(Document.id == doc_num).first()
                        chunks = db.query(Chunk).filter(
                            Chunk.document_id == doc_num
                        ).all()
                        
                        if chunks and i < len(chunks):
                            chunk = chunks[i]
                            # Convert L2 distance to similarity score (0-1 range)
                            similarity = 1 / (1 + distance)
                            
                            chunks_info.append({
                                "document": document.file_name if document else "Unknown",
                                "chunk_index": chunk.chunk_index,
                                "text": chunk.chunk_text,
                                "similarity": float(similarity)
                            })
                            
                            context_text += f"\n{chunk.chunk_text}"
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing doc_id {doc_id}: {str(e)}")
            
            # Generate answer using LLM
            answer = QueryService._generate_answer(question, context_text)
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "sources": chunks_info,
                "response_time_ms": 0
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "question": question,
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "response_time_ms": 0
            }
    
    @staticmethod
    def _generate_answer(question: str, context: str) -> str:
        """
        Generate answer using LLM
        
        Args:
            question: User question
            context: Retrieved context from documents
            
        Returns:
            Generated answer
        """
        try:
            # Use local transformers pipeline for generation
            from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
            
            # Truncate context to max allowed length
            context = context[:MAX_CONTEXT_LENGTH]

            prompt = f"""Answer the question based strictly on the provided context. If the answer cannot be found in the context, say so.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"""

            # Lazy-load model and tokenizer (small seq2seq model recommended for CPU)
            model_name = LLM_MODEL
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                gen = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
            except Exception as e:
                logger.error(f"Failed to load local LLM model '{model_name}': {e}")
                return "Local LLM model not available. Unable to generate answer."

            outputs = gen(prompt, max_length=512, do_sample=False)
            answer = outputs[0]["generated_text"] if isinstance(outputs, list) and outputs else str(outputs)
            logger.info("Generated answer using local LLM model")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
