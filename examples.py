"""
Example Usage of GraphDB - Comprehensive Demonstration

This script demonstrates all features of the GraphDB system including:
- Node and Edge CRUD operations
- Property-based queries
- Graph traversal
- RAG-style semantic search
- Import/Export functionality
"""

from graph_db import GraphDB


def print_section(title: str):
    """Helper to print section headers"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    # Initialize the database
    db = GraphDB()
    
    # ==================== EXAMPLE 1: Creating Nodes ====================
    print_section("EXAMPLE 1: Creating Nodes")
    
    # Create farmers
    farmer1 = db.create_node(
        "farmer_001",
        label="Farmer",
        properties={"name": "Rajesh Kumar", "age": 45, "experience_years": 20}
    )
    print(f"Created: {farmer1}")
    
    farmer2 = db.create_node(
        "farmer_002",
        label="Farmer",
        properties={"name": "Priya Sharma", "age": 38, "experience_years": 15}
    )
    print(f"Created: {farmer2}")
    
    # Create crops
    crop1 = db.create_node(
        "crop_001",
        label="Crop",
        properties={"name": "Organic Rice", "season": "Kharif", "organic": True}
    )
    print(f"Created: {crop1}")
    
    crop2 = db.create_node(
        "crop_002",
        label="Crop",
        properties={"name": "Wheat", "season": "Rabi", "organic": False}
    )
    print(f"Created: {crop2}")
    
    crop3 = db.create_node(
        "crop_003",
        label="Crop",
        properties={"name": "Organic Vegetables", "season": "All Year", "organic": True}
    )
    print(f"Created: {crop3}")
    
    # Create markets
    market1 = db.create_node(
        "market_001",
        label="Market",
        properties={"name": "City Wholesale Market", "city": "Mumbai", "price_index": 95}
    )
    print(f"Created: {market1}")
    
    market2 = db.create_node(
        "market_002",
        label="Market",
        properties={"name": "Organic Farmers Market", "city": "Pune", "price_index": 120}
    )
    print(f"Created: {market2}")
    
    # Create villages
    village1 = db.create_node(
        "village_001",
        label="Village",
        properties={"name": "Greenfield Village", "population": 2500}
    )
    print(f"Created: {village1}")
    
    village2 = db.create_node(
        "village_002",
        label="Village",
        properties={"name": "Riverside Village", "population": 1800}
    )
    print(f"Created: {village2}")
    
    # Create district
    district1 = db.create_node(
        "district_001",
        label="District",
        properties={"name": "Satara District", "state": "Maharashtra"}
    )
    print(f"Created: {district1}")
    
    # ==================== EXAMPLE 2: Adding Relationships ====================
    print_section("EXAMPLE 2: Adding Relationships")
    
    # Farmers grow crops
    edge1 = db.create_edge("farmer_001", "crop_001", "grows", 
                          properties={"hectares": 5, "yield_tons": 15})
    print(f"Created edge: {edge1}")
    
    edge2 = db.create_edge("farmer_001", "crop_003", "grows",
                          properties={"hectares": 2, "yield_tons": 8})
    print(f"Created edge: {edge2}")
    
    edge3 = db.create_edge("farmer_002", "crop_002", "grows",
                          properties={"hectares": 10, "yield_tons": 30})
    print(f"Created edge: {edge3}")
    
    # Crops sold in markets
    db.create_edge("crop_001", "market_002", "sold_in",
                  properties={"price_per_kg": 45, "demand": "high"})
    print("Created edge: crop_001 -> market_002")
    
    db.create_edge("crop_002", "market_001", "sold_in",
                  properties={"price_per_kg": 25, "demand": "medium"})
    print("Created edge: crop_002 -> market_001")
    
    db.create_edge("crop_003", "market_002", "sold_in",
                  properties={"price_per_kg": 60, "demand": "high"})
    print("Created edge: crop_003 -> market_002")
    
    # Farmers located in villages
    db.create_edge("farmer_001", "village_001", "located_in")
    print("Created edge: farmer_001 -> village_001")
    
    db.create_edge("farmer_002", "village_002", "located_in")
    print("Created edge: farmer_002 -> village_002")
    
    # Villages part of district
    db.create_edge("village_001", "district_001", "part_of")
    print("Created edge: village_001 -> district_001")
    
    db.create_edge("village_002", "district_001", "part_of")
    print("Created edge: village_002 -> district_001")
    
    # ==================== EXAMPLE 3: Updating Properties ====================
    print_section("EXAMPLE 3: Updating Node and Edge Properties")
    
    # Update farmer age
    updated_farmer = db.update_node("farmer_001", {"age": 46, "certified_organic": True})
    print(f"Updated farmer: {updated_farmer}")
    
    # Update edge property
    updated_edges = db.update_edge("farmer_001", "crop_001", {"yield_tons": 18})
    print(f"Updated edge: {updated_edges}")
    
    # ==================== EXAMPLE 4: Query - Find All Organic Crops ====================
    print_section("EXAMPLE 4: Query - Find All Organic Crops")
    
    organic_crops = db.find_nodes_by_property("organic", True)
    print(f"Found {len(organic_crops)} organic crops:")
    for crop in organic_crops:
        print(f"  - {crop['name']} ({crop['season']})")
    
    # ==================== EXAMPLE 5: Query - Find High-Profit Crop Farmers ====================
    print_section("EXAMPLE 5: Query - Find Farmers Growing High-Profit Crops")
    
    # Find crops sold at price > 40
    high_profit_farmers = set()
    
    for edge in db.graph.edges(data=True, keys=True):
        from_id, to_id, key, data = edge
        if data.get('relation') == 'sold_in' and data.get('price_per_kg', 0) > 40:
            # This is a high-profit crop, find farmers who grow it
            crop_node = from_id
            for farmer_edge in db.graph.in_edges(crop_node, data=True, keys=True):
                f_from, f_to, f_key, f_data = farmer_edge
                if f_data.get('relation') == 'grows':
                    farmer_node = db.get_node(f_from)
                    high_profit_farmers.add(farmer_node['name'])
                    print(f"  - {farmer_node['name']} grows {db.get_node(crop_node)['name']}")
    
    # ==================== EXAMPLE 6: Multi-Hop Traversal ====================
    print_section("EXAMPLE 6: Multi-Hop Traversal - Markets Connected to Farmer")
    
    # Find all markets connected to farmer_001 (multi-hop)
    traversal_result = db.traverse("farmer_001", depth=3, direction='out')
    
    print(f"Starting from: {db.get_node('farmer_001')['name']}")
    print(f"\nTraversal found {len(traversal_result['nodes'])} nodes:")
    
    for node in traversal_result['nodes']:
        print(f"  - [{node['label']}] {node.get('name', node['node_id'])}")
    
    print(f"\nWith {len(traversal_result['edges'])} edges:")
    for edge in traversal_result['edges'][:5]:  # Show first 5
        print(f"  - {edge['from']} --[{edge['relation']}]--> {edge['to']}")
    
    # ==================== EXAMPLE 7: Relation-Specific Traversal ====================
    print_section("EXAMPLE 7: Traverse by Specific Relation - 'part_of'")
    
    # Start from a village and follow 'part_of' relations
    relation_traversal = db.traverse_by_relation("village_001", "part_of", depth=2)
    
    print(f"Following 'part_of' relation from {db.get_node('village_001')['name']}:")
    for node in relation_traversal['nodes']:
        print(f"  - [{node['label']}] {node.get('name', node['node_id'])}")
    
    # ==================== EXAMPLE 8: Semantic Hop Search (Mini RAG) ====================
    print_section("EXAMPLE 8: Semantic Hop Search for 'organic'")
    
    rag_result = db.semantic_hop_search("organic", depth=2)
    
    print(f"Query: '{rag_result['query']}'")
    print(f"Found {len(rag_result['matching_nodes'])} direct matches:")
    for node in rag_result['matching_nodes']:
        print(f"  - [{node['label']}] {node.get('name', node['node_id'])}")
    
    print(f"\nExpanded context includes {rag_result['total_nodes']} nodes and {rag_result['total_edges']} edges")
    print("\nContext nodes:")
    for node in rag_result['context_nodes']:
        print(f"  - [{node['label']}] {node.get('name', node['node_id'])}")
    
    # ==================== EXAMPLE 9: Export to JSON ====================
    print_section("EXAMPLE 9: Export Graph to JSON")
    
    json_path = "farm_graph.json"
    db.save_to_json(json_path)
    print(f"Graph saved to: {json_path}")
    print(f"Stats: {db.get_stats()}")
    
    # ==================== EXAMPLE 10: Import from JSON ====================
    print_section("EXAMPLE 10: Import Graph from JSON")
    
    # Create new database and load
    db2 = GraphDB()
    db2.load_from_json(json_path)
    print(f"Loaded graph from: {json_path}")
    print(f"Stats: {db2.get_stats()}")
    
    # Verify data
    farmers = db2.find_nodes_by_label("Farmer")
    print(f"\nVerified: Found {len(farmers)} farmers in loaded graph")
    
    # ==================== EXAMPLE 11: Error Handling ====================
    print_section("EXAMPLE 11: Error Handling Examples")
    
    # Try to create duplicate node
    try:
        db.create_node("farmer_001", "Farmer", {"name": "Duplicate"})
    except Exception as e:
        print(f"✓ Caught expected error: {type(e).__name__}: {e}")
    
    # Try to get non-existent node
    try:
        db.get_node("non_existent_node")
    except Exception as e:
        print(f"✓ Caught expected error: {type(e).__name__}: {e}")
    
    # Try to create edge with non-existent node
    try:
        db.create_edge("farmer_001", "non_existent_node", "knows")
    except Exception as e:
        print(f"✓ Caught expected error: {type(e).__name__}: {e}")
    
    # ==================== EXAMPLE 12: Advanced Queries ====================
    print_section("EXAMPLE 12: Advanced Queries")
    
    # Find all 'grows' relationships
    grows_edges = db.find_edges_by_relation("grows")
    print(f"Found {len(grows_edges)} 'grows' relationships:")
    for edge in grows_edges:
        farmer = db.get_node(edge['from'])
        crop = db.get_node(edge['to'])
        print(f"  - {farmer['name']} grows {crop['name']} "
              f"({edge.get('hectares', 0)} hectares, {edge.get('yield_tons', 0)} tons)")
    
    # Find all nodes in a specific village
    print("\nFarmers by village:")
    for village_id in ["village_001", "village_002"]:
        village = db.get_node(village_id)
        # Find farmers in this village
        farmers_in_village = []
        for from_id, to_id, key, data in db.graph.edges(data=True, keys=True):
            if to_id == village_id and data.get('relation') == 'located_in':
                farmer = db.get_node(from_id)
                farmers_in_village.append(farmer)
        
        print(f"  {village['name']}: {[f['name'] for f in farmers_in_village]}")
    
    # ==================== EXAMPLE 13: Neighbor Queries ====================
    print_section("EXAMPLE 13: Neighbor Queries")
    
    # Get outgoing neighbors (crops grown by farmer)
    out_neighbors = db.neighbors("farmer_001", direction='out')
    print(f"Farmer 001 outgoing neighbors (what they interact with):")
    for neighbor in out_neighbors:
        print(f"  - [{neighbor['label']}] {neighbor.get('name', neighbor['node_id'])}")
    
    # Get incoming neighbors (who/what connects to this crop)
    in_neighbors = db.neighbors("crop_001", direction='in')
    print(f"\nCrop 001 incoming neighbors (who grows it):")
    for neighbor in in_neighbors:
        print(f"  - [{neighbor['label']}] {neighbor.get('name', neighbor['node_id'])}")
    
    # Get all neighbors (both directions)
    all_neighbors = db.neighbors("village_001", direction='both')
    print(f"\nVillage 001 all neighbors:")
    for neighbor in all_neighbors:
        print(f"  - [{neighbor['label']}] {neighbor.get('name', neighbor['node_id'])}")
    
    # ==================== Final Summary ====================
    print_section("FINAL SUMMARY")
    
    final_stats = db.get_stats()
    print(f"Graph Database Statistics:")
    print(f"  Total Nodes: {final_stats['total_nodes']}")
    print(f"  Total Edges: {final_stats['total_edges']}")
    print(f"\n  Node Types:")
    
    labels = {}
    for node_id, data in db.graph.nodes(data=True):
        label = data.get('label', 'Unknown')
        labels[label] = labels.get(label, 0) + 1
    
    for label, count in labels.items():
        print(f"    - {label}: {count}")
    
    print(f"\n  Relationship Types:")
    relations = {}
    for from_id, to_id, key, data in db.graph.edges(data=True, keys=True):
        relation = data.get('relation', 'Unknown')
        relations[relation] = relations.get(relation, 0) + 1
    
    for relation, count in relations.items():
        print(f"    - {relation}: {count}")
    
    print("\n" + "=" * 70)
    print("  All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
