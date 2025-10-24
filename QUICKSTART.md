# Databricks Docs MCP - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- 2GB+ RAM
- 500MB+ disk space
- Internet connection

## Step 1: Navigate to Project

```bash
cd /Users/cliff.yang/CursorProj/databricks_docs_mcp
```

## Step 2: Start Server

```bash
./start_server.sh
```

The script will:
1. Install **uv** (fast Python package manager) if needed
2. Create a virtual environment (`.venv`)
3. Install dependencies with uv (10-100x faster than pip!)
4. Offer to crawl documentation (first time only)
5. Start the MCP server on port 8100

**Note**: First-time crawl takes 10-30 minutes. You can skip and crawl later.

## Step 3: Configure AI IDE

### For Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "url": "http://localhost:8100/mcp"
    }
  }
}
```

### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks-docs": {
      "url": "http://localhost:8100/mcp"
    }
  }
}
```

## Step 4: Restart Your AI IDE

Close and reopen Cursor or Claude Desktop to load the MCP configuration.

## Step 5: Test It!

Try these queries in your AI IDE:

```
"Search Databricks docs for Delta Lake"
"How do I create a Unity Catalog metastore?"
"Show me MLflow tracking examples"
"Find getting started guides"
```

## Verify It's Working

You should see responses with documentation content, URLs, and relevant information.

---

## Manual Crawl (If Skipped)

If you skipped the initial crawl, run:

```bash
python -m databricks_docs_mcp crawl
```

This will take 10-30 minutes depending on your connection.

---

## Check Status

```bash
python -m databricks_docs_mcp stats
```

Expected output:
```
📚 Document Cache:
  Total Pages: 1000+
  Categories: 15+
  ...

🔍 Vector Database:
  Total Chunks: 3000+
  ...
```

---

## Common Issues

### Server won't start

```bash
# Check if port 8100 is in use
lsof -i :8100

# Use different port
python -m databricks_docs_mcp server --port 8200
```

### No search results

```bash
# Re-index documentation
python -m databricks_docs_mcp index --clear
```

### AI IDE not connecting

1. Verify server is running: `curl http://localhost:8100/health`
2. Check MCP config file path and syntax
3. Restart AI IDE
4. Check logs: `tail -f docs_mcp_server.log`

---

## What's Next?

- Read [README.md](README.md) for full documentation
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for query examples
- Customize settings in `config.example.py`

---

## Daily Usage

The server automatically refreshes documentation at 2 AM daily. Just keep it running!

Start server:
```bash
./start_server.sh
```

Stop server:
```bash
pkill -f "python.*server.py"
```

---

## Getting Help

- Check logs: `tail -f docs_mcp_server.log`
- View stats: `python -m databricks_docs_mcp stats`
- See examples: `USAGE_EXAMPLES.md`

---

**You're all set! Happy coding with Databricks documentation at your fingertips! 🚀**

