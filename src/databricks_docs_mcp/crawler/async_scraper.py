"""Fast async documentation scraper for Databricks docs."""

import asyncio
import logging
from typing import Optional, List, Set
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.storage.models import DocPage
from databricks_docs_mcp.crawler.parser import DocParser

logger = logging.getLogger(__name__)


class AsyncDocScraper:
    """Fast async scraper for Databricks documentation."""
    
    def __init__(
        self,
        cache: Optional[DocCache] = None,
        max_concurrent: int = 20,
        rate_limit_per_second: float = 10.0,
        timeout: float = 30.0,
    ):
        """Initialize async scraper.
        
        Args:
            cache: Cache instance (creates new if not provided)
            max_concurrent: Maximum concurrent requests
            rate_limit_per_second: Maximum requests per second
            timeout: Request timeout in seconds
        """
        self.cache = cache or DocCache()
        self.parser = DocParser()
        self.max_concurrent = max_concurrent
        self.rate_limit_per_second = rate_limit_per_second
        self.timeout = timeout
        
        # Stats
        self.pages_crawled = 0
        self.errors = 0
        self.failed_urls: List[str] = []
        
        # Semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """Fetch and parse sitemap to get all URLs.
        
        Args:
            sitemap_url: URL of the sitemap
            
        Returns:
            List of URLs from sitemap
        """
        logger.info(f"Fetching sitemap from {sitemap_url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(sitemap_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'xml')
                urls = [loc.text for loc in soup.find_all('loc')]
                
                logger.info(f"Found {len(urls)} URLs in sitemap")
                return urls
                
            except Exception as e:
                logger.error(f"Failed to fetch sitemap: {e}")
                return []
    
    async def fetch_page(self, client: httpx.AsyncClient, url: str) -> Optional[tuple[str, str]]:
        """Fetch a single page.
        
        Args:
            client: HTTP client
            url: URL to fetch
            
        Returns:
            Tuple of (url, html) or None if failed
        """
        try:
            # Rate limiting with semaphore
            async with self.semaphore:
                response = await client.get(
                    url,
                    headers={'User-Agent': 'DatabricksDocsMCP/1.0 (Documentation Indexer)'},
                    follow_redirects=True
                )
                response.raise_for_status()
                
                # Small delay to respect rate limit
                await asyncio.sleep(1.0 / self.rate_limit_per_second)
                
                return (url, response.text)
                
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            self.errors += 1
            self.failed_urls.append(url)
            return None
    
    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled.
        
        Args:
            url: URL to check
            
        Returns:
            True if should crawl
        """
        parsed = urlparse(url)
        
        # Only crawl docs.databricks.com/aws/en pages
        if parsed.netloc != "docs.databricks.com":
            return False
        
        if not parsed.path.startswith("/aws/en"):
            return False
        
        # Skip certain patterns
        skip_patterns = [
            '/release-notes/',  # Too many release notes
            '.pdf', '.zip', '.tar',
        ]
        
        for pattern in skip_patterns:
            if pattern in url:
                return False
        
        return True
    
    async def process_page(self, url: str, html: str) -> Optional[DocPage]:
        """Process and save a page.
        
        Args:
            url: Page URL
            html: Page HTML
            
        Returns:
            DocPage or None if failed
        """
        try:
            # Parse page
            page = self.parser.parse_page(html, url)
            if not page:
                return None
            
            # Save to cache (synchronous, but fast)
            self.cache.save_page(page)
            self.pages_crawled += 1
            
            if self.pages_crawled % 50 == 0:
                logger.info(
                    f"Progress: {self.pages_crawled} pages crawled, "
                    f"{self.errors} errors"
                )
            
            return page
            
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            self.errors += 1
            return None
    
    async def crawl_batch(
        self,
        client: httpx.AsyncClient,
        urls: List[str]
    ) -> List[DocPage]:
        """Crawl a batch of URLs concurrently.
        
        Args:
            client: HTTP client
            urls: List of URLs to crawl
            
        Returns:
            List of successfully crawled pages
        """
        # Fetch all pages concurrently
        tasks = [self.fetch_page(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # Process successful fetches
        pages = []
        for result in results:
            if result:
                url, html = result
                page = await self.process_page(url, html)
                if page:
                    pages.append(page)
        
        return pages
    
    async def crawl_all(
        self,
        sitemap_url: str = "https://docs.databricks.com/aws/en/sitemap.xml",
        max_pages: Optional[int] = None,
        batch_size: int = 100,
    ) -> int:
        """Crawl all documentation pages from sitemap.
        
        Args:
            sitemap_url: URL of the sitemap
            max_pages: Maximum pages to crawl (None for unlimited)
            batch_size: Number of pages to process in each batch
            
        Returns:
            Number of pages crawled
        """
        logger.info(f"Starting async crawl from sitemap")
        start_time = asyncio.get_event_loop().time()
        
        # Fetch sitemap
        all_urls = await self.fetch_sitemap(sitemap_url)
        
        # Filter URLs
        urls_to_crawl = [url for url in all_urls if self.should_crawl(url)]
        logger.info(f"Filtered to {len(urls_to_crawl)} URLs to crawl")
        
        # Apply max_pages limit
        if max_pages:
            urls_to_crawl = urls_to_crawl[:max_pages]
            logger.info(f"Limited to {len(urls_to_crawl)} pages")
        
        # Create HTTP client
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Process in batches
            for i in range(0, len(urls_to_crawl), batch_size):
                batch = urls_to_crawl[i:i + batch_size]
                logger.info(
                    f"Processing batch {i//batch_size + 1}/{(len(urls_to_crawl)-1)//batch_size + 1} "
                    f"({len(batch)} URLs)"
                )
                
                await self.crawl_batch(client, batch)
                
                # Check if we've hit max_pages
                if max_pages and self.pages_crawled >= max_pages:
                    logger.info(f"Reached max pages limit: {max_pages}")
                    break
        
        # Update cache metadata
        self.cache.update_crawl_time()
        
        elapsed = asyncio.get_event_loop().time() - start_time
        pages_per_sec = self.pages_crawled / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"Crawl complete: {self.pages_crawled} pages in {elapsed:.1f}s "
            f"({pages_per_sec:.1f} pages/sec), {self.errors} errors"
        )
        
        if self.failed_urls:
            logger.warning(f"Failed URLs ({len(self.failed_urls)}): {self.failed_urls[:10]}")
        
        return self.pages_crawled
    
    async def incremental_update(self) -> int:
        """Perform incremental update of all cached pages.
        
        Returns:
            Number of pages updated
        """
        logger.info("Starting incremental update")
        
        # Get all cached page URLs
        pages = self.cache.get_all_pages()
        urls = [page.url for page in pages]
        
        logger.info(f"Updating {len(urls)} cached pages")
        
        # Crawl all URLs
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            await self.crawl_batch(client, urls)
        
        logger.info(f"Incremental update complete: {self.pages_crawled} pages updated")
        return self.pages_crawled


def run_async_crawl(
    max_pages: Optional[int] = None,
    max_concurrent: int = 20,
    rate_limit: float = 10.0,
) -> int:
    """Run async crawl in a new event loop.
    
    Args:
        max_pages: Maximum pages to crawl
        max_concurrent: Maximum concurrent requests
        rate_limit: Requests per second
        
    Returns:
        Number of pages crawled
    """
    scraper = AsyncDocScraper(
        max_concurrent=max_concurrent,
        rate_limit_per_second=rate_limit,
    )
    
    return asyncio.run(scraper.crawl_all(max_pages=max_pages))

