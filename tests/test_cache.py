"""Tests for document cache."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from storage.cache import DocCache
from storage.models import DocPage, DocSection


class TestDocCache:
    """Test document cache functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.cache = DocCache(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_page(self):
        """Test saving and loading a page."""
        page = DocPage(
            url="https://docs.databricks.com/test",
            title="Test Page",
            content="# Test\n\nContent here",
            sections=[
                DocSection(
                    title="Section 1",
                    level=2,
                    content="Section content"
                )
            ],
            category="test",
        )
        
        # Save page
        self.cache.save_page(page)
        
        # Load page
        loaded = self.cache.get_page(page.url)
        
        assert loaded is not None
        assert loaded.title == "Test Page"
        assert loaded.url == page.url
        assert len(loaded.sections) == 1
        assert loaded.sections[0].title == "Section 1"
    
    def test_get_pages_by_category(self):
        """Test getting pages by category."""
        page1 = DocPage(
            url="https://docs.databricks.com/test1",
            title="Test Page 1",
            content="Content 1",
            category="test-category",
        )
        page2 = DocPage(
            url="https://docs.databricks.com/test2",
            title="Test Page 2",
            content="Content 2",
            category="test-category",
        )
        
        self.cache.save_page(page1)
        self.cache.save_page(page2)
        
        pages = self.cache.get_pages_by_category("test-category")
        
        assert len(pages) == 2
        assert all(p.category == "test-category" for p in pages)
    
    def test_list_categories(self):
        """Test listing categories."""
        page1 = DocPage(
            url="https://docs.databricks.com/test1",
            title="Test 1",
            content="Content",
            category="cat1",
        )
        page2 = DocPage(
            url="https://docs.databricks.com/test2",
            title="Test 2",
            content="Content",
            category="cat2",
        )
        
        self.cache.save_page(page1)
        self.cache.save_page(page2)
        
        categories = self.cache.list_categories()
        
        assert len(categories) == 2
        assert "cat1" in categories
        assert "cat2" in categories
        assert categories["cat1"] == 1
        assert categories["cat2"] == 1

