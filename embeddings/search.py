"""Semantic search implementation."""

import logging
from typing import List, Dict, Optional

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.storage.models import DocPage
from databricks_docs_mcp.embeddings.embedder import DocumentEmbedder
from databricks_docs_mcp.embeddings.vector_db import VectorDB

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Semantic search for documentation."""
    
    def __init__(
        self,
        cache: Optional[DocCache] = None,
        embedder: Optional[DocumentEmbedder] = None,
        vector_db: Optional[VectorDB] = None,
    ):
        """Initialize semantic search.
        
        Args:
            cache: Document cache
            embedder: Document embedder
            vector_db: Vector database
        """
        self.cache = cache or DocCache()
        self.embedder = embedder or DocumentEmbedder()
        self.vector_db = vector_db or VectorDB()
    
    def index_page(self, page: DocPage):
        """Index a page for semantic search.
        
        Args:
            page: Page to index
        """
        try:
            # Delete existing chunks for this page
            self.vector_db.delete_by_url(page.url)
            
            # Chunk the page
            chunks = self.embedder.chunk_page(page)
            
            if not chunks:
                logger.warning(f"No chunks generated for {page.url}")
                return
            
            # Generate embeddings
            embeddings = self.embedder.embed_chunks(chunks)
            
            # Add to vector DB
            self.vector_db.add_chunks(chunks, embeddings)
            
            logger.info(f"Indexed {len(chunks)} chunks for {page.title}")
            
        except Exception as e:
            logger.error(f"Failed to index page {page.url}: {e}")
    
    def index_all_pages(self):
        """Index all pages in cache."""
        logger.info("Indexing all pages...")
        
        pages = self.cache.get_all_pages()
        total = len(pages)
        
        for idx, page in enumerate(pages, 1):
            self.index_page(page)
            
            if idx % 10 == 0:
                logger.info(f"Indexed {idx}/{total} pages")
        
        logger.info(f"Indexing complete: {total} pages indexed")
    
    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """Semantic search for documentation.
        
        Args:
            query: Search query
            limit: Maximum results
            category: Optional category filter
            
        Returns:
            List of search results with page info
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)
            
            # Search vector DB
            if category:
                results = self.vector_db.search_by_category(
                    query_embedding=query_embedding,
                    category=category,
                    limit=limit * 2,  # Get more for deduplication
                )
            else:
                results = self.vector_db.search(
                    query_embedding=query_embedding,
                    limit=limit * 2,
                )
            
            # Deduplicate by page URL and format
            formatted_results = self._format_and_deduplicate(results, limit)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _format_and_deduplicate(
        self,
        results: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Format search results and deduplicate by page.
        
        Args:
            results: Raw search results
            limit: Max results to return
            
        Returns:
            Formatted and deduplicated results
        """
        seen_urls = set()
        formatted = []
        
        for result in results:
            metadata = result.get("metadata", {})
            page_url = metadata.get("page_url")
            
            # Skip if we've already seen this page
            if page_url in seen_urls:
                continue
            
            seen_urls.add(page_url)
            
            # Get full page info from cache
            page = self.cache.get_page(page_url)
            
            formatted_result = {
                "page_url": page_url,
                "page_title": metadata.get("page_title", "Unknown"),
                "section_title": metadata.get("section_title"),
                "content_snippet": result.get("content", "")[:300] + "...",
                "score": result.get("score", 0.0),
                "category": metadata.get("category"),
                "breadcrumbs": page.breadcrumbs if page else [],
            }
            
            formatted.append(formatted_result)
            
            if len(formatted) >= limit:
                break
        
        return formatted
    
    def find_similar_pages(
        self,
        page_url: str,
        limit: int = 5
    ) -> List[Dict]:
        """Find pages similar to a given page.
        
        Args:
            page_url: URL of the reference page
            limit: Maximum results
            
        Returns:
            List of similar pages
        """
        try:
            # Get the page
            page = self.cache.get_page(page_url)
            if not page:
                logger.warning(f"Page not found: {page_url}")
                return []
            
            # Use page title and first section as query
            query = f"{page.title}\n{page.content[:500]}"
            
            # Search
            results = self.search(query, limit=limit + 1)
            
            # Filter out the original page
            similar = [r for r in results if r["page_url"] != page_url]
            
            return similar[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar pages: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get search system statistics.
        
        Returns:
            Dict with stats
        """
        return {
            "cache": self.cache.get_cache_stats(),
            "vector_db": self.vector_db.get_stats(),
            "embedder_model": self.embedder.model_name,
        }

