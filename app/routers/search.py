from typing import List
from fastapi import APIRouter, Depends
from app.models import (
    VectorSearchRequest, VectorSearchResult,
    GraphTraversalResponse,
    HybridSearchRequest, HybridSearchResult
)
from app.service import HybridRetrievalService
from app.dependencies import get_service

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/vector", response_model=List[VectorSearchResult])
def vector_search(request: VectorSearchRequest, service: HybridRetrievalService = Depends(get_service)):
    return service.vector_search(request.query_text, request.top_k)

@router.get("/graph", response_model=GraphTraversalResponse)
def graph_traversal(start_id: str, depth: int = 2, service: HybridRetrievalService = Depends(get_service)):
    # Note: GET request parameters are used here instead of body as per typical GET convention,
    # but the prompt example showed GET with query params: /search/graph?start_id=...
    return service.graph_traversal(start_id, depth)

@router.post("/hybrid", response_model=List[HybridSearchResult])
def hybrid_search(request: HybridSearchRequest, service: HybridRetrievalService = Depends(get_service)):
    return service.hybrid_search(
        request.query_text,
        request.vector_weight,
        request.graph_weight,
        request.top_k
    )
