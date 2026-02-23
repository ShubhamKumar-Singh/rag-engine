"""Prepare training data for embedding fine-tuning.

Generates simple positive pairs by treating each product as a positive
example for queries that mention its brand/category/specs. This is a
small helper; for real training you should collect user queries and
relevance labels.
"""
import json
from pathlib import Path
from src.services.json_loader import load_products


def prepare_pairs(out_path: Path = Path("data/train_pairs.jsonl")):
    products = load_products()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for p in products:
            # simple synthetic query examples
            queries = [
                f"{p.get('brand','')} {p.get('name','')}",
                f"{p.get('name','')} with {p.get('specifications',{}).get('ram','')} RAM",
                f"{p.get('category','')} {p.get('subcategory','') or ''} under {int(p.get('price') or 10000)}"
            ]
            for q in queries:
                obj = {"query": q, "positive_id": p.get("id")}
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    prepare_pairs()
