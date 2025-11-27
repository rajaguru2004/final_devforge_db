#!/usr/bin/env python3
"""Test NetworkX MultiDiGraph behavior"""
import networkx as nx

print("Testing NetworkX MultiDiGraph...")
g = nx.MultiDiGraph()

# Add nodes
g.add_node("n1")
g.add_node("n2")

# Add edge
print("\nAdding edge...")
result = g.add_edge("n1", "n2", id="edge1", type="test", weight=1.5)
print(f"add_edge returned: {result} (type: {type(result)})")

# Check edge data
print("\nChecking edge data...")
print(f"Edges: {list(g.edges(keys=True, data=True))}")

# Access edge data
print("\nAccessing edge data:")
print(f"g['n1']['n2']: {g['n1']['n2']}")
for key, data in g['n1']['n2'].items():
    print(f"  key={key}, data={data}")

# Access by key
if result is not None:
    print(f"\nAccess by key {result}:")
    print(f"g['n1']['n2'][{result}]: {g['n1']['n2'][result]}")
