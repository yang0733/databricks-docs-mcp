"""Documentation scraper for Databricks docs."""

import logging
import time
from typing import Set, Optional, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from databricks_docs_mcp.storage.cache import DocCache
from databricks_docs_mcp.storage.models import DocPage
from databricks_docs_mcp.crawler.parser import DocParser

logger = logging.getLogger(__name__)


class DocScraper:
    """Scrapes Databricks documentation."""
    
    def __init__(
        self,
        base_url: str = "https://docs.databricks.com/aws/en/",
        cache: Optional[DocCache] = None,
        rate_limit: float = 0.5,
    ):
        """Initialize scraper.
        
        Args:
            base_url: Base URL to start crawling from
            cache: Cache instance (creates new if not provided)
            rate_limit: Delay between requests in seconds
        """
        self.base_url = base_url
        self.cache = cache or DocCache()
        self.parser = DocParser()
        self.rate_limit = rate_limit
        
        # Track visited URLs
        self.visited: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        
        # Stats
        self.pages_crawled = 0
        self.errors = 0
    
    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled.
        
        Args:
            url: URL to check
            
        Returns:
            True if should crawl
        """
        # Skip if already visited
        if url in self.visited:
            return False
        
        # Only crawl docs.databricks.com/aws/en pages
        parsed = urlparse(url)
        if parsed.netloc != "docs.databricks.com":
            return False
        
        if not parsed.path.startswith("/aws/en"):
            return False
        
        # Skip certain patterns
        skip_patterns = [
            '/api/',  # API reference
            '/release-notes/',  # Release notes (too many)
            '#',  # Anchors
            '?',  # Query parameters
            '.pdf',
            '.zip',
            '.tar',
        ]
        
        for pattern in skip_patterns:
            if pattern in url:
                return False
        
        return True
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page HTML.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            
            headers = {
                'User-Agent': 'DatabricksDocsMCP/1.0 (Documentation Indexer)'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            self.errors += 1
            return None
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Resolve relative URLs
                absolute_url = urljoin(base_url, href)
                
                # Clean URL (remove anchors and query params)
                parsed = urlparse(absolute_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                # Remove trailing slash for consistency
                clean_url = clean_url.rstrip('/')
                
                if self.should_crawl(clean_url):
                    links.append(clean_url)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Failed to extract links: {e}")
            return []
    
    def crawl_page(self, url: str) -> Optional[DocPage]:
        """Crawl a single page.
        
        Args:
            url: URL to crawl
            
        Returns:
            DocPage or None if failed
        """
        # Mark as visited
        self.visited.add(url)
        
        # Fetch HTML
        html = self.fetch_page(url)
        if not html:
            return None
        
        # Parse page
        page = self.parser.parse_page(html, url)
        if not page:
            return None
        
        # Save to cache
        self.cache.save_page(page)
        self.pages_crawled += 1
        
        logger.info(f"Crawled [{self.pages_crawled}]: {page.title}")
        
        # Extract and queue new links
        links = self.extract_links(html, url)
        for link in links:
            if link not in self.visited and link not in self.to_visit:
                self.to_visit.append(link)
        
        return page
    
    def crawl_all(self, max_pages: Optional[int] = None) -> int:
        """Crawl all documentation pages.
        
        Args:
            max_pages: Maximum pages to crawl (None for unlimited)
            
        Returns:
            Number of pages crawled
        """
        logger.info(f"Starting crawl from {self.base_url}")
        
        while self.to_visit:
            # Check max pages limit
            if max_pages and self.pages_crawled >= max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break
            
            # Get next URL
            url = self.to_visit.pop(0)
            
            # Skip if already visited
            if url in self.visited:
                continue
            
            # Crawl page
            self.crawl_page(url)
            
            # Log progress
            if self.pages_crawled % 10 == 0:
                logger.info(
                    f"Progress: {self.pages_crawled} pages, "
                    f"{len(self.to_visit)} queued, "
                    f"{self.errors} errors"
                )
        
        # Update cache metadata
        self.cache.update_crawl_time()
        
        logger.info(
            f"Crawl complete: {self.pages_crawled} pages, "
            f"{self.errors} errors"
        )
        
        return self.pages_crawled
    
    def refresh_page(self, url: str) -> bool:
        """Refresh a single page.
        
        Args:
            url: URL to refresh
            
        Returns:
            True if successful
        """
        try:
            page = self.crawl_page(url)
            return page is not None
        except Exception as e:
            logger.error(f"Failed to refresh {url}: {e}")
            return False
    
    def incremental_update(self) -> int:
        """Perform incremental update of all cached pages.
        
        Returns:
            Number of pages updated
        """
        logger.info("Starting incremental update")
        
        pages = self.cache.get_all_pages()
        updated = 0
        
        for page in pages:
            if self.refresh_page(page.url):
                updated += 1
            
            # Log progress
            if updated % 20 == 0:
                logger.info(f"Updated {updated}/{len(pages)} pages")
        
        logger.info(f"Incremental update complete: {updated} pages updated")
        return updated

