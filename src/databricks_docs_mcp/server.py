"""Databricks Documentation MCP Server."""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from fastmcp import FastMCP

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.storage.models import DocIndex
from databricks_docs_mcp.embeddings.embedder import DocumentEmbedder
from databricks_docs_mcp.embeddings.vector_db import VectorDB
from databricks_docs_mcp.embeddings.search import SemanticSearch
from databricks_docs_mcp.crawler.scraper import DocScraper
from databricks_docs_mcp.crawler.scheduler import DocRefreshScheduler
from databricks_docs_mcp.tools.search import register_search_tools
from databricks_docs_mcp.tools.recommend import register_recommendation_tools
from databricks_docs_mcp.resources.docs_resources import register_doc_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docs_mcp_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="DatabricksDocumentation")

# Global instances
cache: DocCache = None
search_engine: SemanticSearch = None
scheduler: DocRefreshScheduler = None


def initialize_components():
    """Initialize all server components."""
    global cache, search_engine, scheduler
    
    logger.info("Initializing MCP server components...")
    
    # Initialize cache
    logger.info("Initializing document cache...")
    cache = DocCache(cache_dir="storage/data")
    
    # Initialize embedder and vector DB
    logger.info("Initializing embedder and vector database...")
    embedder = DocumentEmbedder(model_name="all-MiniLM-L6-v2")
    vector_db = VectorDB(persist_directory="storage/chromadb")
    
    # Initialize search engine
    logger.info("Initializing semantic search...")
    search_engine = SemanticSearch(
        cache=cache,
        embedder=embedder,
        vector_db=vector_db,
    )
    
    # Check if cache is empty (first run)
    if cache.index.total_pages == 0:
        logger.warning("=" * 70)
        logger.warning("Documentation cache is empty!")
        logger.warning("Run initial crawl with: python -m databricks_docs_mcp crawl")
        logger.warning("Or use --crawl flag when starting server")
        logger.warning("=" * 70)
    else:
        logger.info(f"Cache loaded: {cache.index.total_pages} pages")
        
        # Check if vector DB needs indexing
        if vector_db.collection.count() == 0:
            logger.info("Vector DB is empty, indexing all pages...")
            search_engine.index_all_pages()
    
    # Initialize scheduler
    logger.info("Initializing refresh scheduler...")
    scheduler = DocRefreshScheduler(
        cache=cache,
        search_engine=search_engine,
    )
    
    logger.info("Components initialized successfully")


# Register all tools
def register_all_tools():
    """Register all MCP tools and resources."""
    logger.info("Registering MCP tools and resources...")
    
    # Register search tools
    register_search_tools(mcp, search_engine, cache)
    
    # Register recommendation tools
    register_recommendation_tools(mcp, search_engine, cache)
    
    # Register resources
    register_doc_resources(mcp, cache)
    
    logger.info("Tools and resources registered")


# Server status tool
@mcp.tool()
def get_server_status() -> dict:
    """Get server status and statistics.
    
    Returns:
        Dictionary with server stats including cache size, vector DB info, and refresh status
    """
    try:
        cache_stats = cache.get_cache_stats()
        search_stats = search_engine.get_stats()
        refresh_status = scheduler.get_status() if scheduler else {}
        
        return {
            "status": "running",
            "cache": cache_stats,
            "search": search_stats,
            "scheduler": refresh_status,
        }
        
    except Exception as e:
        logger.error(f"Failed to get server status: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


@mcp.tool()
def trigger_refresh() -> dict:
    """Manually trigger a documentation refresh.
    
    Returns:
        Dictionary with refresh trigger status
    """
    try:
        if scheduler:
            return scheduler.trigger_manual_refresh()
        else:
            return {
                "status": "error",
                "message": "Scheduler not initialized",
            }
        
    except Exception as e:
        logger.error(f"Failed to trigger refresh: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def perform_initial_crawl(max_pages: int = None):
    """Perform initial documentation crawl.
    
    Args:
        max_pages: Maximum pages to crawl (None for all)
    """
    logger.info("=" * 70)
    logger.info("Starting initial documentation crawl")
    logger.info("=" * 70)
    
    scraper = DocScraper(
        base_url="https://docs.databricks.com/aws/en/",
        cache=cache,
        rate_limit=0.5,
    )
    
    pages_crawled = scraper.crawl_all(max_pages=max_pages)
    
    logger.info(f"Crawl complete: {pages_crawled} pages")
    
    # Index all pages
    logger.info("Indexing pages for semantic search...")
    search_engine.index_all_pages()
    
    logger.info("=" * 70)
    logger.info("Initial setup complete!")
    logger.info("=" * 70)


def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description='Databricks Documentation MCP Server'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8100,
        help='Port to bind to (default: 8100)'
    )
    parser.add_argument(
        '--crawl',
        action='store_true',
        help='Perform initial crawl before starting server'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum pages to crawl (for testing)'
    )
    parser.add_argument(
        '--no-scheduler',
        action='store_true',
        help='Disable automatic daily refresh'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 70)
    print("🚀 Databricks Documentation MCP Server")
    print("=" * 70)
    print(f"Host: {args.host}:{args.port}")
    print(f"Endpoints:")
    print(f"  • HTTP:   http://{args.host}:{args.port}/mcp")
    print(f"  • Health: http://{args.host}:{args.port}/health")
    print(f"\nFeatures:")
    print(f"  • Semantic search with sentence-transformers")
    print(f"  • MCP Resources for browsing documentation")
    print(f"  • MCP Tools for search and recommendations")
    print(f"  • Daily automatic refresh (2 AM)")
    print("=" * 70)
    
    # Initialize components
    initialize_components()
    
    # Perform initial crawl if requested
    if args.crawl:
        perform_initial_crawl(max_pages=args.max_pages)
    
    # Register tools
    register_all_tools()
    
    # Start scheduler unless disabled
    scheduler_started = False
    if not args.no_scheduler and scheduler:
        scheduler.start()
        scheduler_started = True
        logger.info("Automatic daily refresh enabled")
    
    # Run server
    logger.info("Starting MCP server...")
    try:
        mcp.run(
            transport='streamable-http',
            host=args.host,
            port=args.port
        )
    finally:
        # Cleanup - only stop if scheduler was actually started
        if scheduler_started and scheduler:
            try:
                scheduler.stop()
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")


if __name__ == '__main__':
    main()

