from pathlib import Path
from typing import List, Dict, Any
from app.core.logging_config import logger
from src.config import settings
import hashlib


def load_products(path: Path = None) -> List[Dict[str, Any]]:
    """Load and flatten products from the JSON file.

    Supports a nested structure (category -> subcategory -> list of products).
    Each product will be normalized to contain required fields.
    """
    import json

    p = path or settings.PRODUCTS_JSON
    if not p.exists():
        logger.warning(f"Products JSON not found: {p}")
        return []

    with open(p, "r", encoding="utf-8") as f:
        raw = json.load(f)

    products: List[Dict[str, Any]] = []

    def _flatten(category: str, node: Any):
        if isinstance(node, dict):
            # keys may be subcategories
            for k, v in node.items():
                _flatten(category if category else k, v)
        elif isinstance(node, list):
            for item in node:
                # Normalize product
                prod = {
                    "id": str(item.get("id") or item.get("sku") or item.get("name")),
                    "name": item.get("name", ""),
                    "category": category or item.get("category", ""),
                    "subcategory": item.get("subcategory"),
                    "price": float(item.get("price")) if item.get("price") is not None else None,
                    "description": item.get("description"),
                    "brand": item.get("brand"),
                    "specifications": item.get("specifications", {})
                }

                # Deterministic embedding hash: model version + important text fields
                hash_src = f"{settings.MODEL_VERSION}|{prod.get('name','')}|{prod.get('description','')}|{prod.get('brand','')}"
                prod_hash = hashlib.sha256(hash_src.encode("utf-8")).hexdigest()
                prod["embedding_hash"] = prod_hash

                products.append(prod)
        else:
            logger.debug("Unexpected node type in products JSON")

    # top-level categories
    if isinstance(raw, dict):
        for cat, node in raw.items():
            _flatten(cat, node)
    else:
        logger.warning("Products JSON root is not an object")

    logger.info(f"Loaded {len(products)} products from {p}")
    return products
