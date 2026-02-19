"""Query/Ask routes for RAG system"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from time import time

from app.db.database import get_db
from app.schemas.schemas import QueryRequest, QueryResponse
from app.services.operations import QueryService
from app.core.logging_config import logger

router = APIRouter(prefix="/ask", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Ask a question about the uploaded documents
    
    The system will:
    1. Generate embedding for the question
    2. Search FAISS for similar document chunks
    3. Retrieve full text from database
    4. Generate answer using LLM with retrieved context
    
    Returns:
    - answer: The generated answer
    - sources: The documents and chunks used as context
    - response_time_ms: Time taken to process the query
    """
    try:
        start_time = time()
        logger.info(f"Received query: {request.question[:50]}...")
        
        # Process query
        result = QueryService.answer_question(request.question, request.top_k, db)
        
        # Calculate response time
        response_time_ms = (time() - start_time) * 1000
        
        if not result.get("success", False):
            return QueryResponse(
                question=request.question,
                answer=result.get("answer", "Error processing query"),
                sources=[],
                response_time_ms=response_time_ms
            )
        
        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=result.get("sources", []),
            response_time_ms=response_time_ms
        )
    
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return QueryResponse(
            question=request.question,
            answer=f"Error: {str(e)}",
            sources=[],
            response_time_ms=0
        )
