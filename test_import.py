"""Simple test to debug import issues"""
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

try:
    print("\n1. Testing networkx import...")
    import networkx as nx
    print("   ✓ networkx imported successfully")
    
    print("\n2. Testing graph_db.models import...")
    from graph_db.models import GraphNode, GraphRelationship
    print("   ✓ models imported successfully")
    
    print("\n3. Testing graph_db.graph_db import...")
    from graph_db.graph_db import GraphDatabase
    print("   ✓ GraphDatabase imported successfully")
    
    print("\n4. Creating test node...")
    node = GraphNode("test", {"key": "value"})
    print(f"   ✓ Created node: {node}")
    
    print("\n5. Creating test database...")
    db = GraphDatabase()
    print(f"   ✓ Created database: {db}")
    
    print("\n6. Adding node to database...")
    n1 = db.create_node("Test node", {"test": True})
    print(f"   ✓ Added node: {n1}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
