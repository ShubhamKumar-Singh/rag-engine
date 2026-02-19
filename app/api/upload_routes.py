from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.operations import UploadService
from app.schemas.schemas import UploadResponse
from app.core.logging_config import logger

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document (PDF, TXT, or Image) for RAG processing
    
    - Accepts PDF, TXT, JPG, PNG, GIF files
    - Extracts text automatically
    - Chunks text and generates embeddings
    - Stores vectors in FAISS and metadata in SQLite
    """
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Process upload
        result = UploadService.process_upload(file_content, file.filename, db)
        
        if not result["success"]:
            return UploadResponse(
                success=False,
                filename=file.filename,
                file_type="unknown",
                message=result["message"],
                chunks_created=0,
                vectors_stored=0
            )
        
        return UploadResponse(
            success=True,
            filename=result["filename"],
            file_type=result["file_type"],
            message=result["message"],
            chunks_created=result["chunks_created"],
            vectors_stored=result["vectors_stored"]
        )
    
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        return UploadResponse(
            success=False,
            filename=file.filename,
            file_type="unknown",
            message=f"Error: {str(e)}",
            chunks_created=0,
            vectors_stored=0
        )
