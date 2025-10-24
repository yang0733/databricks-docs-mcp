"""HTML parser and markdown converter."""

import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime

from databricks_docs_mcp.storage.models import DocPage, DocSection

logger = logging.getLogger(__name__)


class DocParser:
    """Parses HTML documentation pages."""
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def parse_page(self, html: str, url: str) -> Optional[DocPage]:
        """Parse an HTML page into a DocPage.
        
        Args:
            html: HTML content
            url: Page URL
            
        Returns:
            DocPage or None if parsing failed
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content_html = self._extract_main_content(soup)
            if not content_html:
                logger.warning(f"No main content found for {url}")
                return None
            
            # Convert to markdown
            content_md = self._html_to_markdown(content_html)
            
            # Extract sections
            sections = self._extract_sections(content_html)
            
            # Extract breadcrumbs
            breadcrumbs = self._extract_breadcrumbs(soup)
            
            # Infer category from breadcrumbs or URL
            category = self._infer_category(breadcrumbs, url)
            
            # Extract tags/keywords
            tags = self._extract_tags(soup)
            
            return DocPage(
                url=url,
                title=title,
                content=content_md,
                sections=sections,
                breadcrumbs=breadcrumbs,
                category=category,
                tags=tags,
                last_updated=datetime.now(),
                last_crawled=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Failed to parse page {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try different title selectors
        title_tag = soup.find('h1')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Clean up title (remove site name suffix)
            if '|' in title_text:
                title_text = title_text.split('|')[0].strip()
            return title_text
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content area."""
        # Try common content selectors for documentation sites
        selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '#main-content',
            '.content',
            '.documentation-content',
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # Fallback: return body
        return soup.find('body')
    
    def _html_to_markdown(self, html_soup: BeautifulSoup) -> str:
        """Convert HTML to markdown."""
        # Convert to string first
        html_str = str(html_soup)
        
        # Use markdownify with options to preserve code blocks
        markdown = md(
            html_str,
            heading_style="ATX",
            bullets="-",
            code_language="python",  # Default code language
            strip=['script', 'style', 'nav', 'footer'],
        )
        
        # Clean up excessive newlines
        while '\n\n\n' in markdown:
            markdown = markdown.replace('\n\n\n', '\n\n')
        
        return markdown.strip()
    
    def _extract_sections(self, content_soup: BeautifulSoup) -> List[DocSection]:
        """Extract document sections based on headings."""
        sections = []
        
        # Find all headings (h2-h6, skip h1 as it's the title)
        headings = content_soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            level = int(heading.name[1])  # Extract number from 'h2', 'h3', etc.
            title = heading.get_text(strip=True)
            
            # Get anchor/id
            anchor = heading.get('id') or heading.get('name')
            
            # Get content until next heading of same or higher level
            content_parts = []
            for sibling in heading.find_next_siblings():
                # Stop at next heading of same or higher level
                if sibling.name and sibling.name.startswith('h'):
                    sibling_level = int(sibling.name[1])
                    if sibling_level <= level:
                        break
                
                # Add content
                content_parts.append(str(sibling))
            
            # Convert section content to markdown
            section_html = ''.join(content_parts)
            section_md = self._html_to_markdown(BeautifulSoup(section_html, 'lxml'))
            
            sections.append(DocSection(
                title=title,
                level=level,
                content=section_md,
                anchor=anchor,
            ))
        
        return sections
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[str]:
        """Extract breadcrumb navigation."""
        breadcrumbs = []
        
        # Try common breadcrumb selectors
        breadcrumb_selectors = [
            'nav[aria-label="Breadcrumb"]',
            '.breadcrumb',
            '.breadcrumbs',
            '[role="navigation"] ol',
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb_nav = soup.select_one(selector)
            if breadcrumb_nav:
                # Extract text from links
                links = breadcrumb_nav.find_all('a')
                breadcrumbs = [link.get_text(strip=True) for link in links]
                break
        
        return breadcrumbs
    
    def _infer_category(self, breadcrumbs: List[str], url: str) -> Optional[str]:
        """Infer category from breadcrumbs or URL."""
        if breadcrumbs and len(breadcrumbs) > 0:
            # Use first breadcrumb as category
            return breadcrumbs[0]
        
        # Try to extract from URL path
        # e.g., /aws/en/getting-started/... -> "getting-started"
        parts = url.split('/')
        if len(parts) > 4:
            # Skip protocol, domain, aws, en
            return parts[4] if len(parts) > 4 else None
        
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags/keywords from meta tags."""
        tags = []
        
        # Try meta keywords
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            keywords = keywords_meta['content'].split(',')
            tags.extend([k.strip() for k in keywords])
        
        # Try meta tags
        tags_meta = soup.find('meta', {'name': 'tags'})
        if tags_meta and tags_meta.get('content'):
            meta_tags = tags_meta['content'].split(',')
            tags.extend([t.strip() for t in meta_tags])
        
        return list(set(tags))  # Remove duplicates

