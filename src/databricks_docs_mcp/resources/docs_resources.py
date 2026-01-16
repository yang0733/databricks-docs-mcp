"""MCP resources for browsing documentation."""

import logging
from typing import List

logger = logging.getLogger(__name__)


def register_doc_resources(mcp, cache):
    """Register documentation resources with MCP server.
    
    Args:
        mcp: FastMCP instance
        cache: DocCache instance
    """
    
    @mcp.resource("databricks-docs://aws/en/index")
    def list_all_docs() -> str:
        """List all available Databricks documentation pages.
        
        Returns:
            Formatted list of all documentation pages
        """
        try:
            pages = cache.get_all_pages()
            
            output = ["# Databricks AWS Documentation Index", ""]
            output.append(f"Total Pages: {len(pages)}")
            output.append("")
            
            # Group by category
            categories = cache.list_categories()
            
            for category, count in sorted(categories.items()):
                output.append(f"## {category} ({count} pages)")
                output.append("")
                
                category_pages = cache.get_pages_by_category(category)
                for page in category_pages[:10]:  # Limit to first 10 per category
                    output.append(f"- [{page.title}]({page.url})")
                
                if count > 10:
                    output.append(f"  ... and {count - 10} more pages")
                
                output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Failed to list docs: {e}")
            return f"Error listing documentation: {e}"
    
    # Note: Parameterized resources not supported in this FastMCP version
    # Use the get_page() tool instead to retrieve specific pages
    
    @mcp.resource("databricks-docs://categories")
    def list_categories() -> str:
        """List all documentation categories.
        
        Returns:
            Formatted list of categories
        """
        try:
            categories = cache.list_categories()
            
            output = ["# Documentation Categories", ""]
            output.append(f"Total Categories: {len(categories)}")
            output.append("")
            
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                output.append(f"- **{category}**: {count} pages")
            
            output.append("")
            output.append("---")
            output.append("")
            output.append("Use the `explore_category` tool to view pages in a specific category.")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            return f"Error listing categories: {e}"

