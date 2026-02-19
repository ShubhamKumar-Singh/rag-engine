from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.operations import UploadService
from app.schemas.schemas import UploadResponse, TextUploadRequest
from app.core.logging_config import logger

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/file", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document file (PDF, TXT, or Image) for RAG processing
    
    - Accepts PDF, TXT, JPG, PNG, GIF files
    - Extracts text automatically
    - Chunks text and generates embeddings
    - Stores vectors in FAISS and metadata in SQLite
    """
    try:
        logger.info(f"Received file upload request: {file.filename}")
        
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
        logger.error(f"Error in file upload endpoint: {str(e)}")
        return UploadResponse(
            success=False,
            filename=file.filename,
            file_type="unknown",
            message=f"Error: {str(e)}",
            chunks_created=0,
            vectors_stored=0
        )


@router.post("/text", response_model=UploadResponse)
async def upload_text(request: TextUploadRequest, db: Session = Depends(get_db)):
    """
    Upload text content directly for RAG processing
    
    - Paste raw text or test content
    - Chunks text and generates embeddings
    - Stores vectors in FAISS and metadata in SQLite
    """
    try:
        # Use description as filename if provided, otherwise generate one
        filename = request.description or "text_upload"
        if not filename.endswith(".txt"):
            filename = f"{filename}.txt"
        
        logger.info(f"Received text upload request: {filename}")
        
        # Process text upload
        result = UploadService.process_text_upload(request.text, filename, db)
        
        if not result["success"]:
            return UploadResponse(
                success=False,
                filename=filename,
                file_type="text",
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
        logger.error(f"Error in text upload endpoint: {str(e)}")
        return UploadResponse(
            success=False,
            filename=request.description or "text_upload.txt",
            file_type="text",
            message=f"Error: {repr(e)}",
            chunks_created=0,
            vectors_stored=0
        )


@router.post("/text/raw", response_model=UploadResponse)
async def upload_text_raw(raw_text: str = File(...), filename: str = "text_upload.txt", db: Session = Depends(get_db)):
    """
    Upload plain text with content-type `text/plain` or as form field `file`.
    Use this when sending multi-line text without JSON escaping.
    """
    try:
        # Some clients send as a form 'file' field; ensure it's a str
        if isinstance(raw_text, bytes):
            raw_text = raw_text.decode('utf-8', errors='ignore')

        logger.info(f"Received raw text upload request: {filename}")
        result = UploadService.process_text_upload(raw_text, filename, db)

        if not result["success"]:
            return UploadResponse(
                success=False,
                filename=filename,
                file_type="text",
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
        logger.error(f"Error in raw text upload endpoint: {repr(e)}")
        return UploadResponse(
            success=False,
            filename=filename,
            file_type="text",
            message=f"Error: {repr(e)}",
            chunks_created=0,
            vectors_stored=0
        )



