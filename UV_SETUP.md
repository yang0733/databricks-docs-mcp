# Using UV for Package Management

This project uses **uv** - a blazingly fast Python package installer and resolver written in Rust.

## Why UV?

- ⚡ **10-100x faster** than pip
- 🔒 **Reliable** dependency resolution with lock files
- 🎯 **Simple** commands
- 🚀 **Modern** Python package management
- 📦 **All-in-one** tool for Python projects

## Installation

UV will be automatically installed when you run `./start_server.sh`.

Or install manually:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

## Quick Start

The easiest way to get started:

```bash
./start_server.sh
```

This script will:
1. Install uv if needed
2. Install all dependencies (creates `.venv` automatically)
3. Offer to crawl documentation
4. Start the server

## Common Commands

### Install Dependencies

```bash
# Install all dependencies (creates .venv if needed)
uv sync

# Install with development dependencies
uv sync --group dev

# Install with test dependencies
uv sync --group test
```

### Run Commands

```bash
# Run any Python command in the virtual environment
uv run python -m databricks_docs_mcp.server

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check .

# Run formatting
uv run black .
```

### Manage Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --group dev package-name

# Remove a dependency
uv remove package-name

# Update all dependencies
uv lock --upgrade
uv sync
```

### Lock File

```bash
# Regenerate lock file
uv lock

# Install from lock file (reproducible)
uv sync
```

## Project Configuration

Dependencies are defined in `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastmcp>=2.14.3",
    "chromadb>=1.4.0",
    # ...
]

[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "black>=25.12.0",
    "ruff>=0.14.11",
]
```

## Advantages Over pip

| Feature | uv | pip |
|---------|-----|-----|
| Speed | ⚡ 10-100x faster | Baseline |
| Dependency Resolution | ✅ Reliable | ⚠️ Can fail |
| Lock Files | ✅ Built-in | ❌ Needs pip-tools |
| Memory Usage | 💚 Low | 📊 Higher |
| Parallel Downloads | ✅ Yes | ❌ Sequential |
| Rust-based | ✅ Yes | ❌ Python |

## Troubleshooting

### Command not found: uv

```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
uv sync
```

### Dependency conflicts

```bash
# Clear cache
uv cache clean

# Regenerate lock file
uv lock
uv sync
```

### Wrong Python version

```bash
# Check .python-version file
cat .python-version

# Install correct Python version with uv
uv python install 3.13
```

## Learn More

- **UV Documentation**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **UV Guide**: https://astral.sh/uv

---

**Note**: This project uses the `src` layout with `uv.lock` for reproducible builds.

