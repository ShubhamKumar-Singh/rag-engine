"""Simple product generator to create many sample products for testing."""
import json
from pathlib import Path
from random import randint, choice

brands = ["Alpha", "Beta", "Gamma", "Delta", "FastFeet", "Basics"]
categories = [
    ("electronics", "phones"),
    ("electronics", "laptops"),
    ("footwear", None),
    ("clothes", None)
]

def generate(n=200, out_path: Path = Path("src/data/products.json")):
    data = {}
    for i in range(n):
        cat, sub = choice(categories)
        prod = {
            "id": f"g{i+1000}",
            "name": f"Product {i+1}",
            "price": randint(299, 99999),
            "brand": choice(brands),
            "description": "Automatically generated sample product",
            "specifications": {"ram": choice(["4GB","8GB","16GB","32GB"]) }
        }
        if sub:
            data.setdefault(cat, {}).setdefault(sub, []).append(prod)
        else:
            data.setdefault(cat, []).append(prod)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {n} products to {out_path}")


if __name__ == "__main__":
    generate(300)
