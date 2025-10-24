"""Local cache management for documentation pages."""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from databricks_docs_mcp.storage.models import DocPage, DocIndex

logger = logging.getLogger(__name__)


class DocCache:
    """Manages local cache of documentation pages."""
    
    def __init__(self, cache_dir: str = "storage/data"):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = Path(cache_dir)
        self.pages_dir = self.cache_dir / "pages"
        self.index_file = self.cache_dir / "index.json"
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        self.index = self._load_index()
    
    def _load_index(self) -> DocIndex:
        """Load index from disk or create new one."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruct DocIndex
                index = DocIndex()
                index.total_pages = data.get("total_pages", 0)
                index.categories = data.get("categories", {})
                
                if data.get("last_full_crawl"):
                    index.last_full_crawl = datetime.fromisoformat(data["last_full_crawl"])
                
                # Load all pages
                for page_file in self.pages_dir.glob("*.json"):
                    try:
                        page = self.load_page_from_file(page_file)
                        if page:
                            index.pages[page.url] = page
                    except Exception as e:
                        logger.warning(f"Failed to load page {page_file}: {e}")
                
                logger.info(f"Loaded cache index with {len(index.pages)} pages")
                return index
                
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new index.")
        
        return DocIndex()
    
    def _save_index(self):
        """Save index to disk."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_pages": self.index.total_pages,
                    "categories": self.index.categories,
                    "last_full_crawl": self.index.last_full_crawl.isoformat() 
                        if self.index.last_full_crawl else None,
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _url_to_filename(self, url: str) -> str:
        """Convert URL to safe filename."""
        # Remove protocol and replace special chars
        filename = url.replace("https://", "").replace("http://", "")
        filename = filename.replace("/", "_").replace(":", "_").replace("?", "_")
        filename = filename.replace("#", "_").replace("&", "_")
        return filename[:200] + ".json"  # Limit length
    
    def save_page(self, page: DocPage):
        """Save a page to cache.
        
        Args:
            page: Page to save
        """
        try:
            # Save to index
            self.index.add_page(page)
            
            # Save page data
            filename = self._url_to_filename(page.url)
            filepath = self.pages_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(page.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Save index
            self._save_index()
            
            logger.debug(f"Saved page: {page.title}")
            
        except Exception as e:
            logger.error(f"Failed to save page {page.url}: {e}")
    
    def load_page_from_file(self, filepath: Path) -> Optional[DocPage]:
        """Load a page from file.
        
        Args:
            filepath: Path to page JSON file
            
        Returns:
            DocPage or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse dates
            if "last_updated" in data and isinstance(data["last_updated"], str):
                data["last_updated"] = datetime.fromisoformat(data["last_updated"])
            if "last_crawled" in data and isinstance(data["last_crawled"], str):
                data["last_crawled"] = datetime.fromisoformat(data["last_crawled"])
            
            return DocPage(**data)
            
        except Exception as e:
            logger.error(f"Failed to load page from {filepath}: {e}")
            return None
    
    def get_page(self, url: str) -> Optional[DocPage]:
        """Get a page from cache by URL.
        
        Args:
            url: Page URL
            
        Returns:
            DocPage or None if not found
        """
        return self.index.get_page(url)
    
    def get_all_pages(self) -> List[DocPage]:
        """Get all cached pages.
        
        Returns:
            List of all pages
        """
        return list(self.index.pages.values())
    
    def get_pages_by_category(self, category: str) -> List[DocPage]:
        """Get pages by category.
        
        Args:
            category: Category name
            
        Returns:
            List of pages in category
        """
        return self.index.get_pages_by_category(category)
    
    def list_categories(self) -> Dict[str, int]:
        """List all categories with page counts.
        
        Returns:
            Dict of category -> page count
        """
        return {cat: len(urls) for cat, urls in self.index.categories.items()}
    
    def update_crawl_time(self):
        """Update last full crawl time."""
        self.index.last_full_crawl = datetime.now()
        self._save_index()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        return {
            "total_pages": self.index.total_pages,
            "categories": len(self.index.categories),
            "last_full_crawl": self.index.last_full_crawl.isoformat() 
                if self.index.last_full_crawl else None,
            "cache_dir": str(self.cache_dir.absolute()),
        }
    
    def search_local(self, query: str, limit: int = 10) -> List[DocPage]:
        """Simple keyword search in cached pages.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching pages
        """
        query_lower = query.lower()
        results = []
        
        for page in self.index.pages.values():
            # Search in title and content
            if (query_lower in page.title.lower() or 
                query_lower in page.content.lower()):
                results.append(page)
                
                if len(results) >= limit:
                    break
        
        return results

