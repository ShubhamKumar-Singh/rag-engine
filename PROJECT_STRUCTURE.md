# RAG Engine - Complete Project Structure

## 📁 Directory Layout

```
rag-engine/
│
├── 📁 app/                             # Main application package
│   ├── __init__.py                     # Package initializer
│   ├── main.py                         # FastAPI application entry point
│   ├── utils.py                        # Utility functions
│   │
│   ├── 📁 api/                         # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── upload_routes.py            # POST /upload endpoint (file ingestion)
│   │   └── query_routes.py             # POST /ask endpoint (question answering)
│   │
│   ├── 📁 core/                        # Core configuration and logging
│   │   ├── __init__.py
│   │   ├── config.py                   # App configuration (paths, API keys, settings)
│   │   └── logging_config.py           # Logging setup (file + console)
│   │
│   ├── 📁 db/                          # Database layer
│   │   ├── __init__.py
│   │   ├── database.py                 # SQLAlchemy setup, session management
│   │   └── models.py                   # SQLAlchemy ORM models (Document, Chunk, SearchLog)
│   │
│   ├── 📁 schemas/                     # Pydantic models for validation
│   │   ├── __init__.py
│   │   └── schemas.py                  # Request/response models (UploadResponse, QueryResponse, etc.)
│   │
│   └── 📁 services/                    # Business logic services
│       ├── __init__.py
│       ├── chunking.py                 # TextChunker: split text into overlapping chunks
│       ├── embedding.py                # EmbeddingService: OpenAI embeddings
│       ├── faiss_store.py              # FAISSStore: vector indexing and search
│       ├── file_extraction.py          # FileExtractor: PDF/image/text extraction
│       └── operations.py               # UploadService & QueryService: orchestration logic
│
├── 📁 data/                            # Data storage (Git ignored except .gitkeep)
│   ├── .gitkeep                        # Keep directory in git
│   ├── vector.index                    # FAISS index (binary file)
│   ├── database.db                     # SQLite database
│   │
│   ├── 📁 logs/                        # Application logs
│   │   ├── .gitkeep
│   │   └── rag_engine.log             # Rotating log file
│   │
│   └── 📁 uploads/                     # Temporary uploaded files (cleaned up)
│       └── .gitkeep
│
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .env                             # Environment variables (Git ignored)
├── 📄 .gitignore                       # Git ignore rules
├── 📄 README.md                        # Comprehensive documentation
├── 📄 run.py                           # Simple entry point script
├── 📄 Dockerfile                       # Docker containerization
├── 📄 docker-compose.yml               # Docker Compose configuration
└── 📄 PROJECT_STRUCTURE.md             # This file
```

---

## 🔄 Data Flow

### Upload Flow
```
Browser/Client
    ↓
POST /upload {file}
    ↓ [upload_routes.py]
UploadService.process_upload()
    ↓
FileExtractor.extract_text() → RAW TEXT
    ↓
TextChunker.chunk_text() → LIST OF CHUNKS
    ↓
EmbeddingService.get_embeddings_batch() → NUMPY ARRAY (n × 1536)
    ↓
FAISSStore.add_vectors() → Add to FAISS index
    ↓ PARALLEL
├─ SQLite: Save Document + Chunks metadata
└─ Disk: Save FAISS index file
    ↓
Response: {"success": true, "chunks_created": N, "vectors_stored": N}
```

### Query Flow
```
Browser/Client
    ↓
POST /ask {"question": "..."}
    ↓ [query_routes.py]
QueryService.answer_question()
    ↓
EmbeddingService.get_embedding() → VECTOR (1536,)
    ↓
FAISSStore.search(vector, k=5) → TOP 5 FAISS IDs + distances
    ↓
SQLite: Fetch chunk texts for top 5 IDs
    ↓
CONCAT: Combine chunks → CONTEXT STRING
    ↓
OpenAI API: Generate answer from context
    ↓
Response: {"answer": "...", "sources": [...], "response_time_ms": N}
```

---

## 📚 Key Components

### 1. **app/core/config.py**
- Centralized configuration
- Storage paths, API keys, model names
- Embedding dimension: 1536 (OpenAI)
- Chunk size: 800 characters, overlap: 100 characters

### 2. **app/services/embedding.py**
- OpenAI embeddings integration
- Batch processing with rate limiting
- Caching (optional)
- Model: text-embedding-3-small

### 3. **app/services/faiss_store.py**
- FAISS IndexFlatL2 (Euclidean distance)
- Vector ID to document ID mapping
- Save/load from disk
- Stats tracking

### 4. **app/services/chunking.py**
- Overlapping text chunks
- Text cleaning (remove null chars, extra whitespace)
- Configurable chunk size and overlap

### 5. **app/services/file_extraction.py**
- **PDF**: pypdf library
- **Images (JPG, PNG, GIF)**: Tesseract OCR
- **Text (TXT)**: Direct file reading
- Validation: size limits, file types

### 6. **app/db/models.py**
Three main tables:
- **documents**: File metadata
- **chunks**: Text chunks + FAISS ID mapping
- **search_logs**: Query history (optional)

### 7. **app/services/operations.py**
- **UploadService**: Orchestrates upload pipeline
- **QueryService**: Orchestrates query pipeline

### 8. **app/main.py**
- FastAPI application setup
- Route registration
- CORS middleware
- Health check endpoints

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check (simple) |
| GET | `/health` | Detailed system status |
| POST | `/upload` | Upload document for RAG |
| POST | `/ask` | Ask question about documents |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc documentation |

---

## 💾 Database Schema

### Table: documents
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    original_text TEXT NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Table: chunks
```sql
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    faiss_id VARCHAR(100) UNIQUE,
    created_at DATETIME
);
```

### Table: search_logs
```sql
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    result_count INTEGER DEFAULT 0,
    top_similarity FLOAT,
    response_time_ms INTEGER DEFAULT 0,
    created_at DATETIME
);
```

---

## ⚙️ Configuration Variables

### File Storage
```python
DATA_DIR          # Base data directory
UPLOADS_DIR       # Temporary upload storage
FAISS_INDEX_PATH  # Vector index file path
DATABASE_PATH     # SQLite database path
```

### Chunking
```python
CHUNK_SIZE        # 800 characters
CHUNK_OVERLAP     # 100 characters
```

### Embeddings
```python
EMBEDDINGS_MODEL        # text-embedding-3-small
EMBEDDINGS_BATCH_SIZE   # 100 texts per batch
FAISS_DIMENSION         # 1536 (OpenAI embedding size)
```

### Search
```python
TOP_K                   # 5 results per search
SIMILARITY_THRESHOLD    # 0.3 (optional filtering)
```

### LLM
```python
LLM_MODEL          # gpt-3.5-turbo
LLM_TEMPERATURE    # 0.7
MAX_CONTEXT_LENGTH # 4000 characters
```

### File Upload
```python
MAX_FILE_SIZE         # 50 MB
ALLOWED_FILE_TYPES    # ['pdf', 'txt', 'jpg', 'png', 'gif']
```

---

## 🚀 Running the Application

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="sk-..."

# Run server
python -m uvicorn app.main:app --reload
```

### Using run.py
```bash
python run.py
```

### Using Docker
```bash
docker-compose up
```

---

## 📝 Environment Variables (.env)

```env
# Required
OPENAI_API_KEY=sk_your_key_here

# Optional (defaults provided)
ENVIRONMENT=development|production
HOST=127.0.0.1
PORT=8000
```

---

## 📦 Dependencies

**Core:**
- fastapi, uvicorn, pydantic
- sqlalchemy (database ORM)
- faiss-cpu (vector search)
- numpy (numerical arrays)
- openai (LLM + embeddings)

**File Processing:**
- pypdf (PDF extraction)
- pytesseract (OCR)
- pillow (image processing)

**Dev/Util:**
- python-multipart (file uploads)
- python-dotenv (env variables)

---

## 🔐 Security Notes

- Store API keys in .env (never commit)
- Validate file uploads (size, type)
- Rate limit OpenAI API calls
- Sanitize database inputs (SQLAlchemy handles this)
- Add authentication for production

---

## 📈 Future Enhancements

- [ ] User authentication & multi-tenant support
- [ ] Advanced FAISS index types (IVFFlat, HNSW)
- [ ] Streaming responses
- [ ] Custom fine-tuned embeddings
- [ ] Support for more file types (DOCX, PPTX)
- [ ] Reranking with cross-encoders
- [ ] Conversation memory
- [ ] Document deletion/update
- [ ] Admin dashboard
- [ ] Prometheus metrics

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0  
**Status:** ✅ Ready for Development
