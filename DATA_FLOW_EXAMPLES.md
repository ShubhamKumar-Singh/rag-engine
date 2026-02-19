"""
COMPLETE DATA FLOW EXAMPLES
With actual data showing how FAISS + SQLite work together
"""

# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: FILE UPLOAD WITH REAL DATA
# ════════════════════════════════════════════════════════════════════════════

UPLOAD_EXAMPLE = """
USER UPLOADS: "research_paper.pdf"
─────────────────────────────────────────────────────────────────────────────

STEP 1: EXTRACT TEXT
  File: research_paper.pdf
  ├─ Size: 2MB
  └─ Extracted Text: "Quantum Computing Fundamentals...
     The quantum computer represents a paradigm shift in computing...
     ... [continued for 50,000 characters]"

STEP 2: CHUNK TEXT (800 char chunks, 100 char overlap)
  chunks = [
    "Quantum Computing Fundamentals...The quantum computer" (800 chars),
    "computer represents a paradigm shift...in computing" (800 chars),
    "shift in computing technology. Classical computers..." (800 chars),
    ... (12 more chunks, total: 15 chunks)
  ]

STEP 3: GENERATE EMBEDDINGS (using OpenAI API)
  embeddings = NumPy array (15, 1536)
  ├─ Chunk 0: [0.12, 0.45, 0.67, ..., 0.98]  (1536 floats)
  ├─ Chunk 1: [0.34, 0.21, 0.89, ..., 0.11]  (1536 floats)
  ├─ Chunk 2: [0.56, 0.78, 0.23, ..., 0.45]  (1536 floats)
  └─ ... (12 more embeddings)

STEP 4a: STORE IN FAISS (Vector Database)
  ─────────────────────────────────────────────────────────────────
  faiss_store.add_vectors(embeddings, doc_ids=["1_0", "1_1", ..., "1_14"])
  
  FAISS Index (data/vector.index):
  ├─ Vector Index 0: [0.12, 0.45, 0.67, ..., 0.98] → doc_id "1_0"
  ├─ Vector Index 1: [0.34, 0.21, 0.89, ..., 0.11] → doc_id "1_1"
  ├─ Vector Index 2: [0.56, 0.78, 0.23, ..., 0.45] → doc_id "1_2"
  └─ ... 12 more vectors mapped to doc_ids

STEP 4b: STORE IN SQLITE (Metadata Database)
  ─────────────────────────────────────────────────────────────────
  SQLite data/database.db
  
  documents TABLE:
  ┌─────┬──────────────────────┬──────────┬─────────────────────┬─────────┐
  │ id  │ file_name            │ file_type│ original_text       │ chunk_cnt
  ├─────┼──────────────────────┼──────────┼─────────────────────┼─────────┤
  │ 1   │ research_paper.pdf   │ pdf      │ "Quantum Computing..│ 15      │
  └─────┴──────────────────────┴──────────┴─────────────────────┴─────────┘
  
  chunks TABLE:
  ┌─────┬──────────────┬───────────┬──────────────────┬───────────┐
  │ id  │ document_id  │ chunk_idx │ faiss_id         │ chunk_text
  ├─────┼──────────────┼───────────┼──────────────────┼───────────┤
  │ 1   │ 1            │ 0         │ "0"              │ "Quantum Computing..."
  │ 2   │ 1            │ 1         │ "1"              │ "computer represents..."
  │ 3   │ 1            │ 2         │ "2"              │ "shift in computing..."
  │ ... │ 1            │ ...       │ ...              │ ...
  │ 15  │ 1            │ 14        │ "14"             │ "..."
  └─────┴──────────────┴───────────┴──────────────────┴───────────┘

RESULT:
  ✓ FAISS: 15 vectors stored, indexed, and searchable
  ✓ SQLite: 1 document + 15 chunks with full text
  ✓ Link: faiss_id column connects both databases
  ✓ API Response:
    {
      "success": true,
      "filename": "research_paper.pdf",
      "file_type": "pdf",
      "chunks_created": 15,
      "vectors_stored": 15
    }
"""

# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: USER ASKS QUESTION
# ════════════════════════════════════════════════════════════════════════════

QUERY_EXAMPLE = """
USER QUESTION: "What are the main applications of quantum computing?"
─────────────────────────────────────────────────────────────────────────────

STEP 1: EMBED QUESTION
  question_embedding = [0.23, 0.56, 0.78, ..., 0.34]  (1536 floats)
  
STEP 2: FAISS VECTOR SEARCH
  ─────────────────────────────────────────────────────────────────
  faiss_store.search(question_embedding, k=5)
  
  FAISS Index (data/vector.index) performs L2 similarity search:
  
  Distances:
  ├─ doc_id "1_3": distance = 0.12  (Most similar)
  ├─ doc_id "1_5": distance = 0.15
  ├─ doc_id "1_1": distance = 0.18
  ├─ doc_id "1_10": distance = 0.21
  └─ doc_id "1_8": distance = 0.24  (5th most similar)
  
  Results from FAISS:
  distances = [0.12, 0.15, 0.18, 0.21, 0.24]
  doc_ids = ["1_3", "1_5", "1_1", "1_10", "1_8"]

STEP 3: RETRIEVE TEXT FROM SQLITE
  ─────────────────────────────────────────────────────────────────
  For each doc_id, extract document_id and chunk_index:
  
  "1_3" → document_id=1, chunk_index=3
  "1_5" → document_id=1, chunk_index=5
  "1_1" → document_id=1, chunk_index=1
  "1_10" → document_id=1, chunk_index=10
  "1_8" → document_id=1, chunk_index=8
  
  SQL Queries:
  ├─ SELECT * FROM documents WHERE id = 1
  │  → Returns: {id: 1, file_name: "research_paper.pdf", ...}
  │
  └─ SELECT * FROM chunks WHERE document_id = 1 ORDER BY chunk_index
     → Returns: List of all 15 chunks
  
  Retrieved Chunks:
  chunk_index=3:  "Applications of quantum computing include cryptography..."
  chunk_index=5:  "drug discovery and optimization problems..."
  chunk_index=1:  "computer represents a paradigm shift in computing..."
  chunk_index=10: "financial modeling and machine learning..."
  chunk_index=8:  "quantum simulation for materials science..."

STEP 4: COMBINE CONTEXT
  ─────────────────────────────────────────────────────────────────
  context = """
  Applications of quantum computing include cryptography and secure
  communication. One major application involves drug discovery and
  optimization problems that are intractable on classical computers.
  
  The quantum computer represents a paradigm shift in computing
  architecture. Financial modeling and machine learning applications
  show promise for quantum acceleration.
  
  Quantum simulation for materials science is another key application,
  enabling researchers to study quantum phenomena directly.
  """

STEP 5: GENERATE ANSWER USING LLM
  ─────────────────────────────────────────────────────────────────
  Prompt to OpenAI:
  """
  Answer strictly from the context below:

  [context text from above]

  Question: What are the main applications of quantum computing?
  """
  
  LLM Response:
  "According to the documents, the main applications of quantum computing
   include: (1) Cryptography and secure communication, (2) Drug discovery
   and optimization problems, (3) Financial modeling and machine learning,
   and (4) Quantum simulation for materials science. These applications
   take advantage of quantum computers' ability to solve problems that are
   intractable on classical computers."

STEP 6: RETURN COMPLETE RESPONSE
  ─────────────────────────────────────────────────────────────────
  JSON Response:
  {
    "question": "What are the main applications of quantum computing?",
    "answer": "According to the documents, the main applications of...",
    "sources": [
      {
        "document": "research_paper.pdf",
        "chunk_index": 3,
        "text": "Applications of quantum computing include cryptography...",
        "similarity": 0.89  (converted from distance: 1/(1+0.12))
      },
      {
        "document": "research_paper.pdf",
        "chunk_index": 5,
        "text": "drug discovery and optimization problems...",
        "similarity": 0.87
      },
      {
        "document": "research_paper.pdf",
        "chunk_index": 1,
        "text": "computer represents a paradigm shift...",
        "similarity": 0.84
      },
      {
        "document": "research_paper.pdf",
        "chunk_index": 10,
        "text": "financial modeling and machine learning...",
        "similarity": 0.83
      },
      {
        "document": "research_paper.pdf",
        "chunk_index": 8,
        "text": "quantum simulation for materials science...",
        "similarity": 0.80
      }
    ],
    "response_time_ms": 1234.56
  }
"""

# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: MULTIPLE UPLOADS - Database State
# ════════════════════════════════════════════════════════════════════════════

MULTIPLE_UPLOADS_EXAMPLE = """
SCENARIO: User uploads 3 different documents
─────────────────────────────────────────────────────────────────────────────

UPLOAD 1: machine_learning.pdf (12 chunks)
UPLOAD 2: deep_learning.txt (18 chunks)
UPLOAD 3: ai_overview.pdf (10 chunks)

Result: Total 40 chunks across 3 documents

FAISS Vector Index (data/vector.index):
─────────────────────────────────────────────────────────────────────────────
Vector Count: 40
ID Mapping:
  ├─ Index 0-11: "1_0" to "1_11" → machine_learning.pdf chunks
  ├─ Index 12-29: "2_0" to "2_17" → deep_learning.txt chunks
  └─ Index 30-39: "3_0" to "3_9" → ai_overview.pdf chunks

SQLite Database (data/database.db):
─────────────────────────────────────────────────────────────────────────────

documents TABLE:
┌────┬──────────────────────┬──────────┬────────────────────┬────────────┐
│ id │ file_name            │ file_type│ original_text      │ chunk_count│
├────┼──────────────────────┼──────────┼────────────────────┼────────────┤
│ 1  │ machine_learning.pdf │ pdf      │ "Machine Learning..│ 12         │
│ 2  │ deep_learning.txt    │ txt      │ "Deep Learning..   │ 18         │
│ 3  │ ai_overview.pdf      │ pdf      │ "AI Overview sys.. │ 10         │
└────┴──────────────────────┴──────────┴────────────────────┴────────────┘

chunks TABLE (showing first & last row per document):
┌────┬──────────────┬───────────┬────────────────────┬────────────┐
│ id │ document_id  │ chunk_idx │ chunk_text         │ faiss_id   │
├────┼──────────────┼───────────┼────────────────────┼────────────┤
│ 1  │ 1            │ 0         │ "Machine Learning..│ "0"        │
│ 2  │ 1            │ 1         │ "supervised and..  │ "1"        │
│ ...│ 1            │ ...       │ ...                │ ...        │
│ 12 │ 1            │ 11        │ "future of ML.."   │ "11"       │
│ 13 │ 2            │ 0         │ "Deep Learning is..│ "12"       │
│ 14 │ 2            │ 1         │ "neural networks.  │ "13"       │
│ ...│ 2            │ ...       │ ...                │ ...        │
│ 30 │ 2            │ 17        │ "applications..    │ "29"       │
│ 31 │ 3            │ 0         │ "AI Overview sys.. │ "30"       │
│ 32 │ 3            │ 1         │ "various domains.. │ "31"       │
│ ...│ 3            │ ...       │ ...                │ ...        │
│ 40 │ 3            │ 9         │ "the future of AI..│ "39"       │
└────┴──────────────┴───────────┴────────────────────┴────────────┘

QUERY ACROSS ALL DOCUMENTS:
Question: "How does machine learning differ from deep learning?"

FAISS Search Results (L2 distance):
├─ Index 0 (faiss_id "0"): doc_id "1_0", similarity 0.91
├─ Index 13 (faiss_id "13"): doc_id "2_1", similarity 0.89
├─ Index 1 (faiss_id "1"): doc_id "1_1", similarity 0.87
├─ Index 31 (faiss_id "31"): doc_id "3_1", similarity 0.85
└─ Index 15 (faiss_id "15"): doc_id "2_3", similarity 0.83

SQLite Retrieval:
├─ Document 1 (machine_learning.pdf): chunk 0 + chunk 1
├─ Document 2 (deep_learning.txt): chunk 1 + chunk 3
└─ Document 3 (ai_overview.pdf): chunk 1

Response includes sources from all 3 documents!
"""

# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: DATABASE QUERIES
# ════════════════════════════════════════════════════════════════════════════

DATABASE_QUERIES_EXAMPLE = """
COMMON QUERIES AND HOW THEY WORK:
─────────────────────────────────────────────────────────────────────────────

QUERY 1: Count total documents
  Python: db.query(Document).count()
  SQL: SELECT COUNT(*) FROM documents
  Result: 3

QUERY 2: Get all chunks for a document
  Python: db.query(Chunk).filter(Chunk.document_id == 1).all()
  SQL: SELECT * FROM chunks WHERE document_id = 1 ORDER BY chunk_index
  Result: 12 rows (all chunks from machine_learning.pdf)

QUERY 3: Get specific chunk text
  Python:
    chunk = db.query(Chunk).filter(
        Chunk.document_id == 1,
        Chunk.chunk_index == 3
    ).first()
  SQL: SELECT * FROM chunks WHERE document_id = 1 AND chunk_index = 3
  Result: One chunk row with text, faiss_id, etc.

QUERY 4: Get document by filename
  Python: db.query(Document).filter(Document.file_name == "ml.pdf").first()
  SQL: SELECT * FROM documents WHERE file_name = "ml.pdf"
  Result: One document row with id=1

QUERY 5: Count total chunks
  Python: db.query(Chunk).count()
  SQL: SELECT COUNT(*) FROM chunks
  Result: 40

QUERY 6: List all documents with chunk counts
  Python:
    docs = db.query(Document).all()
    for doc in docs:
        print(f"{doc.file_name}: {doc.chunk_count} chunks")
  Result:
    machine_learning.pdf: 12 chunks
    deep_learning.txt: 18 chunks
    ai_overview.pdf: 10 chunks

QUERY 7: Delete document and all its chunks (if needed)
  Python:
    doc = db.query(Document).filter(Document.id == 1).first()
    chunks = db.query(Chunk).filter(Chunk.document_id == 1).all()
    for chunk in chunks:
        db.delete(chunk)
    db.delete(doc)
    db.commit()
  SQL: Would execute DELETE on both tables with CASCADE
"""

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY: Data Flow Diagram
# ════════════════════════════════════════════════════════════════════════════

SUMMARY = """
COMPLETE DATA FLOW SUMMARY:
─────────────────────────────────────────────────────────────────────────────

INPUT                          PROCESSING                    STORAGE
─────────────────────────────────────────────────────────────────────────────

Upload Flow:
  User File
      ↓
  Extract Text
      ↓
  Chunk Text (800 chars)
      ├───→ Generate Embeddings (OpenAI)
      │         ↓
      │     (numpy array)
      │         ↓
      ├───→ STORE IN FAISS ──────→ data/vector.index
      │     (vector index)
      │
      └───→ STORE IN SQLITE ──────→ data/database.db
          (text + metadata)

Query Flow:
  User Question
      ↓
  Generate Question Embedding (OpenAI)
      ↓
  Search FAISS for similar vectors ──→ Get doc_ids + distances
      ↓
  Fetch text from SQLite
      ├─ Query documents table
      └─ Query chunks table
      ↓
  Combine context
      ↓
  Generate Answer (OpenAI LLM)
      ↓
  Return Response with sources


KEY INTEGRATION POINTS:
─────────────────────────────────────────────────────────────────────────────

1. UPLOAD INTEGRATION
   ├─ Both stores updated in same operation
   ├─ FAISS IDs linked to SQLite via faiss_id column
   ├─ Both committed together
   └─ On failure, both rolled back

2. QUERY INTEGRATION
   ├─ FAISS provides fast vector search
   ├─ SQLite provides content retrieval
   ├─ Combined results for complete response
   └─ Similarity scores from FAISS distances

3. ID MANAGEMENT
   ├─ SQLite chunk.faiss_id = FAISS vector ID
   ├─ Enables linking back from search results
   ├─ Maintains referential integrity
   └─ Supports future delete/update operations


DATABASE STATISTICS (After 3 uploads):
─────────────────────────────────────────────────────────────────────────────

FAISS Index:
  ├─ Vectors: 40
  ├─ Dimensions: 1536
  ├─ Index Type: IndexFlatL2
  ├─ File Size: ~500 KB (15 vectors × 1536 × 4 bytes)
  └─ Search Time: <10ms for top-5

SQLite Database:
  ├─ Tables: 3 (documents, chunks, search_logs)
  ├─ Documents: 3 rows
  ├─ Chunks: 40 rows
  ├─ Relationships: chunks.document_id → documents.id
  ├─ File Size: ~100 KB (mostly text storage)
  └─ Query Time: <5ms for chunk retrieval
"""

if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPLETE DATA FLOW EXAMPLES")
    print("="*80 + "\n")
    
    print(UPLOAD_EXAMPLE)
    print("\n" + "="*80 + "\n")
    
    print(QUERY_EXAMPLE)
    print("\n" + "="*80 + "\n")
    
    print(MULTIPLE_UPLOADS_EXAMPLE)
    print("\n" + "="*80 + "\n")
    
    print(DATABASE_QUERIES_EXAMPLE)
    print("\n" + "="*80 + "\n")
    
    print(SUMMARY)
    print("\n" + "="*80 + "\n")
