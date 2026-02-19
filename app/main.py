from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload_routes, query_routes
from app.core.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.core.logging_config import logger
from app.db.database import init_db
from app.services.faiss_store import get_faiss_store
from app.services.embedding import get_embedding_service

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


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "RAG Engine Running 🚀",
        "version": API_VERSION,
        "message": "Upload documents at /upload and ask questions at /ask"
    }


@app.get("/health")
def detailed_health():
    """Detailed health check with system status"""
    faiss_stats = {}
    embedding_configured = False
    embeddings_backend = "local"
    llm_backend = "local"
    
    try:
        faiss_store = get_faiss_store()
        faiss_stats = faiss_store.get_stats()
    except Exception as e:
        logger.warning(f"Error getting FAISS stats: {str(e)}")
    
    try:
        embedding_service = get_embedding_service()
        embedding_configured = True
    except Exception as e:
        logger.warning(f"Error checking embedding service: {str(e)}")
    
    return {
        "status": "healthy",
        "database": "initialized",
        "faiss": faiss_stats,
        "embeddings_configured": embedding_configured,
        "embeddings_backend": embeddings_backend,
        "llm_backend": llm_backend,
        "endpoints": {
            "upload": "/upload (POST)",
            "ask": "/ask (POST)",
            "docs": "/docs",
            "health": "/health"
        }
    }

