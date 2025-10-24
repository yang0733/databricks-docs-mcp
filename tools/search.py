"""MCP tools for searching documentation."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def register_search_tools(mcp, search_engine, cache):
    """Register search tools with MCP server.
    
    Args:
        mcp: FastMCP instance
        search_engine: SemanticSearch instance
        cache: DocCache instance
    """
    
    @mcp.tool()
    def search_docs(query: str, limit: int = 10) -> dict:
        """Search Databricks documentation using semantic search.
        
        Args:
            query: Search query (e.g., "How to create a Delta table?")
            limit: Maximum number of results (default: 10)
            
        Returns:
            Dictionary with search results including page URLs, titles, and snippets
        """
        try:
            results = search_engine.search(query, limit=limit)
            
            return {
                "query": query,
                "total_results": len(results),
                "results": results,
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "results": [],
            }
    
    @mcp.tool()
    def get_page(url: str) -> dict:
        """Get a specific documentation page by URL.
        
        Args:
            url: Full URL or path of the documentation page
            
        Returns:
            Dictionary with page content and metadata
        """
        try:
            # Handle partial URLs
            if not url.startswith("http"):
                url = f"https://docs.databricks.com/aws/en/{url.lstrip('/')}"
            
            page = cache.get_page(url)
            
            if not page:
                return {
                    "error": "Page not found",
                    "url": url,
                }
            
            return {
                "url": page.url,
                "title": page.title,
                "content": page.content,
                "sections": [
                    {
                        "title": s.title,
                        "level": s.level,
                        "content": s.content,
                    }
                    for s in page.sections
                ],
                "breadcrumbs": page.breadcrumbs,
                "category": page.category,
                "last_updated": page.last_updated.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get page: {e}")
            return {
                "error": str(e),
                "url": url,
            }
    
    @mcp.tool()
    def list_categories() -> dict:
        """List all documentation categories with page counts.
        
        Returns:
            Dictionary with categories and their page counts
        """
        try:
            categories = cache.list_categories()
            
            return {
                "total_categories": len(categories),
                "categories": [
                    {"name": cat, "page_count": count}
                    for cat, count in sorted(categories.items())
                ],
            }
            
        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            return {
                "error": str(e),
                "categories": [],
            }
    
    @mcp.tool()
    def search_by_category(category: str, query: str, limit: int = 10) -> dict:
        """Search documentation within a specific category.
        
        Args:
            category: Category name (e.g., "getting-started", "delta", "sql")
            query: Search query
            limit: Maximum number of results (default: 10)
            
        Returns:
            Dictionary with filtered search results
        """
        try:
            results = search_engine.search(
                query=query,
                limit=limit,
                category=category,
            )
            
            return {
                "category": category,
                "query": query,
                "total_results": len(results),
                "results": results,
            }
            
        except Exception as e:
            logger.error(f"Category search failed: {e}")
            return {
                "error": str(e),
                "category": category,
                "query": query,
                "results": [],
            }
    
    @mcp.tool()
    def get_page_sections(url: str) -> dict:
        """Get the table of contents (sections) for a documentation page.
        
        Args:
            url: Full URL or path of the documentation page
            
        Returns:
            Dictionary with page sections and their content snippets
        """
        try:
            # Handle partial URLs
            if not url.startswith("http"):
                url = f"https://docs.databricks.com/aws/en/{url.lstrip('/')}"
            
            page = cache.get_page(url)
            
            if not page:
                return {
                    "error": "Page not found",
                    "url": url,
                }
            
            sections = []
            for section in page.sections:
                sections.append({
                    "title": section.title,
                    "level": section.level,
                    "anchor": section.anchor,
                    "content_preview": section.content[:200] + "..." if len(section.content) > 200 else section.content,
                })
            
            return {
                "url": page.url,
                "title": page.title,
                "total_sections": len(sections),
                "sections": sections,
            }
            
        except Exception as e:
            logger.error(f"Failed to get page sections: {e}")
            return {
                "error": str(e),
                "url": url,
            }

