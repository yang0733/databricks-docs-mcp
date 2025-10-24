# Contributing to Databricks Documentation MCP

Thank you for your interest in contributing! This project aims to make Databricks documentation easily accessible through the Model Context Protocol (MCP).

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing [issues](https://github.com/YOUR-USERNAME/databricks-docs-mcp/issues)
2. Create a new issue with:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 style guide
   - Add docstrings for new functions/classes
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Test the server locally
   ./start_server.sh
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/databricks-docs-mcp.git
   cd databricks-docs-mcp
   ```

2. **Set up Python environment**
   ```bash
   # Using uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   
   # OR using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run initial crawl**
   ```bash
   python -m databricks_docs_mcp crawl --fast --max-pages 100
   ```

4. **Start the server**
   ```bash
   python server.py --no-scheduler
   ```

## Project Structure

```
databricks_docs_mcp/
├── crawler/          # Web scraping and parsing
├── embeddings/       # Vector embeddings and search
├── resources/        # MCP resources
├── storage/          # Data models and caching
├── tools/            # MCP tools
└── tests/            # Unit tests
```

## Code Style

- Use type hints where possible
- Add docstrings to all public functions/classes
- Keep functions focused and single-purpose
- Add comments for complex logic

## Testing

- Write unit tests for new features
- Ensure existing tests pass
- Test with different documentation sources if possible

## Questions?

Open an issue with the `question` label or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

