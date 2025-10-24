# Usage Examples

## Example Queries for AI IDEs

### Basic Search

```
"How do I create a Delta table?"
"Show me Unity Catalog documentation"
"Find guides about MLflow"
"What is Auto Loader?"
```

### Category Exploration

```
"What documentation is available in the getting-started category?"
"Show me all SQL related pages"
"List machine learning documentation"
```

### Finding Related Content

```
"Show me pages related to Delta Lake overview"
"Find similar documentation to the Spark configuration guide"
"What else should I read after the quickstart guide?"
```

### Getting Recommendations

```
"I need to set up a streaming pipeline with Delta Lake"
"Suggest docs for optimizing Spark jobs"
"What should I know about Unity Catalog governance?"
```

### Quickstart Guides

```
"Find getting started guides for Delta Lake"
"Show me MLflow quickstart"
"Where can I learn about Databricks SQL basics?"
```

---

## Direct Tool Usage Examples

### Using MCP Tools Directly

```python
# Search documentation
search_docs(
    query="How to create a Delta table?",
    limit=10
)

# Get specific page
get_page(
    url="https://docs.databricks.com/aws/en/getting-started/quick-start"
)

# Search within category
search_by_category(
    category="delta",
    query="performance optimization",
    limit=5
)

# Find related pages
recommend_related(
    page_url="https://docs.databricks.com/aws/en/delta/",
    limit=5
)

# Get contextual suggestions
suggest_docs(
    context="I need to build a real-time streaming pipeline",
    limit=5
)

# Find quickstart guides
get_quickstart(
    topic="mlflow"
)

# Explore category
explore_category(
    category="machine-learning",
    limit=20
)

# Get popular topics
get_popular_topics()

# Check server status
get_server_status()
```

---

## MCP Resources Access

### Browse All Documentation

```
Resource URI: databricks-docs://aws/en/index
```

Returns: Complete index of all documentation organized by category

### Access Specific Page

```
Resource URI: databricks-docs://aws/en/getting-started/quick-start
Resource URI: databricks-docs://aws/en/delta/tutorial
Resource URI: databricks-docs://aws/en/machine-learning/train-model/
```

Returns: Full page content in markdown format

### List Categories

```
Resource URI: databricks-docs://categories
```

Returns: All documentation categories with page counts

---

## CLI Usage Examples

### Initial Setup

```bash
# Crawl all documentation (first time setup)
python -m databricks_docs_mcp crawl

# Crawl with limit for testing
python -m databricks_docs_mcp crawl --max-pages 100

# Crawl without indexing
python -m databricks_docs_mcp crawl --no-index
```

### Maintenance

```bash
# Refresh documentation (incremental update)
python -m databricks_docs_mcp refresh

# Refresh without re-indexing
python -m databricks_docs_mcp refresh --no-index

# Re-index all pages
python -m databricks_docs_mcp index

# Clear and rebuild index
python -m databricks_docs_mcp index --clear
```

### Server Management

```bash
# Start server (interactive)
./start_server.sh

# Start server with custom port
python -m databricks_docs_mcp server --port 8200

# Start with initial crawl
python -m databricks_docs_mcp server --crawl

# Start without scheduler
python -m databricks_docs_mcp server --no-scheduler

# Start with page limit (testing)
python -m databricks_docs_mcp server --crawl --max-pages 50
```

### Statistics

```bash
# View cache and index stats
python -m databricks_docs_mcp stats
```

Output example:
```
============================================================
Databricks Docs MCP - Statistics
============================================================

📚 Document Cache:
  Total Pages: 1247
  Categories: 18
  Last Crawl: 2024-10-24T14:30:00
  Cache Directory: /path/to/storage/data

🔍 Vector Database:
  Total Chunks: 3891
  Collection: databricks_docs

============================================================
```

---

## Python API Examples

### Using Components Directly

```python
from storage.cache import DocCache
from embeddings.search import SemanticSearch

# Initialize
cache = DocCache(cache_dir="storage/data")
search = SemanticSearch(cache=cache)

# Perform search
results = search.search("Delta Lake performance", limit=10)

for result in results:
    print(f"Title: {result['page_title']}")
    print(f"URL: {result['page_url']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Snippet: {result['content_snippet']}")
    print("---")
```

### Manual Crawling

```python
from crawler.scraper import DocScraper
from storage.cache import DocCache

# Initialize
cache = DocCache()
scraper = DocScraper(cache=cache)

# Crawl specific page
page = scraper.crawl_page("https://docs.databricks.com/aws/en/delta/")

if page:
    print(f"Crawled: {page.title}")
    print(f"Sections: {len(page.sections)}")
    print(f"Category: {page.category}")
```

### Programmatic Indexing

```python
from embeddings.embedder import DocumentEmbedder
from embeddings.vector_db import VectorDB
from storage.cache import DocCache

# Initialize
cache = DocCache()
embedder = DocumentEmbedder()
vector_db = VectorDB()

# Get a page
page = cache.get_page("https://docs.databricks.com/aws/en/delta/")

# Chunk and embed
chunks = embedder.chunk_page(page)
embeddings = embedder.embed_chunks(chunks)

# Add to vector DB
vector_db.add_chunks(chunks, embeddings)

print(f"Indexed {len(chunks)} chunks")
```

---

## Integration Examples

### Cursor Integration

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "url": "http://localhost:8100/mcp",
      "description": "Databricks AWS Documentation"
    }
  }
}
```

Then in Cursor:
- "Search Databricks docs for Delta Lake"
- "Find Unity Catalog permissions guide"
- "Show me MLflow tracking examples"

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "url": "http://localhost:8100/mcp"
    }
  }
}
```

Then in Claude Desktop:
- Ask natural language questions about Databricks
- Request specific documentation pages
- Get recommendations based on your task

---

## Advanced Usage

### Custom Embedding Model

```python
from embeddings.embedder import DocumentEmbedder

# Use different model
embedder = DocumentEmbedder(model_name="all-mpnet-base-v2")
```

### Category Filtering

```python
# Search only in specific category
results = search.search(
    query="optimization techniques",
    category="delta",
    limit=10
)
```

### Finding Similar Pages

```python
# Find pages similar to a reference page
similar = search.find_similar_pages(
    page_url="https://docs.databricks.com/aws/en/delta/optimize",
    limit=5
)
```

### Manual Refresh Trigger

Via MCP Tool:
```python
trigger_refresh()
```

Via CLI:
```bash
python -m databricks_docs_mcp refresh
```

---

## Workflow Examples

### Daily Development Workflow

```bash
# Morning: Start server
./start_server.sh

# During development: Use AI IDE for queries
# "How do I optimize this Delta merge operation?"
# "Show me examples of structured streaming"

# Evening: Check stats
python -m databricks_docs_mcp stats

# Server auto-refreshes at 2 AM
```

### Initial Setup Workflow

```bash
# Step 1: Clone/download project
cd databricks_docs_mcp

# Step 2: Run initial crawl
./start_server.sh
# Answer 'y' when prompted to crawl

# Step 3: Wait for crawl to complete (10-30 minutes)

# Step 4: Configure AI IDE
# Add MCP URL to IDE config

# Step 5: Test queries
# Try searching for documentation in your IDE

# Step 6: Done! Server will auto-refresh daily
```

### Maintenance Workflow

```bash
# Weekly: Check status
python -m databricks_docs_mcp stats

# Monthly: Force full refresh
python -m databricks_docs_mcp crawl
python -m databricks_docs_mcp index --clear

# As needed: Restart server
pkill -f "python.*server.py"
./start_server.sh
```

---

## Tips & Best Practices

### Search Tips

1. **Be specific**: "How to optimize Delta Lake merge operations" vs "Delta Lake"
2. **Use keywords**: Include product names (Delta Lake, MLflow, Unity Catalog)
3. **Ask questions**: Natural language questions work well
4. **Try variations**: If first search doesn't help, rephrase

### Performance Tips

1. Limit results for faster responses
2. Use category filters when possible
3. Cache frequently accessed pages
4. Schedule refreshes during off-hours

### Troubleshooting Tips

1. Check logs: `tail -f docs_mcp_server.log`
2. Verify cache: `python -m databricks_docs_mcp stats`
3. Re-index if search quality degrades
4. Restart server after major updates

