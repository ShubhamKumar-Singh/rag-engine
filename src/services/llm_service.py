import re
from typing import Dict, Any
from app.core.logging_config import logger

def extract_filters(query: str) -> Dict[str, Any]:
    """Extract simple filters from user query using regex heuristics.

    Returns a dict with possible keys: price_max, price_min, brand, ram, category
    """
    q = query.lower()
    filters = {}

    # price: under/below/less than
    m = re.search(r"(?:under|below|less than)\s+(?:rs\.?\s*)?(\d{2,7})", q)
    if m:
        try:
            filters["price_max"] = float(m.group(1))
        except Exception:
            pass

    # price: between X and Y
    m = re.search(r"(?:between)\s+(?:rs\.?\s*)?(\d{2,7})\s*(?:and|-)\s*(?:rs\.?\s*)?(\d{2,7})", q)
    if m:
        try:
            filters["price_min"] = float(m.group(1))
            filters["price_max"] = float(m.group(2))
        except Exception:
            pass

    # price: exactly numbers like 'under 3000' or '3000 se kam'
    m = re.search(r"(\d{2,7})\s*(?:rupees|rs|rs\.|inr)?", q)
    # if no explicit under/above, interpret presence of number as max budget sometimes
    if m and "under" in q or "below" in q or "kam" in q:
        try:
            filters.setdefault("price_max", float(m.group(1)))
        except Exception:
            pass

    # RAM extraction like 8GB, 4 GB
    m = re.search(r"(\d{1,2})\s*gb", q)
    if m:
        try:
            filters["ram_gb"] = int(m.group(1))
        except Exception:
            pass

    # brand heuristics - look for 'apple', 'samsung', 'nike', 'adidas' etc.
    brands = ["apple", "samsung", "xiaomi", "oneplus", "nike", "adidas", "puma"]
    for b in brands:
        if b in q:
            filters["brand"] = b
            break

    # category hints
    cats = ["phone", "phones", "laptop", "laptops", "shoe", "shoes", "clothes", "shirt", "pant"]
    for c in cats:
        if c in q:
            filters["category"] = c
            break

    logger.info(f"Extracted filters from query: {filters}")
    return filters
