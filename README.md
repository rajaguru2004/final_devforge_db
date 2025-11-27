# DevForge Graph Database

A complete, production-quality **Graph Database implementation using Python + NetworkX**.

## 🎯 Features

### Core Functionality
- ✅ **Node CRUD Operations** - Create, Read, Update, Delete nodes with labels and properties
- ✅ **Edge CRUD Operations** - Manage relationships between nodes with properties
- ✅ **Property Support** - Rich metadata for both nodes and edges
- ✅ **Graph Traversal** - Multi-hop traversal with depth control
- ✅ **Query Engine** - Search by label, property, or relationship type
- ✅ **Import/Export** - Save and load graphs from JSON
- ✅ **Error Handling** - Comprehensive error handling with custom exceptions
- ✅ **RAG Integration** - Mini RAG-style semantic hop search

### Advanced Features
- 🔍 Keyword-based semantic search
- 🔗 Relation-specific traversal
- 📊 Graph statistics and analytics
- 🎯 Multi-directional neighbor queries
- 💾 JSON persistence layer

## 📦 Installation

```bash
# Activate poetry shell
poetry shell

# Install dependencies
poetry install --no-root
```

## 🚀 Quick Start

```python
from graph_db import GraphDB

# Initialize database
db = GraphDB()

# Create nodes
farmer = db.create_node(
    "farmer_001",
    label="Farmer",
    properties={"name": "Rajesh Kumar", "age": 45}
)

crop = db.create_node(
    "crop_001",
    label="Crop",
    properties={"name": "Organic Rice", "organic": True}
)

# Create relationship
db.create_edge(
    "farmer_001", 
    "crop_001", 
    "grows",
    properties={"hectares": 5, "yield_tons": 15}
)

# Query
organic_crops = db.find_nodes_by_property("organic", True)

# Traverse
result = db.traverse("farmer_001", depth=2)

# RAG Search
rag_result = db.semantic_hop_search("organic", depth=2)

# Save
db.save_to_json("my_graph.json")
```

## 🏃 Running Examples

```bash
# Run all examples
poetry run python main.py
```

This will demonstrate:
1. Creating nodes and edges
2. Updating properties
3. Querying by property (find organic crops)
4. Complex queries (high-profit crop farmers)
5. Multi-hop traversal
6. Relation-specific traversal
7. Semantic hop search (RAG)
8. Import/Export to JSON
9. Error handling
10. Advanced queries

## 📖 API Reference

### GraphDB Class

#### Node Operations

```python
# Create node
create_node(node_id: str, label: str, properties: Dict = None) -> Dict

# Get node
get_node(node_id: str) -> Dict

# Update node
update_node(node_id: str, properties: Dict) -> Dict

# Delete node
delete_node(node_id: str) -> bool
```

#### Edge Operations

```python
# Create edge
create_edge(from_id: str, to_id: str, relation: str, properties: Dict = None) -> Dict

# Get edge
get_edge(from_id: str, to_id: str, relation: str = None) -> List[Dict]

# Update edge
update_edge(from_id: str, to_id: str, properties: Dict, relation: str = None) -> List[Dict]

# Delete edge
delete_edge(from_id: str, to_id: str, relation: str = None) -> bool
```

#### Query Operations

```python
# Find nodes by label
find_nodes_by_label(label: str) -> List[Dict]

# Find nodes by property
find_nodes_by_property(key: str, value: Any) -> List[Dict]

# Find edges by relation
find_edges_by_relation(relation: str) -> List[Dict]
```

#### Traversal Operations

```python
# Get neighbors
neighbors(node_id: str, direction: str = 'out') -> List[Dict]
# direction: 'out', 'in', or 'both'

# Traverse graph
traverse(start_node: str, depth: int = 1, direction: str = 'out') -> Dict

# Traverse by relation
traverse_by_relation(start_node: str, relation: str, depth: int = 3, direction: str = 'out') -> Dict
```

#### RAG Operations

```python
# Semantic hop search
semantic_hop_search(query_string: str, depth: int = 2) -> Dict
```

#### Persistence

```python
# Save to JSON
save_to_json(filepath: str) -> bool

# Load from JSON
load_from_json(filepath: str) -> bool
```

## 🌾 Example Dataset

The examples include a farming domain dataset:

```
Farmer → grows → Crop → sold_in → Market
Farmer → located_in → Village → part_of → District
```

**Entities:**
- **Farmer**: {name, age, experience_years, certified_organic}
- **Crop**: {name, season, organic}
- **Market**: {name, city, price_index}
- **Village**: {name, population}
- **District**: {name, state}

**Relationships:**
- **grows**: {hectares, yield_tons}
- **sold_in**: {price_per_kg, demand}
- **located_in**: {}
- **part_of**: {}

## 🔍 Example Queries

### Find All Organic Crops
```python
organic_crops = db.find_nodes_by_property("organic", True)
```

### Find Farmers Growing High-Profit Crops
```python
# Multi-step traversal to connect farmers → crops → markets
result = db.traverse("farmer_001", depth=3)
```

### Find All Markets Connected to a Farmer
```python
# Multi-hop traversal
markets = db.traverse("farmer_001", depth=3, direction='out')
```

### Semantic Search for "organic"
```python
# RAG-style search with context expansion
rag_result = db.semantic_hop_search("organic", depth=2)
```

## 🛠️ Error Handling

The library includes custom exceptions:

- `NodeNotFoundError` - Node doesn't exist
- `EdgeNotFoundError` - Edge doesn't exist
- `DuplicateNodeError` - Node already exists
- `DuplicateEdgeError` - Edge already exists

```python
from graph_db import GraphDB, NodeNotFoundError

try:
    node = db.get_node("non_existent")
except NodeNotFoundError as e:
    print(f"Error: {e}")
```

## 📈 Extending to Full Graph RAG

To build a complete Graph RAG system, add:

### 1. Embedding Models
```python
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

# Add embeddings to node properties
embeddings = OpenAIEmbeddings()
vector = embeddings.embed_query(node_text)
db.update_node(node_id, {"embedding": vector})
```

### 2. Vector Similarity Search
```python
import numpy as np

def find_similar_nodes(query_embedding, top_k=5):
    # Compare query embedding with node embeddings
    similarities = []
    for node_id, data in db.graph.nodes(data=True):
        if 'embedding' in data:
            similarity = cosine_similarity(query_embedding, data['embedding'])
            similarities.append((node_id, similarity))
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
```

### 3. LLM Integration
```python
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain

# Use LLM to understand natural language queries
llm = ChatOpenAI(temperature=0)

def query_with_llm(question: str):
    # 1. Convert question to graph query
    # 2. Execute traversal
    # 3. Format results with LLM
    context = db.semantic_hop_search(question, depth=2)
    # Generate answer from context
```

### 4. Caching & Indexing
```python
# Add Redis caching for frequent queries
# Create indexes for common property lookups
# Use vector databases (ChromaDB, Pinecone) for embeddings
```

### 5. Advanced Features
- **Community Detection**: Identify clusters in the graph
- **Pathfinding**: Shortest path between entities
- **Centrality Analysis**: Find important nodes
- **Temporal Graphs**: Add time-based edges
- **Multi-modal**: Store different data types

## 📝 Project Structure

```
devforge_db/
├── graph_db/
│   ├── __init__.py       # Module exports
│   └── graph.py          # GraphDB implementation
├── examples.py           # Comprehensive examples
├── main.py               # Entry point
├── pyproject.toml        # Dependencies
├── README.md             # This file
└── .env                  # Environment variables
```

## 🎓 Learning Resources

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Graph Database Concepts](https://neo4j.com/developer/graph-database/)
- [Graph RAG Papers](https://arxiv.org/search/?query=graph+retrieval+augmented+generation)

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add more traversal algorithms
- Implement graph algorithms (PageRank, community detection)
- Add visualization capabilities
- Performance optimizations for large graphs
- Support for other graph formats (GraphML, GML)

## 📧 Support

For questions or issues, please refer to the examples.py file for comprehensive usage patterns.

---

**Built with ❤️ using Python, NetworkX, and LangChain ecosystem**
