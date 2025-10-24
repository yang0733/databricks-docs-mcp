"""Pydantic models for documentation storage."""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class DocSection(BaseModel):
    """A section within a documentation page."""
    
    title: str
    level: int  # Heading level (1-6)
    content: str
    anchor: Optional[str] = None


class DocPage(BaseModel):
    """A documentation page."""
    
    url: str
    title: str
    content: str  # Full markdown content
    sections: List[DocSection] = Field(default_factory=list)
    breadcrumbs: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    last_crawled: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "sections": [
                {
                    "title": s.title,
                    "level": s.level,
                    "content": s.content,
                    "anchor": s.anchor,
                }
                for s in self.sections
            ],
            "breadcrumbs": self.breadcrumbs,
            "category": self.category,
            "tags": self.tags,
            "last_updated": self.last_updated.isoformat(),
            "last_crawled": self.last_crawled.isoformat(),
        }


class DocIndex(BaseModel):
    """Master index of all documentation pages."""
    
    pages: Dict[str, DocPage] = Field(default_factory=dict)  # URL -> DocPage
    categories: Dict[str, List[str]] = Field(default_factory=dict)  # Category -> URLs
    last_full_crawl: Optional[datetime] = None
    total_pages: int = 0
    
    def add_page(self, page: DocPage):
        """Add a page to the index."""
        self.pages[page.url] = page
        self.total_pages = len(self.pages)
        
        if page.category:
            if page.category not in self.categories:
                self.categories[page.category] = []
            if page.url not in self.categories[page.category]:
                self.categories[page.category].append(page.url)
    
    def get_page(self, url: str) -> Optional[DocPage]:
        """Get a page by URL."""
        return self.pages.get(url)
    
    def get_pages_by_category(self, category: str) -> List[DocPage]:
        """Get all pages in a category."""
        urls = self.categories.get(category, [])
        return [self.pages[url] for url in urls if url in self.pages]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_pages": self.total_pages,
            "categories": {k: len(v) for k, v in self.categories.items()},
            "last_full_crawl": self.last_full_crawl.isoformat() if self.last_full_crawl else None,
        }


class DocumentChunk(BaseModel):
    """A chunk of documentation for embedding."""
    
    chunk_id: str
    page_url: str
    page_title: str
    section_title: Optional[str] = None
    content: str
    chunk_index: int  # Position within the page
    metadata: Dict = Field(default_factory=dict)

