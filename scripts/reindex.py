"""Rebuild FAISS index from documents stored in the database.

Usage:
    python -m scripts.reindex
"""
from pathlib import Path
from app.db.database import SessionLocal
from app.db.models import Document, Chunk
from app.services.chunking import chunk_text
from app.services.embedding import get_embedding_service
from app.services.faiss_store import get_faiss_store
from app.core.config import FAISS_INDEX_PATH
from app.core.logging_config import logger


def rebuild_index():
    db = SessionLocal()
    try:
        # Remove existing index file if present
        if Path(FAISS_INDEX_PATH).exists():
            try:
                Path(FAISS_INDEX_PATH).unlink()
                logger.info(f"Deleted existing FAISS index at {FAISS_INDEX_PATH}")
            except Exception as e:
                logger.warning(f"Could not delete FAISS index file: {e}")

        # Initialize fresh FAISS store
        faiss_store = get_faiss_store()
        faiss_store.create_index()

        # Clear existing chunks in DB
        deleted = db.query(Chunk).delete()
        db.commit()
        logger.info(f"Cleared {deleted} existing chunk records from DB")

        # Reprocess documents
        documents = db.query(Document).order_by(Document.id).all()
        embedder = get_embedding_service()

        total_vectors = 0
        for doc in documents:
            try:
                chunks = chunk_text(doc.original_text)
                if not chunks:
                    continue

                embeddings = embedder.get_embeddings_as_numpy(chunks)
                chunk_doc_ids = [f"{doc.id}_{i}" for i in range(len(chunks))]
                faiss_ids = faiss_store.add_vectors(embeddings, chunk_doc_ids)

                # Store chunks
                for i, faiss_id in enumerate(faiss_ids):
                    chunk = Chunk(
                        document_id=doc.id,
                        chunk_index=i,
                        chunk_text=chunks[i],
                        faiss_id=str(faiss_id)
                    )
                    db.add(chunk)

                doc.chunk_count = len(chunks)
                db.commit()
                total_vectors += len(faiss_ids)
                logger.info(f"Reindexed document id={doc.id}: {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"Error reindexing document id={doc.id}: {e}")
                db.rollback()

        # Save FAISS index to disk
        faiss_store.save_index()
        logger.info(f"Reindex complete. Total vectors indexed: {total_vectors}")

    finally:
        db.close()


if __name__ == "__main__":
    rebuild_index()
