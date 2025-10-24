#!/bin/bash

# Quick GitHub Publish Script
# Run this from the databricks_docs_mcp_SHARE directory

set -e

echo "🚀 Publishing Databricks Documentation MCP Server to GitHub"
echo ""

# Check if in SHARE directory
if [[ ! $(pwd) == *"_SHARE" ]]; then
    echo "❌ Error: Must run from databricks_docs_mcp_SHARE directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "feat: Initial release of Databricks Documentation MCP Server

- Semantic search over 3,181 Databricks AWS documentation pages
- Fast async crawler (5-7 minute full crawl)
- 10 MCP tools for search, recommendation, and exploration
- ChromaDB-powered vector search
- Complete offline documentation cache
- Docker and systemd deployment support"
    echo "✅ Git initialized and initial commit created"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "Next steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   gh repo create databricks-docs-mcp --public --source=. --remote=origin"
echo ""
echo "2. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Add topics:"
echo "   gh repo edit --add-topic mcp,databricks,documentation,ai,semantic-search"
echo ""
echo "Or run all at once:"
echo "   gh repo create databricks-docs-mcp --public --source=. --remote=origin && \\"
echo "   git branch -M main && \\"
echo "   git push -u origin main && \\"
echo "   gh repo edit --add-topic mcp,databricks,documentation,ai,semantic-search"
echo ""
