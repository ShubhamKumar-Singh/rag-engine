# 🚀 RAG Engine - Retrieval-Augmented Generation System

A production-ready RAG (Retrieval-Augmented Generation) engine built with FastAPI, FAISS, and OpenAI. Upload documents and ask questions to get intelligent answers based on your data.

## 🎯 Features

✅ **Multi-Format Support**: PDF, TXT, JPG, PNG, GIF  
✅ **Intelligent Text Extraction**: Automatic OCR for images, PDF parsing  
✅ **Smart Chunking**: Overlapping text chunks for better context  
✅ **Vector Embeddings**: OpenAI embeddings for semantic search  
✅ **FAISS Integration**: Fast similarity search  
✅ **SQLite Metadata**: Store document metadata and chunk references  
✅ **LLM Integration**: GPT-powered answer generation  
✅ **Production Ready**: Logging, error handling, CORS support  

---

## 📋 Requirements

- Python 3.10+
- OpenAI API Key
- Tesseract OCR (for image processing)

---

## ⚙️ Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install System Dependencies (Optional - for OCR)

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use scoop: scoop install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 4. Setup Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
ENVIRONMENT=development
```

---

## 🚀 Quick Start

### 1. Start the Server

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Access the API

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

---

## 📚 API Endpoints

### 1. Upload Document

**POST** `/upload`

Upload a document for RAG processing.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_type": "pdf",
  "message": "Successfully processed document.pdf",
  "chunks_created": 15,
  "vectors_stored": 15
}
```

### 2. Ask Question

**POST** `/ask`

Ask a question about the uploaded documents.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "question": "What is the main topic?",
  "answer": "The main topic is...",
  "sources": [
    {
      "document": "document.pdf",
      "chunk_index": 0,
      "text": "...",
      "similarity": 0.92
    }
  ],
  "response_time_ms": 1234.5
}
```

### 3. Health Check

**GET** `/health`

Get system status and statistics.

**Response:**
```json
{
  "status": "healthy",
  "database": "initialized",
  "faiss": {
    "total_vectors": 45,
    "dimension": 1536,
    "index_type": "IndexFlatL2"
  },
  "embeddings_configured": true,
  "openai_configured": true
}
```

---

## 📁 Project Structure

```
rag-engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── upload_routes.py    # File upload endpoints
│   │   └── query_routes.py     # Question/answer endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration & settings
│   │   └── logging_config.py   # Logging setup
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite connection
│   │   └── models.py           # Database models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic request/response models
│   │
│   └── services/
│       ├── __init__.py
│       ├── chunking.py         # Text chunking logic
│       ├── embedding.py        # OpenAI embeddings
│       ├── faiss_store.py      # FAISS vector store
│       ├── file_extraction.py  # PDF/image/text extraction
│       └── operations.py       # Upload & query logic
│
├── data/
│   ├── uploads/                # Uploaded files (temp)
│   ├── logs/                   # Application logs
│   ├── vector.index            # FAISS index file
│   └── database.db             # SQLite database
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create locally)
└── README.md                   # This file
```

---

## ⚙️ Configuration

Edit `app/core/config.py` to customize:

```python
# Chunking
CHUNK_SIZE = 800  # Characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks

# Search
TOP_K = 5  # Number of similar chunks to retrieve

# LLM
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7
MAX_CONTEXT_LENGTH = 4000

# Embeddings
EMBEDDINGS_MODEL = "text-embedding-3-small"
FAISS_DIMENSION = 1536
```

---

## 🔄 How It Works

### Upload Flow

```
File Upload
    ↓
Text Extraction (PDF/OCR/TXT)
    ↓
Text Cleaning & Normalization
    ↓
Text Chunking (800 chars, 100 overlap)
    ↓
Embedding Generation (OpenAI)
    ↓
Store in FAISS Index
    ↓
Store Metadata in SQLite
    ↓
Save Index to Disk
```

### Query Flow

```
User Question
    ↓
Generate Embedding (OpenAI)
    ↓
FAISS Similarity Search (Top 5)
    ↓
Retrieve Chunk Text from SQLite
    ↓
Combine Retrieved Chunks
    ↓
Generate Answer with LLM (GPT-3.5)
    ↓
Return Answer + Sources
```

---

## 🔒 Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    original_text TEXT,
    chunk_count INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Chunks Table
```sql
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    chunk_index INTEGER,
    chunk_text TEXT,
    token_count INTEGER,
    faiss_id VARCHAR(100),
    created_at DATETIME
);
```

### Search Logs Table
```sql
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY,
    query TEXT,
    result_count INTEGER,
    top_similarity FLOAT,
    response_time_ms INTEGER,
    created_at DATETIME
);
```

---

## 🐛 Troubleshooting

### 1. "OPENAI_API_KEY not set"
- Create `.env` file with `OPENAI_API_KEY=your_key`
- Or set environment variable: `export OPENAI_API_KEY=your_key`

### 2. "No module named 'pytesseract'"
- Install: `pip install pytesseract`
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

### 3. "FAISS index is empty"
- Upload documents first using the `/upload` endpoint
- Check database with: `sqlite3 data/database.db`

### 4. "OpenAI API rate limit exceeded"
- Implement retry logic (add to `embedding.py`)
- Use batch processing for embeddings

---

## 📈 Performance Tips

1. **Batch Embeddings**: Process multiple chunks together
2. **Adjust CHUNK_SIZE**: Larger chunks = faster search, less context
3. **FAISS Optimization**: Use IVFFlat for 100K+ vectors
4. **Caching**: Cache question embeddings for repeated queries
5. **Database Indexing**: Add indexes on frequently searched columns

---

## 🔐 Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Setup monitoring & alerts
- [ ] Regular database backups
- [ ] Load balancing (multiple workers)
- [ ] Docker containerization

---

## 📝 Example Workflow

```bash
# 1. Start server
python -m uvicorn app.main:app --reload

# 2. Upload a document
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@research_paper.pdf"

# 3. Ask a question
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?"}'

# 4. Check health
curl http://127.0.0.1:8000/health
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review logs in `data/logs/rag_engine.log`
3. Check OpenAI API status
4. Verify all dependencies are installed

---

## 🚀 Next Steps

- [ ] Add user authentication
- [ ] Implement document deletion
- [ ] Add advanced search filters
- [ ] Support for more file types (DOCX, PPTX)
- [ ] Streaming responses
- [ ] Multi-language support
- [ ] Fine-tuned embeddings
- [ ] Custom LLM models

---

**Happy RAG Engineering! 🎉**
