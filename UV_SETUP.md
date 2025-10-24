# Using UV for Package Management

This project now uses **uv** - a blazingly fast Python package installer and resolver written in Rust.

## Why UV?

- ⚡ **10-100x faster** than pip
- 🔒 **Reliable** dependency resolution
- 🎯 **Simple** commands
- 🚀 **Modern** Python package management

## Installation

UV will be automatically installed when you run `./start_server.sh`.

Or install manually:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

## Common Commands

### Setup Project

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install project in editable mode
uv pip install -e .

# Or install from requirements.txt
uv pip install -r requirements.txt
```

### Install Packages

```bash
# Install a package
uv pip install fastmcp

# Install with version
uv pip install "fastmcp>=0.2.0"

# Install development dependencies
uv pip install -e ".[dev]"
```

### Manage Dependencies

```bash
# Show installed packages
uv pip list

# Show outdated packages
uv pip list --outdated

# Upgrade all packages
uv pip install --upgrade -r requirements.txt
```

### Lock Dependencies

```bash
# Generate lock file (done automatically)
uv lock

# Install from lock file
uv sync
```

## Quick Start

The easiest way to get started:

```bash
./start_server.sh
```

This script will:
1. Install uv if needed
2. Create `.venv` virtual environment
3. Install all dependencies
4. Start the server

## Manual Setup

If you prefer manual control:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install
cd databricks_docs_mcp
uv venv
source .venv/bin/activate
uv pip install -e .

# Run server
python server.py
```

## Advantages Over pip

| Feature | uv | pip |
|---------|-----|-----|
| Speed | ⚡ 10-100x faster | Baseline |
| Dependency Resolution | ✅ Reliable | ⚠️ Can fail |
| Memory Usage | 💚 Low | 📊 Higher |
| Parallel Downloads | ✅ Yes | ❌ Sequential |
| Rust-based | ✅ Yes | ❌ Python |

## Troubleshooting

### Command not found: uv

```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or install globally
pip install uv
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Package conflicts

```bash
# Clear cache
uv cache clean

# Reinstall
uv pip install --force-reinstall -e .
```

## Learn More

- **UV Docs**: https://github.com/astral-sh/uv
- **UV Guide**: https://astral.sh/uv
- **Rye (Alternative)**: https://rye-up.com/

---

**Note**: The old `venv/` directory has been removed. We now use `.venv/` (standard convention).

