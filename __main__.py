"""CLI entry point for databricks_docs_mcp."""

import sys
import argparse
import logging
from pathlib import Path

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.embeddings.embedder import DocumentEmbedder
from databricks_docs_mcp.embeddings.vector_db import VectorDB
from databricks_docs_mcp.embeddings.search import SemanticSearch
from databricks_docs_mcp.crawler.scraper import DocScraper
from databricks_docs_mcp.crawler.async_scraper import AsyncDocScraper, run_async_crawl

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def crawl_command(args):
    """Crawl documentation."""
    cache = DocCache(cache_dir="storage/data")
    
    if args.fast:
        logger.info("Starting FAST async documentation crawl...")
        import asyncio
        
        scraper = AsyncDocScraper(
            cache=cache,
            max_concurrent=args.concurrent,
            rate_limit_per_second=args.rate_limit,
        )
        
        pages_crawled = asyncio.run(scraper.crawl_all(max_pages=args.max_pages))
    else:
        logger.info("Starting documentation crawl...")
        
        scraper = DocScraper(
            base_url="https://docs.databricks.com/aws/en/",
            cache=cache,
            rate_limit=args.rate_limit,
        )
        
        pages_crawled = scraper.crawl_all(max_pages=args.max_pages)
    
    logger.info(f"Crawl complete: {pages_crawled} pages")
    
    # Index if requested
    if not args.no_index:
        logger.info("Indexing pages...")
        embedder = DocumentEmbedder()
        vector_db = VectorDB()
        search_engine = SemanticSearch(cache=cache, embedder=embedder, vector_db=vector_db)
        search_engine.index_all_pages()
        logger.info("Indexing complete")


def refresh_command(args):
    """Refresh existing documentation."""
    logger.info("Starting documentation refresh...")
    
    cache = DocCache(cache_dir="storage/data")
    scraper = DocScraper(cache=cache, rate_limit=args.rate_limit)
    
    pages_updated = scraper.incremental_update()
    
    logger.info(f"Refresh complete: {pages_updated} pages updated")
    
    # Re-index if requested
    if not args.no_index:
        logger.info("Re-indexing pages...")
        embedder = DocumentEmbedder()
        vector_db = VectorDB()
        search_engine = SemanticSearch(cache=cache, embedder=embedder, vector_db=vector_db)
        search_engine.index_all_pages()
        logger.info("Re-indexing complete")


def index_command(args):
    """Index documentation for semantic search."""
    logger.info("Starting indexing...")
    
    cache = DocCache(cache_dir="storage/data")
    embedder = DocumentEmbedder()
    vector_db = VectorDB()
    
    if args.clear:
        logger.info("Clearing existing index...")
        vector_db.clear()
    
    search_engine = SemanticSearch(cache=cache, embedder=embedder, vector_db=vector_db)
    search_engine.index_all_pages()
    
    logger.info("Indexing complete")


def stats_command(args):
    """Show cache and index statistics."""
    cache = DocCache(cache_dir="storage/data")
    vector_db = VectorDB()
    
    print("\n" + "=" * 60)
    print("Databricks Docs MCP - Statistics")
    print("=" * 60)
    
    cache_stats = cache.get_cache_stats()
    print(f"\n📚 Document Cache:")
    print(f"  Total Pages: {cache_stats['total_pages']}")
    print(f"  Categories: {cache_stats['categories']}")
    print(f"  Last Crawl: {cache_stats['last_full_crawl'] or 'Never'}")
    print(f"  Cache Directory: {cache_stats['cache_dir']}")
    
    vector_stats = vector_db.get_stats()
    print(f"\n🔍 Vector Database:")
    print(f"  Total Chunks: {vector_stats['total_chunks']}")
    print(f"  Collection: {vector_stats['collection_name']}")
    
    print("\n" + "=" * 60 + "\n")


def server_command(args):
    """Start the MCP server."""
    from databricks_docs_mcp.server import main
    
    # Modify sys.argv to pass arguments to server main
    sys.argv = ['server.py', '--host', args.host, '--port', str(args.port)]
    
    if args.crawl:
        sys.argv.append('--crawl')
    if args.no_scheduler:
        sys.argv.append('--no-scheduler')
    if args.max_pages:
        sys.argv.extend(['--max-pages', str(args.max_pages)])
    
    main()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Databricks Documentation MCP Server - CLI'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl documentation from scratch')
    crawl_parser.add_argument('--max-pages', type=int, help='Maximum pages to crawl')
    crawl_parser.add_argument('--rate-limit', type=float, default=10.0, help='Requests per second (for --fast) or delay between requests (default mode)')
    crawl_parser.add_argument('--no-index', action='store_true', help='Skip indexing after crawl')
    crawl_parser.add_argument('--fast', action='store_true', help='Use fast async crawler (5-10x faster)')
    crawl_parser.add_argument('--concurrent', type=int, default=20, help='Max concurrent requests for --fast mode')
    crawl_parser.set_defaults(func=crawl_command)
    
    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh existing documentation')
    refresh_parser.add_argument('--rate-limit', type=float, default=0.5, help='Delay between requests (seconds)')
    refresh_parser.add_argument('--no-index', action='store_true', help='Skip re-indexing after refresh')
    refresh_parser.set_defaults(func=refresh_command)
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documentation for semantic search')
    index_parser.add_argument('--clear', action='store_true', help='Clear existing index first')
    index_parser.set_defaults(func=index_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=stats_command)
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start MCP server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    server_parser.add_argument('--port', type=int, default=8100, help='Port to bind to')
    server_parser.add_argument('--crawl', action='store_true', help='Perform initial crawl before starting')
    server_parser.add_argument('--max-pages', type=int, help='Maximum pages to crawl (for testing)')
    server_parser.add_argument('--no-scheduler', action='store_true', help='Disable automatic refresh')
    server_parser.set_defaults(func=server_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()

