#!/usr/bin/env python3
"""Simple debug test"""
import sys
import traceback

try:
    print("Testing imports...")
    from graph_db import GraphDatabase
    
    print("Creating database...")
    db = GraphDatabase()
    
    print("Creating nodes...")
    n1 = db.create_node("Node 1", {})
    n2 = db.create_node("Node 2", {})
    print(f"  n1: {n1.id[:8]}")
    print(f"  n2: {n2.id[:8]}")
    
    print("\nCreating edge...")
    edge = db.create_edge(n1.id, n2.id, "test", weight=1.0)
    print(f"  edge: {edge.id[:8]}")
    print(f"  Edge map: {db._edge_id_map[edge.id]}")
    
    print("\nRetrieving edge...")
    retrieved = db.get_edge(edge.id)
    print(f"  Retrieved: {retrieved}")
    if retrieved:
        print(f"    source: {retrieved.source[:8]}")
        print(f"    target: {retrieved.target[:8]}")
        print(f"    type: {retrieved.type}")
        print(f"    weight: {retrieved.weight}")
    
    print("\n✅ All operations successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
