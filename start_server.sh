#!/bin/bash

# Databricks Documentation MCP Server - Startup Script

set -e

echo "=========================================="
echo "Databricks Documentation MCP Server"
echo "=========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies using uv (creates .venv automatically)
echo "Installing dependencies with uv..."
uv sync

# Check if cache exists
if [ ! -f "storage/data/index.json" ]; then
    echo ""
    echo "=========================================="
    echo "⚠️  No cached documentation found"
    echo "=========================================="
    echo ""
    echo "Would you like to crawl the documentation now? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo "Starting initial crawl (this may take 10-30 minutes)..."
        uv run python -m databricks_docs_mcp crawl
        echo ""
        echo "Crawl complete!"
    else
        echo ""
        echo "Skipping crawl. You can run it later with:"
        echo "  uv run python -m databricks_docs_mcp crawl"
        echo ""
        echo "Note: The server will start but won't have any documentation to serve."
    fi
fi

# Start server
echo ""
echo "=========================================="
echo "Starting MCP server on port 8100..."
echo "=========================================="
echo ""

uv run python -m databricks_docs_mcp.server "$@"

