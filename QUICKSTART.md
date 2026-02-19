# 🚀 RAG Engine - Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Windows users (for OCR support):
```bash
# Download Tesseract installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
# Or use scoop: scoop install tesseract
```

## Step 2: Configure Environment

Create `.env` file:
```env
OPENAI_API_KEY=sk_your_api_key_here
ENVIRONMENT=development
```

Get your OpenAI API key: https://platform.openai.com/api-keys

## Step 3: Run Startup Check

```bash
python startup_check.py
```

Should show all ✅ checks passing.

## Step 4: Start the Server

### Option A: Using uvicorn directly
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Option B: Using run.py
```bash
python run.py
```

### Option C: Using Docker
```bash
docker-compose up
```

## Step 5: Test the API

### Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

### Test in Swagger:
1. Click **POST /upload**
2. Click **"Try it out"**
3. Select a PDF/TXT/image file
4. Click **Execute**

Expected response:
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

### Test Query Endpoint:
1. Click **POST /ask**
2. Click **"Try it out"**
3. Enter: `{"question": "What is the main topic?", "top_k": 5}`
4. Click **Execute**

Expected response:
```json
{
  "question": "What is the main topic?",
  "answer": "Based on the documents, the main topic is...",
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

## Test with cURL

### Upload a file:
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"
```

### Ask a question:
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key points?",
    "top_k": 5
  }'
```

### Check health:
```bash
curl http://127.0.0.1:8000/health
```

## 📁 Key Files to Know

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/api/upload_routes.py` | Upload endpoint |
| `app/api/query_routes.py` | Query endpoint |
| `app/services/` | Business logic |
| `app/core/config.py` | Configuration |
| `data/database.db` | SQLite database (auto-created) |
| `data/vector.index` | FAISS index (auto-created) |
| `README.md` | Full documentation |
| `PROJECT_STRUCTURE.md` | Detailed architecture |

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'openai'"
```bash
pip install -r requirements.txt
```

### Error: "OPENAI_API_KEY not set"
```bash
# Windows PowerShell:
$env:OPENAI_API_KEY = "sk_your_key"

# Windows cmd:
set OPENAI_API_KEY=sk_your_key

# Linux/Mac:
export OPENAI_API_KEY="sk_your_key"
```

### Error: "pytesseract.TesseractNotFoundError"
Install Tesseract OCR:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

Then set path in config if needed.

### Port 8000 already in use
```bash
python -m uvicorn app.main:app --port 8001
```

### Database errors
Delete existing database:
```bash
rm data/database.db  # Linux/Mac
del data\database.db  # Windows
```

It will be recreated automatically.

## 📖 Next Steps

1. Read [README.md](README.md) for comprehensive documentation
2. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
3. Explore the code in `app/services/` folder
4. Try different file types (PDF, images, plain text)
5. Experiment with different questions
6. Check logs in `data/logs/rag_engine.log`

## 💡 Tips

- Keep chunk size 500-1000 characters for better accuracy
- Use top_k=5 for most queries (adjust if needed)
- Monitor API usage to control costs
- Check `data/logs/rag_engine.log` for debugging
- Use Swagger UI (`/docs`) for easy testing

## 🎓 Learning Path

1. **Basic**: Upload a PDF and ask a simple question
2. **Intermediate**: Upload multiple documents and ask comparative questions
3. **Advanced**: Experiment with chunk sizes, embeddings, and different LLM models
4. **Production**: Deploy with Docker, add authentication, setup monitoring

---

**Happy RAG Engineering! 🎉**

For issues and support, check the README.md or review logs in `data/logs/`
