"""ChromaDB vector database wrapper."""

import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings

from databricks_docs_mcp.storage.models import DocumentChunk

logger = logging.getLogger(__name__)


class VectorDB:
    """Manages vector database for semantic search."""
    
    def __init__(self, persist_directory: str = "storage/chromadb"):
        """Initialize vector database.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        logger.info(f"Initializing ChromaDB at {persist_directory}")
        
        # Create persistent client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="databricks_docs",
            metadata={"description": "Databricks AWS documentation"}
        )
        
        logger.info(f"ChromaDB initialized with {self.collection.count()} documents")
    
    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ):
        """Add document chunks with embeddings to the database.
        
        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors
        """
        if not chunks or not embeddings:
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = {
                "page_url": chunk.page_url,
                "page_title": chunk.page_title,
                "chunk_index": chunk.chunk_index,
            }
            
            # Add optional fields
            if chunk.section_title:
                metadata["section_title"] = chunk.section_title
            
            # Add custom metadata
            if chunk.metadata:
                for key, value in chunk.metadata.items():
                    # ChromaDB only supports simple types in metadata
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    elif isinstance(value, list) and value:
                        # Convert list to comma-separated string
                        metadata[key] = ",".join(str(v) for v in value)
            
            metadatas.append(metadata)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Added {len(chunks)} chunks to vector DB")
        except Exception as e:
            logger.error(f"Failed to add chunks to vector DB: {e}")
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with metadata and scores
        """
        try:
            # Build where clause for filtering
            where = filter_metadata if filter_metadata else None
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
            )
            
            # Format results
            formatted_results = []
            
            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None,
                        "score": 1.0 - results['distances'][0][i] if 'distances' in results else None,
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_by_category(
        self,
        query_embedding: List[float],
        category: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Search within a specific category.
        
        Args:
            query_embedding: Query embedding vector
            category: Category to filter by
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        return self.search(
            query_embedding=query_embedding,
            limit=limit,
            filter_metadata={"category": category},
        )
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get a specific chunk by ID.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            Chunk data or None if not found
        """
        try:
            results = self.collection.get(ids=[chunk_id])
            
            if results and results['ids']:
                return {
                    "id": results['ids'][0],
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0],
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {e}")
            return None
    
    def delete_by_url(self, page_url: str):
        """Delete all chunks for a specific page URL.
        
        Args:
            page_url: Page URL to delete chunks for
        """
        try:
            self.collection.delete(
                where={"page_url": page_url}
            )
            logger.info(f"Deleted chunks for {page_url}")
        except Exception as e:
            logger.error(f"Failed to delete chunks for {page_url}: {e}")
    
    def clear(self):
        """Clear all documents from the database."""
        try:
            # Delete collection and recreate
            self.client.delete_collection("databricks_docs")
            self.collection = self.client.create_collection(
                name="databricks_docs",
                metadata={"description": "Databricks AWS documentation"}
            )
            logger.info("Vector DB cleared")
        except Exception as e:
            logger.error(f"Failed to clear vector DB: {e}")
    
    def get_stats(self) -> Dict:
        """Get database statistics.
        
        Returns:
            Dict with stats
        """
        return {
            "total_chunks": self.collection.count(),
            "collection_name": self.collection.name,
        }

