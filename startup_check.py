#!/usr/bin/env python
"""
Quick startup test for RAG Engine
Verifies all dependencies are installed and configured
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python 3.10+ is installed"""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required, you have {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} installed")
    return True


def check_imports():
    """Check if required packages are installed"""
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'faiss': 'FAISS',
        'numpy': 'NumPy',
        'sentence_transformers': 'sentence-transformers',
        'transformers': 'transformers',
        'pypdf': 'PyPDF',
        'PIL': 'Pillow',
        'pydantic': 'Pydantic'
    }
    
    missing = []
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            missing.append(name)
    
    return len(missing) == 0


def check_env_file():
    """Check if .env file exists (no API key required for local models)"""
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env from .env.docker or set required values")
        return False

    print("✅ .env file found")
    return True


def check_data_directories():
    """Check if data directories exist"""
    data_dir = Path(__file__).resolve().parent / "data"
    subdirs = ["logs", "uploads"]
    
    if not data_dir.exists():
        print(f"❌ Data directory doesn't exist: {data_dir}")
        return False
    
    for subdir in subdirs:
        if not (data_dir / subdir).exists():
            print(f"❌ Missing directory: {data_dir / subdir}")
            return False
    
    print("✅ Data directories exist")
    return True


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print(" 🚀 RAG Engine Startup Check")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("Environment Variables", check_env_file),
        ("Data Directories", check_data_directories),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All checks passed! Ready to start the server.\n")
        print("Start the server with:")
        print("  python -m uvicorn app.main:app --reload\n")
        print("Or use the convenience script:")
        print("  python run.py\n")
        print("Then access:")
        print("  - API docs: http://127.0.0.1:8000/docs")
        print("  - Health check: http://127.0.0.1:8000/health\n")
    else:
        print("❌ Some checks failed. Please fix the issues above.\n")
        print("Installation steps:")
        print("  1. pip install -r requirements.txt")
        print("  2. Create .env file with local model settings (see .env.docker)")
        print("  3. Run this check again\n")
        sys.exit(1)
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
