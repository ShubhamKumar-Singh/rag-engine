from fastapi import FastAPI
from pydantic import BaseModel
from src.services.json_loader import load_products
from src.services.embedding_service import get_embedding_service
from src.services.vector_store_service import get_vector_store
from src.services.search_service import search_products
from src.config import settings
from app.core.logging_config import logger

app = FastAPI(title="Product Recommender (Refactored)")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.on_event("startup")
def startup():
    # Load and index products if needed
    products = load_products(settings.PRODUCTS_JSON)
    if not products:
        logger.warning("No products found to index on startup")
        return

    emb = get_embedding_service()
    store = get_vector_store()

    # Determine which products are already present in metadata to avoid re-embedding
    existing_ids = {v.get("id") for v in store.metadata.values()}
    to_index = [p for p in products if p.get("id") not in existing_ids]

    if not to_index:
        logger.info("No new products to index")
        return

    texts = [f"{p.get('name')} {p.get('description') or ''} {p.get('brand') or ''}" for p in to_index]
    embeddings = emb.embed_texts(texts)
    store.add_products(to_index, embeddings)
    store.save()
    logger.info(f"Indexed {len(to_index)} new products on startup")


@app.post("/search")
def api_search(req: SearchRequest):
    return search_products(req.query, req.top_k)
