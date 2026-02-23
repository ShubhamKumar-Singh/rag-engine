"""
RAG Engine - Retrieval-Augmented Generation System
Main entry point for the application
"""

import os
from app.utils import load_env_variables, ensure_directories

# Load environment variables
load_env_variables()

# Ensure directories exist
ensure_directories()

# Import after environment setup
# Keep legacy utils but point to new src FastAPI app
from app.utils import load_env_variables  # keep for env loading
try:
    from src.main import app
except Exception:
    # fallback to legacy app if new app not yet ready
    from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") == "development"
    
    # Run server (prefer new src.main)
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
