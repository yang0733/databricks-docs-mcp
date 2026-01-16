# Databricks Documentation MCP Server 📚

> **Make Databricks documentation instantly accessible to AI assistants through the Model Context Protocol (MCP)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)

> **⚠️ DISCLAIMER**: This is **NOT** an official Databricks product and is **NOT** supported by Databricks. This is a community project that crawls and indexes publicly available Databricks documentation to provide MCP integration. Use at your own risk. For official Databricks support, please contact Databricks directly.

This MCP server provides AI assistants like Claude, GPT-4, and others with semantic search access to the complete Databricks AWS documentation (~3,200 pages). It crawls, caches, indexes, and serves documentation through both MCP tools and resources.

## ✨ Features

- 🔍 **Semantic Search**: Find relevant documentation using natural language queries
- 📦 **Complete Coverage**: Access to 3,181+ pages of Databricks AWS documentation
- ⚡ **Fast Async Crawler**: 5-10x faster than traditional crawlers (crawls full docs in ~5-7 minutes)
- 🗄️ **Local Caching**: Crawled pages stored locally for offline access and fast queries
- 🧠 **Vector Search**: Powered by ChromaDB and sentence-transformers embeddings
- 🔄 **Auto-Refresh**: Optional daily documentation refresh
- 🛠️ **10 MCP Tools**: Search, recommend, explore documentation programmatically
- 📖 **MCP Resources**: Browse documentation directly
- 🎯 **AI IDE Compatible**: Works with Cursor, Claude Code, and other MCP clients

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/databricks-docs-mcp.git
cd databricks-docs-mcp

# Quick start script (installs dependencies, crawls docs, starts server)
chmod +x start_server.sh
./start_server.sh
```

**⏱️ Initial Setup Time Expectations:**
- **First-time crawl**: ~5-7 minutes (3,181 pages with fast async crawler)
- **Embedding generation**: ~10-15 minutes (creating vector embeddings for all pages)
- **Total first run**: ~15-22 minutes
- **Subsequent starts**: ~5-10 seconds (uses cached data)

The server will automatically crawl and index documentation on first run. Grab a coffee! ☕

### Manual Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync --group dev

# Crawl documentation (fast mode) - Takes ~5-7 minutes
uv run python -m databricks_docs_mcp crawl --fast

# Start MCP server (first start: ~10-15 min for indexing, subsequent: ~5-10 sec)
uv run python -m databricks_docs_mcp.server --no-scheduler
```

> **💡 Tip**: The `--fast` flag uses the async crawler for 5-10x faster crawling. The server automatically creates embeddings on first startup.

## 📖 Usage

### Available MCP Tools

The server exposes 10 MCP tools for AI assistants:

1. **`search_docs`** - Search documentation with semantic search
2. **`get_page`** - Retrieve a specific documentation page
3. **`list_categories`** - List all documentation categories
4. **`search_by_category`** - Search within a specific category
5. **`get_page_sections`** - Get page table of contents
6. **`recommend_related`** - Find related documentation pages
7. **`suggest_docs`** - Get suggestions based on context
8. **`get_quickstart`** - Find quickstart guides for topics
9. **`explore_category`** - Browse all pages in a category
10. **`get_popular_topics`** - Get most popular documentation topics

### Example Queries in AI IDEs

```
"Search Databricks docs for Lakeflow Connect with Salesforce"
"How do I use MLflow to track experiments?"
"Show me Unity Catalog best practices"
"What are Delta Lake optimization techniques?"
```

### CLI Commands

```bash
# Crawl documentation
python -m databricks_docs_mcp crawl --fast --max-pages 1000

# Check statistics
python -m databricks_docs_mcp stats

# Reindex existing data
python -m databricks_docs_mcp index

# Refresh documentation
python -m databricks_docs_mcp refresh

# Start server
python -m databricks_docs_mcp server --no-scheduler
```

## 🔧 Configuration

### Configure in AI IDEs

#### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "url": "http://localhost:8100/mcp"
    }
  }
}
```

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "command": "python",
      "args": ["-m", "databricks_docs_mcp", "server", "--no-scheduler"],
      "cwd": "/path/to/databricks_docs_mcp",
      "env": {
        "PYTHONPATH": "/path/to/parent/directory"
      }
    }
  }
}
```

## 🏗️ Architecture

```
databricks_docs_mcp/
├── crawler/            # Web scraping and parsing
│   ├── scraper.py     # Original sequential crawler
│   ├── async_scraper.py   # Fast async crawler (5-10x faster)
│   ├── parser.py      # HTML to Markdown conversion
│   └── scheduler.py   # Daily auto-refresh scheduler
├── embeddings/        # Vector search components
│   ├── embedder.py    # Sentence-transformer embeddings
│   ├── vector_db.py   # ChromaDB wrapper
│   └── search.py      # Semantic search engine
├── resources/         # MCP resources
│   └── docs_resources.py
├── storage/           # Data models and caching
│   ├── models.py      # Pydantic data models
│   ├── cache.py       # Local cache management
│   └── data/          # Cached documentation
├── tools/             # MCP tools
│   ├── search.py      # Search tools
│   └── recommend.py   # Recommendation tools
├── tests/             # Unit tests
├── server.py          # FastMCP server
└── __main__.py        # CLI entry point
```

## 📊 Performance

- **Crawl Speed**: ~5-7 minutes for 3,181 pages (async mode)
- **Indexing Speed**: ~5-6 minutes for full documentation
- **Search Latency**: <100ms for semantic queries
- **Storage**: ~50MB for cached pages, ~200MB for embeddings

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

## 📝 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Fast Crawl Guide](FAST_CRAWL_GUIDE.md)
- [Project Status](PROJECT_STATUS.md)
- [Contributing](CONTRIBUTING.md)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [sentence-transformers](https://www.sbert.net/)
- Vector search via [ChromaDB](https://www.trychroma.com/)
- Documentation from [Databricks](https://docs.databricks.com/)

## 📬 Support

- Open an [issue](https://github.com/YOUR-USERNAME/databricks-docs-mcp/issues)
- Check [existing discussions](https://github.com/YOUR-USERNAME/databricks-docs-mcp/discussions)
