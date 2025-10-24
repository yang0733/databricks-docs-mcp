"""Generate embeddings for documentation chunks."""

import logging
from typing import List
import hashlib

from sentence_transformers import SentenceTransformer

from databricks_docs_mcp.storage.models import DocPage, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Generates embeddings for documentation."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedder.
        
        Args:
            model_name: Sentence transformer model name
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Embedding model loaded")
    
    def chunk_page(self, page: DocPage, max_tokens: int = 512) -> List[DocumentChunk]:
        """Chunk a page into smaller pieces for embedding.
        
        Args:
            page: Page to chunk
            max_tokens: Maximum tokens per chunk (approximate)
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        # If page has sections, chunk by section
        if page.sections:
            for idx, section in enumerate(page.sections):
                # Skip empty sections
                if not section.content.strip():
                    continue
                
                # Create chunk ID
                chunk_id = self._generate_chunk_id(page.url, idx)
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    page_url=page.url,
                    page_title=page.title,
                    section_title=section.title,
                    content=section.content,
                    chunk_index=idx,
                    metadata={
                        "category": page.category,
                        "breadcrumbs": page.breadcrumbs,
                        "tags": page.tags,
                        "section_level": section.level,
                        "anchor": section.anchor,
                    }
                )
                chunks.append(chunk)
        else:
            # No sections, chunk by paragraphs or fixed size
            content_chunks = self._chunk_text(page.content, max_tokens)
            
            for idx, content in enumerate(content_chunks):
                chunk_id = self._generate_chunk_id(page.url, idx)
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    page_url=page.url,
                    page_title=page.title,
                    section_title=None,
                    content=content,
                    chunk_index=idx,
                    metadata={
                        "category": page.category,
                        "breadcrumbs": page.breadcrumbs,
                        "tags": page.tags,
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_text(self, text: str, max_tokens: int) -> List[str]:
        """Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
            max_tokens: Max tokens per chunk (rough estimate)
            
        Returns:
            List of text chunks
        """
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > max_chars and current_chunk:
                # Start new chunk
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # Add last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _generate_chunk_id(self, url: str, index: int) -> str:
        """Generate unique chunk ID.
        
        Args:
            url: Page URL
            index: Chunk index
            
        Returns:
            Unique chunk ID
        """
        # Create hash of URL + index
        content = f"{url}::{index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def embed_chunk(self, chunk: DocumentChunk) -> List[float]:
        """Generate embedding for a chunk.
        
        Args:
            chunk: Document chunk
            
        Returns:
            Embedding vector
        """
        # Combine title and content for better context
        text = f"{chunk.page_title}"
        if chunk.section_title:
            text += f" - {chunk.section_title}"
        text += f"\n\n{chunk.content}"
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """Generate embeddings for multiple chunks (batched).
        
        Args:
            chunks: List of document chunks
            
        Returns:
            List of embedding vectors
        """
        if not chunks:
            return []
        
        # Prepare texts
        texts = []
        for chunk in chunks:
            text = f"{chunk.page_title}"
            if chunk.section_title:
                text += f" - {chunk.section_title}"
            text += f"\n\n{chunk.content}"
            texts.append(text)
        
        # Batch encode
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10,
            batch_size=32,
        )
        
        return [emb.tolist() for emb in embeddings]
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query.
        
        Args:
            query: Search query
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()

