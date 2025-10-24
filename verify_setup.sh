#!/bin/bash

# Quick verification script

echo "Verifying Databricks Docs MCP Setup"
echo "===================================="
echo ""

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✅ uv is installed: $(uv --version)"
else
    echo "❌ uv is not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment exists (.venv)"
else
    echo "⚠️  Virtual environment not found"
    echo "   Run: uv venv"
fi

# Check if package is installed
if [ -f ".venv/bin/python" ]; then
    source .venv/bin/activate
    if python -c "import databricks_docs_mcp" 2>/dev/null; then
        echo "✅ Package is installed (databricks_docs_mcp)"
    else
        echo "⚠️  Package not installed"
        echo "   Run: uv pip install -e ."
    fi
else
    echo "⚠️  Cannot check package installation (no .venv/bin/python)"
fi

echo ""
echo "===================================="
echo "Setup verification complete!"
echo ""
echo "To start the server:"
echo "  ./start_server.sh"
echo ""

