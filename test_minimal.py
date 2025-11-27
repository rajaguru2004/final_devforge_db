#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("Importing...")
from graph_db import GraphDatabase

print("Creating DB...")
db = GraphDatabase(auto_persist=False)

print("Creating node...")
n = db.create_node("test", {})

print(f"SUCCESS: {n.id}")
