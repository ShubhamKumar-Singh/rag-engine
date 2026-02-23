from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload_routes, query_routes
from app.core.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.core.logging_config import logger
from app.db.database import init_db, SessionLocal
from app.db.models import Document
from app.services.faiss_store import get_faiss_store
from app.services.embedding import get_embedding_service
from pathlib import Path
from app.core.config import FAISS_INDEX_PATH, DATABASE_PATH

# Initialize database and services
try:
    init_db()
    logger.info("Database initialized")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

try:
    faiss_store = get_faiss_store()
    logger.info(f"FAISS store initialized with {faiss_store.index.ntotal} vectors")
except Exception as e:
    logger.error(f"Failed to initialize FAISS: {str(e)}")

try:
    embedding_service = get_embedding_service()
    logger.info("Embedding service initialized")
except Exception as e:
    logger.error(f"Failed to initialize embedding service: {str(e)}")

# Perform a startup consistency check between SQLite DB and FAISS index.
try:
    session = SessionLocal()
    try:
        doc_count = session.query(Document).count()
    finally:
        session.close()

    faiss_vectors = 0
    try:
        faiss_vectors = getattr(faiss_store.index, "ntotal", 0)
    except Exception:
        faiss_vectors = 0

    faiss_path = Path(FAISS_INDEX_PATH)
    db_path = Path(DATABASE_PATH)

    # If DB has no documents but FAISS has vectors, remove stale FAISS index to avoid inconsistency
    if doc_count == 0 and faiss_vectors > 0:
        try:
            if faiss_path.exists():
                faiss_path.unlink()
                logger.info(f"Removed stale FAISS index at {faiss_path} because DB is empty")
        except Exception as e:
            logger.warning(f"Failed to remove stale FAISS index: {e}")

    # If both DB and FAISS appear empty but an index file exists, remove it to ensure clean first-run state
    if doc_count == 0 and faiss_vectors == 0 and faiss_path.exists():
        try:
            faiss_path.unlink()
            logger.info(f"Removed existing FAISS index file at {faiss_path} for clean first-run state")
        except Exception as e:
            logger.warning(f"Failed to remove existing FAISS index file: {e}")

except Exception as e:
    logger.warning(f"Startup consistency check failed: {e}")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_routes.router)
app.include_router(query_routes.router)

