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
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") == "development"
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
