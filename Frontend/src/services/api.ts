import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Node {
  id: string
  text: string
  metadata: Record<string, any>
  embedding_created?: boolean
  relationships?: Relationship[]
}

export interface Relationship {
  target: string
  type: string
  weight?: number
}

export interface NodeCreate {
  text: string
  metadata?: Record<string, any>
  auto_embed?: boolean
}

export interface NodeUpdate {
  text?: string
  metadata?: Record<string, any>
  regenerate_embedding?: boolean
}

export interface Edge {
  edge_id: string
  source: string
  target: string
  type: string
  weight?: number
  status?: string
}

export interface EdgeCreate {
  source: string
  target: string
  type: string
  weight?: number
}

export interface VectorSearchRequest {
  query_text: string
  top_k: number
}

export interface VectorSearchResult {
  node_id: string
  text: string
  cosine_similarity: number
  metadata: Record<string, any>
}

export interface GraphTraversalResponse {
  start: string
  depth: number
  results: Array<{
    node_id: string
    depth: number
  }>
}

export interface HybridSearchRequest {
  query_text: string
  vector_weight?: number
  graph_weight?: number
  top_k?: number
}

export interface HybridSearchResult {
  node_id: string
  text: string
  cosine_similarity: number
  graph_score: number
  final_score: number
  metadata: Record<string, any>
}

// Node APIs
export const nodeApi = {
  create: (data: NodeCreate) => api.post<Node>('/nodes', data),
  get: (id: string) => api.get<Node>(`/nodes/${id}`),
  update: (id: string, data: NodeUpdate) => api.put(`/nodes/${id}`, data),
  delete: (id: string) => api.delete(`/nodes/${id}`),
}

// Edge APIs
export const edgeApi = {
  create: (data: EdgeCreate) => api.post<Edge>('/edges', data),
  get: (id: string) => api.get<Edge>(`/edges/${id}`),
  delete: (id: string) => api.delete(`/edges/${id}`),
}

// Search APIs
export const searchApi = {
  vector: (data: VectorSearchRequest) => api.post<VectorSearchResult[]>('/search/vector', data),
  graph: (startId: string, depth: number = 2) => 
    api.get<GraphTraversalResponse>(`/search/graph?start_id=${startId}&depth=${depth}`),
  hybrid: (data: HybridSearchRequest) => api.post<HybridSearchResult[]>('/search/hybrid', data),
}

// PDF API
export const pdfApi = {
  upload: (file: File, query: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('query', query)
    return api.post<HybridSearchResult>('/pdf/search', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export default api

