#!/bin/bash

# Prepare Code for Sharing
# This script creates a CLEAN COPY of your code for sharing
# Your original working code remains UNCHANGED!

set -e

echo "🎯 Preparing Clean Code for Sharing..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Must run from databricks_docs_mcp directory${NC}"
    exit 1
fi

# Create clean directory for sharing
SHARE_DIR="../databricks_docs_mcp_SHARE"
echo -e "${BLUE}📦 Creating clean copy for sharing...${NC}"

# Remove old share directory if exists
if [ -d "$SHARE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Removing old share directory...${NC}"
    rm -rf "$SHARE_DIR"
fi

# Copy everything to share directory
echo -e "${BLUE}📋 Copying files...${NC}"
cp -r . "$SHARE_DIR"
cd "$SHARE_DIR"

echo -e "${GREEN}✅ Copy created at: $SHARE_DIR${NC}"
echo ""

# Remove sensitive/temporary files from the COPY
echo -e "${YELLOW}🗑️  Removing sensitive and temporary files from copy...${NC}"
rm -f .env .env.local *.log 2>/dev/null || true
rm -rf __pycache__/ */__pycache__/ */*/__pycache__/ 2>/dev/null || true
rm -rf storage/chromadb/ 2>/dev/null || true
rm -rf storage/data/pages/*.json 2>/dev/null || true
rm -f storage/data/index.json 2>/dev/null || true
rm -rf backup_* .venv/ venv/ env/ 2>/dev/null || true
rm -rf .pytest_cache/ htmlcov/ .coverage 2>/dev/null || true
rm -rf *.egg-info/ dist/ build/ 2>/dev/null || true
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Create necessary empty directories
echo -e "${BLUE}📁 Creating necessary directory structure...${NC}"
mkdir -p storage/data/pages
mkdir -p storage/chromadb
echo "{\"pages\": {}, \"total_pages\": 0, \"last_crawl\": null}" > storage/data/index.json
echo -e "${GREEN}✅ Done${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${GREEN}✅ Clean copy ready for sharing!${NC}"
echo ""
echo -e "${BLUE}📍 Location: $SHARE_DIR${NC}"
echo ""
echo -e "${GREEN}✅ Your original code is UNTOUCHED!${NC}"
echo -e "${GREEN}   Continue using: $(pwd | sed 's/_SHARE$//')${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "Option A: Share via GitHub"
echo "  cd $SHARE_DIR"
echo "  git init"
echo "  git add ."
echo "  git commit -m 'Databricks Documentation MCP Server'"
echo "  git remote add origin https://github.com/YOUR-USERNAME/databricks-docs-mcp.git"
echo "  git push -u origin main"
echo ""
echo "Option B: Share via Zip"
echo "  cd $(dirname "$SHARE_DIR")"
echo "  zip -r databricks-docs-mcp.zip $(basename "$SHARE_DIR") \\"
echo "    -x '*.pyc' '*__pycache__*' '*.log' '*/.venv/*' '*/env/*'"
echo ""
echo "After sharing, you can delete the copy:"
echo "  rm -rf $SHARE_DIR"
echo ""

