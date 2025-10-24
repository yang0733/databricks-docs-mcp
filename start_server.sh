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

# Create virtual environment and install dependencies using uv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies using uv (much faster than pip)
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Add parent directory to PYTHONPATH so imports work
# This allows `from databricks_docs_mcp.xxx import yyy` to work
export PYTHONPATH="/Users/cliff.yang/CursorProj:$PYTHONPATH"

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
        python3 -m databricks_docs_mcp crawl
        echo ""
        echo "Crawl complete!"
    else
        echo ""
        echo "Skipping crawl. You can run it later with:"
        echo "  python3 -m databricks_docs_mcp crawl"
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

python server.py "$@"

