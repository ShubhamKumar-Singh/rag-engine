"""Utility functions and helpers"""

import os
from pathlib import Path
from datetime import datetime


def ensure_directories():
    """Ensure all required directories exist"""
    from app.core.config import (
        DATA_DIR, UPLOADS_DIR, LOGS_DIR, 
        FAISS_INDEX_PATH
    )
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR = DATA_DIR / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep files to ensure directories are tracked
    for dir_path in [DATA_DIR, UPLOADS_DIR, LOGS_DIR]:
        gitkeep_path = dir_path / ".gitkeep"
        if not gitkeep_path.exists():
            gitkeep_path.touch()


def format_bytes(bytes_size: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_time(seconds: float) -> str:
    """Convert seconds to human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        return f"{seconds/60:.2f} m"
    else:
        return f"{seconds/3600:.2f} h"


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def load_env_variables():
    """Load environment variables from .env file"""
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent / ".env"
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
