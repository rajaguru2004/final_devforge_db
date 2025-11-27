"""
Graph Database Implementation using NetworkX

A complete graph database system with CRUD operations, querying, 
traversal capabilities, and RAG integration.
"""

import json
from typing import Dict, List, Any, Optional, Set
import networkx as nx


class GraphDBError(Exception):
    """Base exception for GraphDB errors"""
    pass


class NodeNotFoundError(GraphDBError):
    """Raised when a node is not found"""
    pass


class EdgeNotFoundError(GraphDBError):
    """Raised when an edge is not found"""
    pass


class DuplicateNodeError(GraphDBError):
    """Raised when attempting to create a duplicate node"""
    pass


class DuplicateEdgeError(GraphDBError):
    """Raised when attempting to create a duplicate edge"""
    pass


class GraphDB:
    """
    A Graph Database implementation using NetworkX.
    
    Supports:
    - Node and Edge CRUD operations
    - Property-based queries
    - Graph traversal
    - Import/Export to JSON
    - RAG-style semantic search
    """
    
    def __init__(self):
        """Initialize an empty directed multigraph"""
        self.graph = nx.MultiDiGraph()
    
    # ==================== NODE CRUD OPERATIONS ====================
    
    def create_node(self, node_id: str, label: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new node in the graph.
        
        Args:
            node_id: Unique identifier for the node
            label: Node label/type (e.g., 'Farmer', 'Crop')
            properties: Dictionary of node properties
            
        Returns:
            Dictionary containing node data
            
        Raises:
            DuplicateNodeError: If node already exists
        """
        if self.graph.has_node(node_id):
            raise DuplicateNodeError(f"Node '{node_id}' already exists")
        
        properties = properties or {}
        node_data = {
            'label': label,
            **properties
        }
        
        self.graph.add_node(node_id, **node_data)
        return {'node_id': node_id, **node_data}
    
    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Retrieve a node by its ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Dictionary containing node data
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if not self.graph.has_node(node_id):
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        node_data = dict(self.graph.nodes[node_id])
        return {'node_id': node_id, **node_data}
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update node properties.
        
        Args:
            node_id: Node identifier
            properties: Properties to update/add
            
        Returns:
            Updated node data
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if not self.graph.has_node(node_id):
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        # Update existing properties
        self.graph.nodes[node_id].update(properties)
        return self.get_node(node_id)
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all its edges.
        
        Args:
            node_id: Node identifier
            
        Returns:
            True if deleted successfully
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if not self.graph.has_node(node_id):
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        self.graph.remove_node(node_id)
        return True
    
    # ==================== EDGE CRUD OPERATIONS ====================
    
    def create_edge(self, from_id: str, to_id: str, relation: str, 
                   properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a directed edge between two nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Relationship type (e.g., 'grows', 'located_in')
            properties: Edge properties
            
        Returns:
            Dictionary containing edge data
            
        Raises:
            NodeNotFoundError: If either node doesn't exist
            DuplicateEdgeError: If edge with same relation already exists
        """
        if not self.graph.has_node(from_id):
            raise NodeNotFoundError(f"Source node '{from_id}' not found")
        if not self.graph.has_node(to_id):
            raise NodeNotFoundError(f"Target node '{to_id}' not found")
        
        # Check for duplicate edge with same relation
        if self.graph.has_edge(from_id, to_id):
            for key, edge_data in self.graph[from_id][to_id].items():
                if edge_data.get('relation') == relation:
                    raise DuplicateEdgeError(
                        f"Edge from '{from_id}' to '{to_id}' with relation '{relation}' already exists"
                    )
        
        properties = properties or {}
        edge_data = {
            'relation': relation,
            **properties
        }
        
        self.graph.add_edge(from_id, to_id, **edge_data)
        return {
            'from': from_id,
            'to': to_id,
            **edge_data
        }
    
    def get_edge(self, from_id: str, to_id: str, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get edge(s) between two nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Optional - filter by relation type
            
        Returns:
            List of edge dictionaries
            
        Raises:
            EdgeNotFoundError: If no edge exists
        """
        if not self.graph.has_edge(from_id, to_id):
            raise EdgeNotFoundError(f"No edge from '{from_id}' to '{to_id}'")
        
        edges = []
        for key, edge_data in self.graph[from_id][to_id].items():
            if relation is None or edge_data.get('relation') == relation:
                edges.append({
                    'from': from_id,
                    'to': to_id,
                    'key': key,
                    **edge_data
                })
        
        if not edges:
            raise EdgeNotFoundError(
                f"No edge from '{from_id}' to '{to_id}' with relation '{relation}'"
            )
        
        return edges
    
    def update_edge(self, from_id: str, to_id: str, properties: Dict[str, Any], 
                   relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Update edge properties.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            properties: Properties to update
            relation: Optional - update specific relation type
            
        Returns:
            List of updated edges
            
        Raises:
            EdgeNotFoundError: If edge doesn't exist
        """
        if not self.graph.has_edge(from_id, to_id):
            raise EdgeNotFoundError(f"No edge from '{from_id}' to '{to_id}'")
        
        updated_edges = []
        for key, edge_data in self.graph[from_id][to_id].items():
            if relation is None or edge_data.get('relation') == relation:
                self.graph[from_id][to_id][key].update(properties)
                updated_edges.append({
                    'from': from_id,
                    'to': to_id,
                    'key': key,
                    **self.graph[from_id][to_id][key]
                })
        
        if not updated_edges:
            raise EdgeNotFoundError(
                f"No edge from '{from_id}' to '{to_id}' with relation '{relation}'"
            )
        
        return updated_edges
    
    def delete_edge(self, from_id: str, to_id: str, relation: Optional[str] = None) -> bool:
        """
        Delete edge(s) between nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Optional - delete specific relation type
            
        Returns:
            True if deleted successfully
            
        Raises:
            EdgeNotFoundError: If edge doesn't exist
        """
        if not self.graph.has_edge(from_id, to_id):
            raise EdgeNotFoundError(f"No edge from '{from_id}' to '{to_id}'")
        
        if relation is None:
            # Remove all edges between nodes
            self.graph.remove_edge(from_id, to_id)
        else:
            # Remove specific relation
            keys_to_remove = []
            for key, edge_data in self.graph[from_id][to_id].items():
                if edge_data.get('relation') == relation:
                    keys_to_remove.append(key)
            
            if not keys_to_remove:
                raise EdgeNotFoundError(
                    f"No edge from '{from_id}' to '{to_id}' with relation '{relation}'"
                )
            
            for key in keys_to_remove:
                self.graph.remove_edge(from_id, to_id, key)
        
        return True
    
    # ==================== QUERY OPERATIONS ====================
    
    def find_nodes_by_label(self, label: str) -> List[Dict[str, Any]]:
        """
        Find all nodes with a specific label.
        
        Args:
            label: Node label to search for
            
        Returns:
            List of matching nodes
        """
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('label') == label:
                results.append({'node_id': node_id, **data})
        return results
    
    def find_nodes_by_property(self, key: str, value: Any) -> List[Dict[str, Any]]:
        """
        Find nodes by property key-value pair.
        
        Args:
            key: Property key
            value: Property value to match
            
        Returns:
            List of matching nodes
        """
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get(key) == value:
                results.append({'node_id': node_id, **data})
        return results
    
    def find_edges_by_relation(self, relation: str) -> List[Dict[str, Any]]:
        """
        Find all edges with a specific relation type.
        
        Args:
            relation: Relation type to search for
            
        Returns:
            List of matching edges
        """
        results = []
        for from_id, to_id, key, data in self.graph.edges(data=True, keys=True):
            if data.get('relation') == relation:
                results.append({
                    'from': from_id,
                    'to': to_id,
                    'key': key,
                    **data
                })
        return results
    
    # ==================== TRAVERSAL OPERATIONS ====================
    
    def neighbors(self, node_id: str, direction: str = 'out') -> List[Dict[str, Any]]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: Node identifier
            direction: 'out' (successors), 'in' (predecessors), or 'both'
            
        Returns:
            List of neighbor nodes
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        if not self.graph.has_node(node_id):
            raise NodeNotFoundError(f"Node '{node_id}' not found")
        
        neighbor_ids = set()
        
        if direction in ['out', 'both']:
            neighbor_ids.update(self.graph.successors(node_id))
        
        if direction in ['in', 'both']:
            neighbor_ids.update(self.graph.predecessors(node_id))
        
        return [self.get_node(nid) for nid in neighbor_ids]
    
    def traverse(self, start_node: str, depth: int = 1, direction: str = 'out') -> Dict[str, Any]:
        """
        Traverse the graph from a starting node up to a certain depth.
        
        Args:
            start_node: Starting node ID
            depth: Maximum traversal depth
            direction: 'out', 'in', or 'both'
            
        Returns:
            Dictionary with nodes and edges in the traversal
            
        Raises:
            NodeNotFoundError: If start node doesn't exist
        """
        if not self.graph.has_node(start_node):
            raise NodeNotFoundError(f"Node '{start_node}' not found")
        
        visited_nodes = set()
        visited_edges = []
        queue = [(start_node, 0)]
        
        while queue:
            current_node, current_depth = queue.pop(0)
            
            if current_node in visited_nodes or current_depth > depth:
                continue
            
            visited_nodes.add(current_node)
            
            if current_depth < depth:
                # Get neighbors based on direction
                neighbors = []
                if direction in ['out', 'both']:
                    neighbors.extend(self.graph.successors(current_node))
                if direction in ['in', 'both']:
                    neighbors.extend(self.graph.predecessors(current_node))
                
                for neighbor in neighbors:
                    queue.append((neighbor, current_depth + 1))
                    
                    # Collect edges
                    if direction in ['out', 'both'] and self.graph.has_edge(current_node, neighbor):
                        for key, data in self.graph[current_node][neighbor].items():
                            visited_edges.append({
                                'from': current_node,
                                'to': neighbor,
                                'key': key,
                                **data
                            })
                    
                    if direction in ['in', 'both'] and self.graph.has_edge(neighbor, current_node):
                        for key, data in self.graph[neighbor][current_node].items():
                            visited_edges.append({
                                'from': neighbor,
                                'to': current_node,
                                'key': key,
                                **data
                            })
        
        nodes = [self.get_node(nid) for nid in visited_nodes]
        
        return {
            'nodes': nodes,
            'edges': visited_edges,
            'depth': depth,
            'start_node': start_node
        }
    
    def traverse_by_relation(self, start_node: str, relation: str, 
                           depth: int = 3, direction: str = 'out') -> Dict[str, Any]:
        """
        Traverse graph following specific relation types.
        
        Args:
            start_node: Starting node ID
            relation: Relation type to follow
            depth: Maximum traversal depth
            direction: 'out', 'in', or 'both'
            
        Returns:
            Dictionary with nodes and edges matching the relation
            
        Raises:
            NodeNotFoundError: If start node doesn't exist
        """
        if not self.graph.has_node(start_node):
            raise NodeNotFoundError(f"Node '{start_node}' not found")
        
        visited_nodes = set()
        visited_edges = []
        queue = [(start_node, 0)]
        
        while queue:
            current_node, current_depth = queue.pop(0)
            
            if current_node in visited_nodes or current_depth > depth:
                continue
            
            visited_nodes.add(current_node)
            
            if current_depth < depth:
                # Check outgoing edges
                if direction in ['out', 'both']:
                    for neighbor in self.graph.successors(current_node):
                        for key, data in self.graph[current_node][neighbor].items():
                            if data.get('relation') == relation:
                                queue.append((neighbor, current_depth + 1))
                                visited_edges.append({
                                    'from': current_node,
                                    'to': neighbor,
                                    'key': key,
                                    **data
                                })
                
                # Check incoming edges
                if direction in ['in', 'both']:
                    for neighbor in self.graph.predecessors(current_node):
                        for key, data in self.graph[neighbor][current_node].items():
                            if data.get('relation') == relation:
                                queue.append((neighbor, current_depth + 1))
                                visited_edges.append({
                                    'from': neighbor,
                                    'to': current_node,
                                    'key': key,
                                    **data
                                })
        
        nodes = [self.get_node(nid) for nid in visited_nodes]
        
        return {
            'nodes': nodes,
            'edges': visited_edges,
            'relation': relation,
            'depth': depth,
            'start_node': start_node
        }
    
    # ==================== RAG INTEGRATION ====================
    
    def semantic_hop_search(self, query_string: str, depth: int = 2) -> Dict[str, Any]:
        """
        Perform RAG-style semantic search using keyword matching and graph traversal.
        
        Args:
            query_string: Search keyword
            depth: Number of hops to expand from matching nodes
            
        Returns:
            Dictionary containing matching nodes, expanded context, and edges
        """
        query_lower = query_string.lower()
        matching_nodes = []
        
        # Step 1: Find nodes with matching keywords in properties
        for node_id, data in self.graph.nodes(data=True):
            # Check if query appears in any property value
            for key, value in data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    matching_nodes.append(node_id)
                    break
                elif isinstance(value, bool) and query_lower in str(value).lower():
                    matching_nodes.append(node_id)
                    break
        
        # Step 2: Expand to neighbors up to depth hops
        all_nodes = set(matching_nodes)
        all_edges = []
        
        for start_node in matching_nodes:
            traversal_result = self.traverse(start_node, depth=depth, direction='both')
            
            for node in traversal_result['nodes']:
                all_nodes.add(node['node_id'])
            
            all_edges.extend(traversal_result['edges'])
        
        # Step 3: Collect full node data
        context_nodes = [self.get_node(nid) for nid in all_nodes]
        
        # Remove duplicate edges
        unique_edges = []
        seen_edges = set()
        for edge in all_edges:
            edge_sig = (edge['from'], edge['to'], edge.get('relation'))
            if edge_sig not in seen_edges:
                seen_edges.add(edge_sig)
                unique_edges.append(edge)
        
        return {
            'query': query_string,
            'matching_nodes': [self.get_node(nid) for nid in matching_nodes],
            'context_nodes': context_nodes,
            'edges': unique_edges,
            'depth': depth,
            'total_nodes': len(context_nodes),
            'total_edges': len(unique_edges)
        }
    
    # ==================== IMPORT/EXPORT ====================
    
    def save_to_json(self, filepath: str) -> bool:
        """
        Save graph to JSON file.
        
        Args:
            filepath: Path to save JSON file
            
        Returns:
            True if saved successfully
        """
        data = {
            'nodes': [],
            'edges': []
        }
        
        # Export nodes
        for node_id, node_data in self.graph.nodes(data=True):
            data['nodes'].append({
                'node_id': node_id,
                **node_data
            })
        
        # Export edges
        for from_id, to_id, key, edge_data in self.graph.edges(data=True, keys=True):
            data['edges'].append({
                'from': from_id,
                'to': to_id,
                'key': key,
                **edge_data
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def load_from_json(self, filepath: str) -> bool:
        """
        Load graph from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if loaded successfully
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clear existing graph
        self.graph.clear()
        
        # Load nodes
        for node in data.get('nodes', []):
            node_id = node.pop('node_id')
            self.graph.add_node(node_id, **node)
        
        # Load edges
        for edge in data.get('edges', []):
            from_id = edge.pop('from')
            to_id = edge.pop('to')
            key = edge.pop('key', None)
            self.graph.add_edge(from_id, to_id, key=key, **edge)
        
        return True
    
    # ==================== UTILITY METHODS ====================
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get graph statistics.
        
        Returns:
            Dictionary with node and edge counts
        """
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges()
        }
    
    def clear(self) -> bool:
        """
        Clear all nodes and edges from the graph.
        
        Returns:
            True if cleared successfully
        """
        self.graph.clear()
        return True
    
    def __repr__(self) -> str:
        """String representation of the graph"""
        stats = self.get_stats()
        return f"GraphDB(nodes={stats['total_nodes']}, edges={stats['total_edges']})"
