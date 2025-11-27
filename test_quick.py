"""Quick test of GraphDB functionality"""

import sys
sys.path.insert(0, '/home/suryaguru/StudioProjects/final_devforge_db')

from graph_db import GraphDB

# Test basic functionality
db = GraphDB()
print("✓ GraphDB initialized successfully")

# Create a simple graph
db.create_node("n1", "Person", {"name": "Alice"})
db.create_node("n2", "Person", {"name": "Bob"})
db.create_edge("n1", "n2", "knows")
print("✓ Created nodes and edges")

# Query
result = db.find_nodes_by_label("Person")
print(f"✓ Found {len(result)} Person nodes")

# Traverse
traversal = db.traverse("n1", depth=1)
print(f"✓ Traversal found {len(traversal['nodes'])} nodes")

# RAG search
rag = db.semantic_hop_search("Alice", depth=1)
print(f"✓ RAG search found {len(rag['matching_nodes'])} matches")

# Save/Load
db.save_to_json("/tmp/test_graph.json")
print("✓ Saved to JSON")

db2 = GraphDB()
db2.load_from_json("/tmp/test_graph.json")
print(f"✓ Loaded from JSON: {db2.get_stats()}")

print("\n🎉 All tests passed!")
print(f"   Final graph: {db}")
