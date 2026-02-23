from typing import List, Dict, Any
from src.services.llm_service import extract_filters
from src.services.embedding_service import get_embedding_service
from src.services.vector_store_service import get_vector_store
from app.core.logging_config import logger
from src.config import settings


def search_products(query: str, top_k: int = None) -> Dict[str, Any]:
    top_k = top_k or settings.TOP_K

    filters = extract_filters(query)

    emb_service = get_embedding_service()
    vec_store = get_vector_store()

    q_emb = emb_service.embed_texts([query])[0]

    distances, results = vec_store.search(q_emb, k=top_k)

    # Convert distances to score (higher is better)
    recs: List[Dict[str, Any]] = []
    for dist, prod in zip(distances, results):
        if not prod:
            continue
        score = 1 / (1 + dist)

        # Apply simple post-filters
        if "price_max" in filters and prod.get("price") is not None:
            if prod.get("price") > filters["price_max"]:
                continue
        if "brand" in filters and prod.get("brand"):
            if filters["brand"] != prod.get("brand").lower():
                continue
        if "ram_gb" in filters and prod.get("specifications"):
            ram = prod.get("specifications", {}).get("ram")
            try:
                if ram and int(str(ram).replace("GB", "").strip()) < filters["ram_gb"]:
                    continue
            except Exception:
                pass

        recs.append({
            "id": prod.get("id"),
            "name": prod.get("name"),
            "price": prod.get("price"),
            "category": prod.get("category"),
            "score": float(score)
        })

    # sort by score
    recs = sorted(recs, key=lambda r: r["score"], reverse=True)[:top_k]

    return {
        "query": query,
        "filters_applied": filters,
        "recommendations": recs
    }
