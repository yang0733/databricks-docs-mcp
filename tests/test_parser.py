"""Tests for HTML parser."""

import pytest
from bs4 import BeautifulSoup

from databricks_docs_mcp.crawler.parser import DocParser


class TestDocParser:
    """Test HTML parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DocParser()
    
    def test_extract_title(self):
        """Test title extraction."""
        html = """
        <html>
        <head><title>Test Page | Databricks</title></head>
        <body><h1>Test Page</h1></body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        title = self.parser._extract_title(soup)
        
        assert title == "Test Page"
    
    def test_extract_sections(self):
        """Test section extraction."""
        html = """
        <div>
            <h2 id="section-1">Section 1</h2>
            <p>Content 1</p>
            <h2 id="section-2">Section 2</h2>
            <p>Content 2</p>
        </div>
        """
        soup = BeautifulSoup(html, 'lxml')
        sections = self.parser._extract_sections(soup)
        
        assert len(sections) == 2
        assert sections[0].title == "Section 1"
        assert sections[0].level == 2
        assert sections[0].anchor == "section-1"
        assert "Content 1" in sections[0].content
    
    def test_html_to_markdown(self):
        """Test HTML to markdown conversion."""
        html = BeautifulSoup("<p><strong>Bold</strong> text</p>", 'lxml')
        markdown = self.parser._html_to_markdown(html)
        
        assert "**Bold**" in markdown or "Bold" in markdown
        assert "text" in markdown

