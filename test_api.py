from fastapi.testclient import TestClient
from app.main import app
import os
import shutil

# Clean up DBs for testing
if os.path.exists("db/test_graph_data.json"):
    os.remove("db/test_graph_data.json")
if os.path.exists("db/test_chroma_db"):
    shutil.rmtree("db/test_chroma_db")

# Mock paths in service (optional, but good for isolation)
# For now, we'll just run against the default paths or we could patch the service.
# Let's just run it. The service uses "db/chroma_db_service" and "db/graph_data_service.json"

client = TestClient(app)

def test_workflow():
    print("Testing Node Creation...")
    # 1. Create Node 1
    response = client.post("/nodes", json={
        "text": "Machine learning is a subset of AI.",
        "metadata": { "source": "doc1" },
        "auto_embed": True
    })
    assert response.status_code == 200
    node1 = response.json()
    node1_id = node1["id"]
    print(f"Created Node 1: {node1_id}")

    # 2. Create Node 2
    response = client.post("/nodes", json={
        "text": "Supervised learning uses labeled data.",
        "metadata": { "source": "doc2" },
        "auto_embed": True
    })
    assert response.status_code == 200
    node2 = response.json()
    node2_id = node2["id"]
    print(f"Created Node 2: {node2_id}")

    # 3. Create Edge
    print("Testing Edge Creation...")
    response = client.post("/edges", json={
        "source": node1_id,
        "target": node2_id,
        "type": "subtopic",
        "weight": 0.9
    })
    assert response.status_code == 200
    edge = response.json()
    edge_id = edge["edge_id"]
    print(f"Created Edge: {edge_id}")

    # 4. Get Node (check relationships)
    print("Testing Get Node...")
    response = client.get(f"/nodes/{node1_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["relationships"]) > 0
    print("Node 1 relationships verified.")

    # 5. Vector Search
    print("Testing Vector Search...")
    response = client.post("/search/vector", json={
        "query_text": "What is machine learning?",
        "top_k": 5
    })
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    print(f"Vector search returned {len(results)} results.")

    # 6. Graph Traversal
    print("Testing Graph Traversal...")
    response = client.get(f"/search/graph?start_id={node1_id}&depth=2")
    assert response.status_code == 200
    data = response.json()
    assert data["start"] == node1_id
    assert len(data["results"]) > 0
    print("Graph traversal verified.")

    # 7. Hybrid Search
    print("Testing Hybrid Search...")
    response = client.post("/search/hybrid", json={
        "query_text": "Explain supervised learning",
        "vector_weight": 0.7,
        "graph_weight": 0.3,
        "top_k": 5
    })
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    print(f"Hybrid search returned {len(results)} results.")
    print(f"Top result: {results[0]}")

    # 8. Update Node
    print("Testing Update Node...")
    response = client.put(f"/nodes/{node1_id}", json={
        "text": "Updated ML content",
        "metadata": { "source": "updated_doc" },
        "regenerate_embedding": True
    })
    assert response.status_code == 200
    print("Node updated.")

    # 9. Delete Edge
    print("Testing Delete Edge...")
    response = client.delete(f"/edges/{edge_id}")
    assert response.status_code == 200
    print("Edge deleted.")

    # 10. Delete Node
    print("Testing Delete Node...")
    response = client.delete(f"/nodes/{node1_id}")
    assert response.status_code == 200
    print("Node deleted.")

if __name__ == "__main__":
    test_workflow()
