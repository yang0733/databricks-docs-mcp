"""MCP tools for documentation recommendations."""

import logging

logger = logging.getLogger(__name__)


def register_recommendation_tools(mcp, search_engine, cache):
    """Register recommendation tools with MCP server.
    
    Args:
        mcp: FastMCP instance
        search_engine: SemanticSearch instance
        cache: DocCache instance
    """
    
    @mcp.tool()
    def recommend_related(page_url: str, limit: int = 5) -> dict:
        """Find documentation pages related to a specific page.
        
        Args:
            page_url: URL of the reference page
            limit: Maximum number of recommendations (default: 5)
            
        Returns:
            Dictionary with related pages
        """
        try:
            # Handle partial URLs
            if not page_url.startswith("http"):
                page_url = f"https://docs.databricks.com/aws/en/{page_url.lstrip('/')}"
            
            related = search_engine.find_similar_pages(page_url, limit=limit)
            
            return {
                "reference_page": page_url,
                "total_related": len(related),
                "related_pages": related,
            }
            
        except Exception as e:
            logger.error(f"Failed to find related pages: {e}")
            return {
                "error": str(e),
                "reference_page": page_url,
                "related_pages": [],
            }
    
    @mcp.tool()
    def suggest_docs(context: str, limit: int = 5) -> dict:
        """Get documentation suggestions based on context or task description.
        
        Args:
            context: Description of what you're trying to do (e.g., "I need to create a streaming pipeline with Delta Lake")
            limit: Maximum number of suggestions (default: 5)
            
        Returns:
            Dictionary with suggested documentation pages
        """
        try:
            results = search_engine.search(context, limit=limit)
            
            return {
                "context": context,
                "total_suggestions": len(results),
                "suggestions": results,
            }
            
        except Exception as e:
            logger.error(f"Failed to suggest docs: {e}")
            return {
                "error": str(e),
                "context": context,
                "suggestions": [],
            }
    
    @mcp.tool()
    def get_quickstart(topic: str) -> dict:
        """Find getting started guides for a specific topic.
        
        Args:
            topic: Topic name (e.g., "delta", "mlflow", "unity catalog", "sql")
            
        Returns:
            Dictionary with quickstart guides and tutorials
        """
        try:
            # Search for getting started content
            query = f"getting started {topic} quickstart tutorial"
            results = search_engine.search(query, limit=10)
            
            # Filter for pages likely to be tutorials/quickstarts
            quickstarts = []
            for result in results:
                title_lower = result["page_title"].lower()
                url_lower = result["page_url"].lower()
                
                # Check if it's a getting started / tutorial page
                if any(keyword in title_lower or keyword in url_lower 
                       for keyword in ["getting started", "quickstart", "tutorial", "quick start", "intro"]):
                    quickstarts.append(result)
            
            # If no specific quickstarts found, return top general results
            if not quickstarts:
                quickstarts = results[:5]
            
            return {
                "topic": topic,
                "total_guides": len(quickstarts),
                "guides": quickstarts,
            }
            
        except Exception as e:
            logger.error(f"Failed to get quickstart: {e}")
            return {
                "error": str(e),
                "topic": topic,
                "guides": [],
            }
    
    @mcp.tool()
    def explore_category(category: str, limit: int = 20) -> dict:
        """Explore all pages in a documentation category.
        
        Args:
            category: Category name (e.g., "machine-learning", "data-engineering")
            limit: Maximum pages to return (default: 20)
            
        Returns:
            Dictionary with pages in the category
        """
        try:
            pages = cache.get_pages_by_category(category)
            
            # Format page summaries
            page_summaries = []
            for page in pages[:limit]:
                page_summaries.append({
                    "url": page.url,
                    "title": page.title,
                    "breadcrumbs": page.breadcrumbs,
                    "sections_count": len(page.sections),
                    "last_updated": page.last_updated.isoformat(),
                })
            
            return {
                "category": category,
                "total_pages": len(pages),
                "displayed_pages": len(page_summaries),
                "pages": page_summaries,
            }
            
        except Exception as e:
            logger.error(f"Failed to explore category: {e}")
            return {
                "error": str(e),
                "category": category,
                "pages": [],
            }
    
    @mcp.tool()
    def get_popular_topics() -> dict:
        """Get most popular documentation topics based on page count.
        
        Returns:
            Dictionary with popular topics and their page counts
        """
        try:
            categories = cache.list_categories()
            
            # Sort by page count
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            popular = [
                {
                    "category": cat,
                    "page_count": count,
                    "sample_query": f"Show me {cat} documentation"
                }
                for cat, count in sorted_categories[:15]
            ]
            
            return {
                "total_topics": len(categories),
                "popular_topics": popular,
            }
            
        except Exception as e:
            logger.error(f"Failed to get popular topics: {e}")
            return {
                "error": str(e),
                "popular_topics": [],
            }

