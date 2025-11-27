from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ==================== Node Models ====================

class NodeCreate(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    auto_embed: bool = True

class NodeResponse(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding_created: Optional[bool] = None
    relationships: Optional[List[Dict[str, Any]]] = None

class NodeUpdate(BaseModel):
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    regenerate_embedding: bool = False

class NodeUpdateResponse(BaseModel):
    status: str
    id: str
    embedding_regenerated: bool

class NodeDeleteResponse(BaseModel):
    status: str
    id: str
    edges_removed: int

# ==================== Edge Models ====================

class EdgeCreate(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 1.0

class EdgeResponse(BaseModel):
    status: Optional[str] = None
    edge_id: str
    source: str
    target: str
    type: str
    weight: Optional[float] = None # Added for Get Relationship response which includes weight but not status

class EdgeDeleteResponse(BaseModel):
    status: str
    id: str

# ==================== Search Models ====================

class VectorSearchRequest(BaseModel):
    query_text: str
    top_k: int = 5

class VectorSearchResult(BaseModel):
    node_id: str
    text: str
    cosine_similarity: float
    metadata: Dict[str, Any]

class GraphTraversalResultItem(BaseModel):
    node_id: str
    depth: int

class GraphTraversalResponse(BaseModel):
    start: str
    depth: int
    results: List[GraphTraversalResultItem]

class HybridSearchRequest(BaseModel):
    query_text: str
    vector_weight: float = 0.7
    graph_weight: float = 0.3
    top_k: int = 5

class HybridSearchResult(BaseModel):
    node_id: str
    text: str
    cosine_similarity: float
    graph_score: float
    final_score: float
    metadata: Dict[str, Any]
