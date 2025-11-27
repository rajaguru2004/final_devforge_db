import os
from typing import List, Dict, Any, Optional
import collections
import shutil
from fastapi import UploadFile
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models import (
    NodeCreate, NodeResponse, NodeUpdate, NodeUpdateResponse, NodeDeleteResponse,
    EdgeCreate, EdgeResponse, EdgeDeleteResponse,
    VectorSearchResult, GraphTraversalResponse, GraphTraversalResultItem,
    HybridSearchResult
)
from app.vector_db import VectorDatabase
from graph_db.graph_db import GraphDatabase
from graph_db.models import GraphNode, GraphRelationship

class HybridRetrievalService:
    def __init__(self):
        # Paths
        current_dir = os.getcwd()
        self.vector_db_path = os.path.join(current_dir, "db", "chroma_db_service")
        self.graph_db_path = os.path.join(current_dir, "db", "graph_data_service.json")
        self.books_dir = os.path.join(current_dir, "vector_db", "books")
        os.makedirs(self.books_dir, exist_ok=True)
        
        # Initialize DBs
        self.vector_db = VectorDatabase(persist_directory=self.vector_db_path)
        self.graph_db = GraphDatabase(db_path=self.graph_db_path, auto_persist=True)

    # ==================== Node Operations ====================

    def create_node(self, node_data: NodeCreate) -> NodeResponse:
        # Create in GraphDB
        # Note: GraphDatabase.create_node returns a GraphNode
        # We don't generate embedding here manually if we use VectorDB to handle it via sentence-transformers
        # But GraphNode has an 'embedding' field. 
        # The prompt says "auto_embed: true" -> "embedding_created: true"
        # It implies the system handles it.
        # My VectorDB wrapper uses HuggingFaceEmbeddings to embed text.
        # So I should add to VectorDB if auto_embed is True.
        
        # Create node in graph first to get ID
        graph_node = self.graph_db.create_node(
            text=node_data.text,
            metadata=node_data.metadata
        )
        
        embedding_created = False
        if node_data.auto_embed:
            # Add 'id' to metadata for VectorDB retrieval
            meta = node_data.metadata.copy()
            meta['id'] = graph_node.id
            self.vector_db.add_document(graph_node.id, node_data.text, meta)
            embedding_created = True
            
        return NodeResponse(
            id=graph_node.id,
            text=graph_node.text,
            metadata=graph_node.metadata,
            embedding_created=embedding_created
        )

    def get_node(self, node_id: str) -> Optional[NodeResponse]:
        graph_node = self.graph_db.get_node(node_id)
        if not graph_node:
            return None
            
        # Get relationships
        relationships = []
        # GraphDatabase doesn't have a direct "get_edges_for_node" method exposed clearly in the interface 
        # but we can access the graph directly or implement a helper.
        # The prompt response for Get Node includes "relationships": [{target, type, weight}]
        # I'll access the networkx graph directly from graph_db.graph
        
        # Outgoing edges
        if node_id in self.graph_db.graph:
            for neighbor in self.graph_db.graph.successors(node_id):
                for key, edge_data in self.graph_db.graph[node_id][neighbor].items():
                    relationships.append({
                        "target": neighbor,
                        "type": edge_data.get("type"),
                        "weight": edge_data.get("weight")
                    })
        
        return NodeResponse(
            id=graph_node.id,
            text=graph_node.text,
            metadata=graph_node.metadata,
            relationships=relationships
        )

    def update_node(self, node_id: str, update_data: NodeUpdate) -> Optional[NodeUpdateResponse]:
        # Check if node exists
        if not self.graph_db.get_node(node_id):
            return None
            
        # Update GraphDB
        self.graph_db.update_node(
            node_id=node_id,
            text=update_data.text,
            metadata=update_data.metadata
        )
        
        embedding_regenerated = False
        if update_data.regenerate_embedding:
            # We need the text. If it was updated, use new text. If not, fetch existing.
            current_node = self.graph_db.get_node(node_id)
            if current_node:
                meta = current_node.metadata.copy()
                meta['id'] = node_id
                self.vector_db.update_document(node_id, current_node.text, meta)
                embedding_regenerated = True
                
        return NodeUpdateResponse(
            status="updated",
            id=node_id,
            embedding_regenerated=embedding_regenerated
        )

    def delete_node(self, node_id: str) -> Optional[NodeDeleteResponse]:
        # Count edges to be removed for response
        edges_removed = 0
        if node_id in self.graph_db.graph:
            edges_removed += self.graph_db.graph.out_degree(node_id)
            edges_removed += self.graph_db.graph.in_degree(node_id)
            
        success = self.graph_db.delete_node(node_id)
        if not success:
            return None
            
        # Delete from VectorDB
        self.vector_db.delete_document(node_id)
        
        return NodeDeleteResponse(
            status="deleted",
            id=node_id,
            edges_removed=edges_removed
        )

    # ==================== Edge Operations ====================

    def create_edge(self, edge_data: EdgeCreate) -> Optional[EdgeResponse]:
        edge = self.graph_db.create_edge(
            source_id=edge_data.source,
            target_id=edge_data.target,
            rel_type=edge_data.type,
            weight=edge_data.weight
        )
        if not edge:
            return None
            
        return EdgeResponse(
            status="edge_created",
            edge_id=edge.id,
            source=edge.source,
            target=edge.target,
            type=edge.type,
            weight=edge.weight
        )

    def get_edge(self, edge_id: str) -> Optional[EdgeResponse]:
        edge = self.graph_db.get_edge(edge_id)
        if not edge:
            return None
            
        return EdgeResponse(
            edge_id=edge.id,
            source=edge.source,
            target=edge.target,
            type=edge.type,
            weight=edge.weight
        )

    def delete_edge(self, edge_id: str) -> Optional[EdgeDeleteResponse]:
        success = self.graph_db.delete_edge(edge_id)
        if not success:
            return None
            
        return EdgeDeleteResponse(
            status="deleted",
            id=edge_id
        )

    # ==================== Search Operations ====================

    def vector_search(self, query: str, top_k: int, filter: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        results = self.vector_db.search(query, top_k, filter=filter)
        response = []
        for doc_id, text, score, metadata in results:
            # Ensure doc_id is present (fallback to metadata if needed)
            nid = doc_id or metadata.get('id')
            if not nid:
                continue # Skip if no ID found
                
            response.append(VectorSearchResult(
                node_id=nid,
                text=text,
                cosine_similarity=round(score, 4),
                metadata=metadata
            ))
        return response

    def graph_traversal(self, start_id: str, depth: int) -> Optional[GraphTraversalResponse]:
        if not self.graph_db.get_node(start_id):
            return None
            
        # Use GraphDB traverse, but we need depths. 
        # GraphDB.traverse returns list of IDs.
        # GraphDB.compute_graph_scores calculates scores but logic is slightly different.
        # I'll implement a simple BFS here to get depths as requested in API.
        
        visited = {start_id: 0}
        queue = [(start_id, 0)]
        results = []
        
        import collections
        queue = collections.deque([(start_id, 0)])
        
        while queue:
            node_id, current_depth = queue.popleft()
            
            if current_depth > 0:
                results.append(GraphTraversalResultItem(node_id=node_id, depth=current_depth))
            
            if current_depth < depth:
                # Neighbors
                if node_id in self.graph_db.graph:
                    neighbors = set(self.graph_db.graph.successors(node_id))
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            visited[neighbor] = current_depth + 1
                            queue.append((neighbor, current_depth + 1))
                            
        return GraphTraversalResponse(
            start=start_id,
            depth=depth,
            results=results
        )

    def hybrid_search(self, query: str, vector_weight: float, graph_weight: float, top_k: int, filter: Optional[Dict[str, Any]] = None) -> List[HybridSearchResult]:
        # 1. Vector Search
        vector_results = self.vector_search(query, top_k, filter=filter)
        
        # 2. Graph Expansion & Scoring - Optimized with Multi-Source BFS
        # We need to compute graph scores for each vector result
        # Map: node_id -> {cosine_score, graph_score, text, metadata}
        candidates = {}
        
        # Initialize with vector results
        # We'll use these as starting points for Multi-Source BFS
        start_nodes = []
        
        for res in vector_results:
            candidates[res.node_id] = {
                "text": res.text,
                "metadata": res.metadata,
                "cosine_similarity": res.cosine_similarity,
                "graph_score": 0.0
            }
            start_nodes.append(res.node_id)
            
        # Multi-Source BFS
        # We want to find the minimum depth from ANY start node to other nodes.
        # Depth 0 (Start Node) -> Score 1.0
        # Depth 1 -> Score 1.0
        # Depth 2 -> Score 0.5
        
        graph_scores_map = {} # node_id -> score
        visited = {} # node_id -> min_depth
        
        # Initialize queue with all start nodes at depth 0
        queue = collections.deque()
        for nid in start_nodes:
            if nid not in visited:
                visited[nid] = 0
                queue.append((nid, 0))
                # Score for depth 0
                graph_scores_map[nid] = 1.0
        
        while queue:
            curr, d = queue.popleft()
            
            # Determine score based on depth
            score = 0.0
            if d == 0: score = 1.0
            elif d == 1: score = 1.0
            elif d == 2: score = 0.5
            
            # We only process up to depth 2 for scoring
            if d > 2:
                continue
                
            # Update score if better (though BFS guarantees we see min depth first, so first visit is best)
            # But since we have multiple sources, a node might be reached from source A at depth 2 
            # and later from source B at depth 1? 
            # No, standard BFS with all sources in initial queue guarantees finding min depth from *any* source first.
            # So we just assign score on first visit.
            graph_scores_map[curr] = score
            
            if d < 2:
                if curr in self.graph_db.graph:
                    # Expand to neighbors (Successors and Predecessors)
                    neighbors = set(self.graph_db.graph.successors(curr)) | set(self.graph_db.graph.predecessors(curr))
                    for n in neighbors:
                        if n not in visited:
                            visited[n] = d + 1
                            queue.append((n, d + 1))

        # 3. Combine
        final_candidates = {}
        
        # Add vector results again to ensure they are in (they might be in graph_scores_map too)
        for nid, data in candidates.items():
            final_candidates[nid] = data
            
        # Add pure graph results
        for nid, g_score in graph_scores_map.items():
            if nid not in final_candidates:
                # Fetch node details
                node = self.graph_db.get_node(nid)
                if node:
                    final_candidates[nid] = {
                        "text": node.text,
                        "metadata": node.metadata,
                        "cosine_similarity": 0.0,
                        "graph_score": g_score
                    }
            else:
                final_candidates[nid]["graph_score"] = g_score
                
        # Calculate final score
        results = []
        for nid, data in final_candidates.items():
            final_score = (data["cosine_similarity"] * vector_weight) + (data["graph_score"] * graph_weight)
            results.append(HybridSearchResult(
                node_id=nid,
                text=data["text"],
                cosine_similarity=round(data["cosine_similarity"], 4),
                graph_score=round(data["graph_score"], 4),
                final_score=round(final_score, 4),
                metadata=data["metadata"]
            ))
            
        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)
        
        return results[:top_k]

    # ==================== PDF Operations ====================

    def process_pdf_and_search(self, file: UploadFile, query: str) -> HybridSearchResult:
        # 1. Save PDF and Extract Text
        filename = file.filename
        file_path = os.path.join(self.books_dir, filename)
        
        # Save uploaded file (PDF) - wait, user said "extract the text from it @[vector_db/books] and it should automatically store in this directory"
        # So we should save the text file there.
        # But first we need to read the PDF.
        
        # Save PDF temporarily to read it? Or read from stream.
        # Let's read from stream to avoid saving PDF if not needed, but saving it is safer for debugging.
        # I'll save the PDF temporarily or just process stream.
        # User said "store in this directory and using that txt file alone".
        # So I must save the TXT file.
        
        # Extract text
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        # Save text file
        txt_filename = f"{os.path.splitext(filename)[0]}.txt"
        txt_path = os.path.join(self.books_dir, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        # 2. Ingest into DB (Scoped) - Optimized with Batching
        # We need to chunk the text and create nodes.
        # We'll use a specific source tag for this file.
        source_id = txt_filename
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # Prepare for batch insertion
        node_ids = []
        node_texts = []
        node_metadatas = []
        
        # Create nodes in GraphDB first (in memory/batch if possible, but GraphDB is sequential)
        # However, we can disable auto-persist on GraphDB temporarily if we had access, 
        # but here we just iterate. GraphDB operations are relatively fast if not persisting every time.
        # But VectorDB is the bottleneck.
        
        import uuid
        
        # We will create GraphNodes manually to get IDs, then batch insert to VectorDB
        # And batch insert to GraphDB if we add a method, or just loop.
        # Let's loop for GraphDB but batch for VectorDB.
        
        # Optimize: Disable auto-persist temporarily
        original_auto_persist = self.graph_db.auto_persist
        self.graph_db.auto_persist = False
        
        prev_node_id = None
        
        try:
            for i, chunk in enumerate(chunks):
                # Generate ID
                node_id = str(uuid.uuid4())
                metadata = {"source": source_id, "chunk_index": i}
                
                # Add to GraphDB
                # We use create_node but we need to avoid the individual vector db add
                # So we can't use self.create_node directly if we want to batch vector add.
                # We'll call graph_db.create_node directly.
                
                self.graph_db.create_node(
                    text=chunk,
                    metadata=metadata,
                    node_id=node_id
                )
                
                # Collect for VectorDB Batch
                node_ids.append(node_id)
                node_texts.append(chunk)
                # Add ID to metadata for VectorDB
                vector_meta = metadata.copy()
                vector_meta['id'] = node_id
                node_metadatas.append(vector_meta)
                
                # Create Edge from previous chunk
                if prev_node_id:
                    self.create_edge(EdgeCreate(
                        source=prev_node_id,
                        target=node_id,
                        type="next_chunk",
                        weight=1.0
                    ))
                prev_node_id = node_id
        finally:
            # Restore and save
            self.graph_db.auto_persist = original_auto_persist
            if self.graph_db.auto_persist:
                self.graph_db.save()
            
        # Batch insert to VectorDB
            
        # Batch insert to VectorDB
        if node_ids:
            self.vector_db.add_documents(node_ids, node_texts, node_metadatas)
            
        # Force persist GraphDB once if needed, but it auto-persists on create_node currently.
        # To optimize GraphDB, we would need to disable auto-persist in init and save manually.
        # But user asked to reduce time "wherever possible".
        # VectorDB batching is the biggest win.
            
        # 3. Hybrid Search on this source
        # We filter by metadata "source": source_id
        results = self.hybrid_search(
            query=query,
            vector_weight=0.7, # Default weights
            graph_weight=0.3,
            top_k=5,
            filter={"source": source_id}
        )
        
        if not results:
            # Return empty or raise?
            # User output format implies we should return something that can be printed.
            # I'll return a dummy result or raise 404 if not found?
            # But let's return the top result if exists.
            # If empty, I'll return an empty object or handle in router.
            pass
            
        return results[0] if results else None

