"""Tests for document embedder."""

import pytest

from embeddings.embedder import DocumentEmbedder
from storage.models import DocPage, DocSection


class TestDocumentEmbedder:
    """Test document embedder functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Note: This will download the model on first run
        self.embedder = DocumentEmbedder(model_name="all-MiniLM-L6-v2")
    
    def test_chunk_page_with_sections(self):
        """Test chunking a page with sections."""
        page = DocPage(
            url="https://docs.databricks.com/test",
            title="Test Page",
            content="Full content",
            sections=[
                DocSection(
                    title="Section 1",
                    level=2,
                    content="Content of section 1"
                ),
                DocSection(
                    title="Section 2",
                    level=2,
                    content="Content of section 2"
                ),
            ],
            category="test",
        )
        
        chunks = self.embedder.chunk_page(page)
        
        assert len(chunks) == 2
        assert chunks[0].page_title == "Test Page"
        assert chunks[0].section_title == "Section 1"
        assert chunks[1].section_title == "Section 2"
    
    def test_embed_query(self):
        """Test query embedding generation."""
        query = "How to create a Delta table?"
        
        embedding = self.embedder.embed_query(query)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_chunks(self):
        """Test batch chunk embedding."""
        page = DocPage(
            url="https://docs.databricks.com/test",
            title="Test Page",
            content="Content",
            sections=[
                DocSection(title="Section 1", level=2, content="Content 1"),
                DocSection(title="Section 2", level=2, content="Content 2"),
            ],
        )
        
        chunks = self.embedder.chunk_page(page)
        embeddings = self.embedder.embed_chunks(chunks)
        
        assert len(embeddings) == len(chunks)
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)

