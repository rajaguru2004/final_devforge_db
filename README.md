# Hybrid Retrieval System

A production-ready backend service using **FastAPI**, **ChromaDB**, and **NetworkX** for hybrid vector + graph retrieval.

## Features

- **Node CRUD**: Create, Read, Update, Delete nodes with automatic vector embedding.
- **Edge CRUD**: Manage relationships between nodes.
- **Vector Search**: Search nodes using cosine similarity.
- **Graph Traversal**: BFS traversal to find connected nodes.
- **Hybrid Search**: Combine vector similarity and graph connectivity scores.

## Setup

1. **Install Dependencies**:
   ```bash
   poetry install
   ```

2. **Run the Server**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.
   Interactive docs: `http://localhost:8000/docs`.

## API Endpoints & cURL Commands

### 1. Create Node
```bash
curl -X POST "http://localhost:8000/nodes" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Machine learning is a subset of AI.",
           "metadata": { "source": "doc1" },
           "auto_embed": true
         }'
```

### 2. Get Node
```bash
curl "http://localhost:8000/nodes/{node_id}"
```

### 3. Update Node
```bash
curl -X PUT "http://localhost:8000/nodes/{node_id}" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Updated content",
           "metadata": { "source": "updated_doc" },
           "regenerate_embedding": true
         }'
```

### 4. Delete Node
```bash
curl -X DELETE "http://localhost:8000/nodes/{node_id}"
```

### 5. Create Relationship (Edge)
```bash
curl -X POST "http://localhost:8000/edges" \
     -H "Content-Type: application/json" \
     -d '{
           "source": "{source_node_id}",
           "target": "{target_node_id}",
           "type": "related_to",
           "weight": 0.9
         }'
```

### 6. Get Relationship
```bash
curl "http://localhost:8000/edges/{edge_id}"
```

### 7. Delete Relationship
```bash
curl -X DELETE "http://localhost:8000/edges/{edge_id}"
```

### 8. Vector Search
```bash
curl -X POST "http://localhost:8000/search/vector" \
     -H "Content-Type: application/json" \
     -d '{
           "query_text": "What is machine learning?",
           "top_k": 5
         }'
```

### 9. Graph Traversal
```bash
curl "http://localhost:8000/search/graph?start_id={node_id}&depth=2"
```

### 10. Hybrid Search
```bash
curl -X POST "http://localhost:8000/search/hybrid" \
     -H "Content-Type: application/json" \
     -d '{
           "query_text": "Explain supervised learning",
           "vector_weight": 0.7,
           "graph_weight": 0.3,
           "top_k": 5
         }'
```
