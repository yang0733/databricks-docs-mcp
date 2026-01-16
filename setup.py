"""Setup script for databricks-docs-mcp."""

from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="databricks-docs-mcp",
    version="1.0.0",
    packages=["databricks_docs_mcp", "databricks_docs_mcp.crawler", "databricks_docs_mcp.embeddings", "databricks_docs_mcp.storage", "databricks_docs_mcp.tools", "databricks_docs_mcp.resources"],
    package_dir={"databricks_docs_mcp": "."},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "databricks-docs-mcp=databricks_docs_mcp.__main__:main",
        ],
    },
    python_requires=">=3.11",
)

