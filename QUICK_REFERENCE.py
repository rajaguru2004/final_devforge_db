"""
Quick Reference Guide for GraphDB
All essential methods with examples
"""

# ============================================================================
# INITIALIZATION
# ============================================================================

from graph_db import GraphDB

db = GraphDB()


# ============================================================================
# NODE OPERATIONS
# ============================================================================

# CREATE NODE
node = db.create_node(
    node_id="user_001",
    label="User", 
    properties={"name": "Alice", "age": 30, "active": True}
)

# GET NODE
user = db.get_node("user_001")
# Returns: {'node_id': 'user_001', 'label': 'User', 'name': 'Alice', ...}

# UPDATE NODE
updated = db.update_node("user_001", {"age": 31, "premium": True})

# DELETE NODE (also deletes all connected edges)
db.delete_node("user_001")


# ============================================================================
# EDGE OPERATIONS
# ============================================================================

# CREATE EDGE
edge = db.create_edge(
    from_id="user_001",
    to_id="product_001", 
    relation="purchased",
    properties={"price": 99.99, "date": "2024-01-15"}
)

# GET EDGE (returns list of edges)
edges = db.get_edge("user_001", "product_001")
edges_filtered = db.get_edge("user_001", "product_001", relation="purchased")

# UPDATE EDGE
updated_edges = db.update_edge(
    "user_001", 
    "product_001", 
    {"price": 89.99},
    relation="purchased"
)

# DELETE EDGE
db.delete_edge("user_001", "product_001")  # Delete all edges
db.delete_edge("user_001", "product_001", relation="purchased")  # Delete specific


# ============================================================================
# QUERY OPERATIONS
# ============================================================================

# FIND BY LABEL
all_users = db.find_nodes_by_label("User")
# Returns: [{'node_id': '...', 'label': 'User', ...}, ...]

# FIND BY PROPERTY
active_users = db.find_nodes_by_property("active", True)
premium_users = db.find_nodes_by_property("premium", True)

# FIND EDGES BY RELATION  
purchases = db.find_edges_by_relation("purchased")
# Returns: [{'from': '...', 'to': '...', 'relation': 'purchased', ...}, ...]


# ============================================================================
# TRAVERSAL OPERATIONS
# ============================================================================

# GET NEIGHBORS
outgoing = db.neighbors("user_001", direction='out')  # What user connects to
incoming = db.neighbors("product_001", direction='in')  # What connects to product
all_neighbors = db.neighbors("user_001", direction='both')  # All connections

# MULTI-HOP TRAVERSE
result = db.traverse("user_001", depth=2, direction='out')
# Returns: {
#   'nodes': [...],
#   'edges': [...],
#   'depth': 2,
#   'start_node': 'user_001'
# }

# TRAVERSE BY RELATION (follow specific relationship types)
friends = db.traverse_by_relation("user_001", "friends_with", depth=3)
# Finds all friends up to 3 degrees of separation


# ============================================================================
# RAG / SEMANTIC SEARCH
# ============================================================================

# SEMANTIC HOP SEARCH
rag_result = db.semantic_hop_search("premium", depth=2)
# Returns: {
#   'query': 'premium',
#   'matching_nodes': [...],  # Nodes with "premium" in properties
#   'context_nodes': [...],   # Matching nodes + neighbors up to depth
#   'edges': [...],
#   'total_nodes': 15,
#   'total_edges': 20
# }

# Example: Find all context around "organic" keyword
organic_context = db.semantic_hop_search("organic", depth=2)
print(f"Found {len(organic_context['matching_nodes'])} direct matches")
print(f"Expanded to {organic_context['total_nodes']} nodes")


# ============================================================================
# PERSISTENCE
# ============================================================================

# SAVE TO JSON
db.save_to_json("my_graph.json")

# LOAD FROM JSON
db2 = GraphDB()
db2.load_from_json("my_graph.json")


# ============================================================================
# UTILITY
# ============================================================================

# GET STATISTICS
stats = db.get_stats()
# Returns: {'total_nodes': 100, 'total_edges': 250}

# CLEAR GRAPH
db.clear()

# STRING REPRESENTATION
print(db)  # GraphDB(nodes=100, edges=250)


# ============================================================================
# ERROR HANDLING
# ============================================================================

from graph_db import (
    NodeNotFoundError, 
    EdgeNotFoundError,
    DuplicateNodeError,
    DuplicateEdgeError
)

try:
    node = db.get_node("non_existent")
except NodeNotFoundError as e:
    print(f"Error: {e}")

try:
    db.create_node("existing_id", "Label", {})
except DuplicateNodeError as e:
    print(f"Error: {e}")


# ============================================================================
# COMMON PATTERNS
# ============================================================================

# Pattern 1: Create a knowledge graph
def create_knowledge_graph():
    db = GraphDB()
    
    # Entities
    db.create_node("p1", "Person", {"name": "Alice"})
    db.create_node("p2", "Person", {"name": "Bob"})
    db.create_node("c1", "Company", {"name": "TechCorp"})
    
    # Relationships
    db.create_edge("p1", "c1", "works_at", {"role": "Engineer", "since": 2020})
    db.create_edge("p1", "p2", "knows", {"since": 2018})
    
    return db


# Pattern 2: Find shortest path context
def find_connection(db, person1, person2, depth=3):
    """Find how two people are connected"""
    result = db.traverse(person1, depth=depth)
    
    # Check if person2 is in the traversal
    node_ids = [n['node_id'] for n in result['nodes']]
    if person2 in node_ids:
        return result
    return None


# Pattern 3: Recommendation based on graph
def recommend_products(db, user_id, depth=2):
    """Find products that user's connections purchased"""
    
    # Get user's network
    network = db.traverse(user_id, depth=depth)
    
    # Find all 'purchased' edges in network
    recommendations = []
    for edge in network['edges']:
        if edge.get('relation') == 'purchased':
            product = db.get_node(edge['to'])
            recommendations.append(product)
    
    return recommendations


# Pattern 4: Build document knowledge graph for RAG
def add_document_chunks(db, document_id, chunks):
    """Add document chunks as nodes with relationships"""
    
    # Create document node
    db.create_node(document_id, "Document", {"title": "My Document"})
    
    # Add chunks
    prev_chunk_id = None
    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{document_id}_chunk_{i}"
        db.create_node(chunk_id, "Chunk", {
            "text": chunk_text,
            "index": i
        })
        
        # Link to document
        db.create_edge(chunk_id, document_id, "part_of")
        
        # Link to previous chunk
        if prev_chunk_id:
            db.create_edge(prev_chunk_id, chunk_id, "next")
        
        prev_chunk_id = chunk_id


# Pattern 5: Multi-criteria search
def advanced_search(db, criteria):
    """Search with multiple criteria"""
    results = set()
    
    # Search by each criterion
    for key, value in criteria.items():
        nodes = db.find_nodes_by_property(key, value)
        node_ids = {n['node_id'] for n in nodes}
        
        if not results:
            results = node_ids
        else:
            results &= node_ids  # Intersection (AND)
    
    return [db.get_node(nid) for nid in results]


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Create sample graph
    db = create_knowledge_graph()
    
    # Query
    people = db.find_nodes_by_label("Person")
    print(f"Found {len(people)} people")
    
    # Traverse
    alice_network = db.traverse("p1", depth=2)
    print(f"Alice's network: {len(alice_network['nodes'])} nodes")
    
    # Save
    db.save_to_json("/tmp/knowledge_graph.json")
    print("Saved!")
