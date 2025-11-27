import os
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class VectorDatabase:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function
        )

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """Add or update a document in the vector store."""
        # Chroma's add_texts or add_documents handles upsert if IDs are provided
        self.db.add_texts(
            texts=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def delete_document(self, doc_id: str):
        """Delete a document from the vector store."""
        try:
            self.db.delete(ids=[doc_id])
        except ValueError:
            # Handle case where ID doesn't exist if needed, though Chroma might just warn
            pass

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Tuple[str, str, float, Dict[str, Any]]]:
        """
        Search for documents similar to the query.
        Returns: List of (id, text, score, metadata)
        """
        results = self.db.similarity_search_with_score(query, k=top_k, filter=filter)
        formatted_results = []
        for doc, score in results:
            # Chroma returns distance, convert to similarity
            # Assuming L2 distance (lower is better), similarity = 1 / (1 + distance)
            # Or if it's cosine distance, similarity = 1 - distance.
            # LangChain Chroma usually returns distance.
            # Let's stick to the formula used in hybrid_retrieval.py: 1.0 / (1.0 + score)
            similarity = 1.0 / (1.0 + score)
            
            # Chroma stores the ID in the internal structure, but LangChain's Document object
            # might not expose it directly unless we put it in metadata or use the ID returned by search if available.
            # However, when we add_texts with ids, Chroma uses those.
            # LangChain's similarity_search_with_score returns Document objects.
            # We need to ensure we can get the ID back.
            # Usually, we store ID in metadata as well to be safe, or rely on Chroma to return it.
            # LangChain's Chroma implementation might not return the ID in the Document object easily without a hack.
            # BUT, we can just store 'id' in metadata when adding.
            
            doc_id = doc.metadata.get('id')
            # If id is not in metadata, we might have a problem if we rely on it.
            # So I will ensure 'id' is in metadata in add_document.
            
            formatted_results.append((doc_id, doc.page_content, similarity, doc.metadata))
            
        return formatted_results

    def update_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """Update a document. In Chroma, adding with same ID overwrites."""
        self.add_document(doc_id, text, metadata)
