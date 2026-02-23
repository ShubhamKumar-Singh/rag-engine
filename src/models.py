from pydantic import BaseModel
from typing import Any, Dict, Optional


class Product(BaseModel):
    id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class Recommendation(BaseModel):
    id: str
    name: str
    price: Optional[float]
    category: str
    score: float


class SearchResponse(BaseModel):
    query: str
    filters_applied: Dict[str, Any]
    recommendations: list[Recommendation]
