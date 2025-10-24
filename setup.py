"""Setup script for databricks-docs-mcp."""

from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="databricks-docs-mcp",
    version="1.0.0",
    packages=find_packages(where="."),
    package_dir={"databricks_docs_mcp": "."},
    py_modules=[
        "__init__",
        "__main__",
        "server",
        "config.example",
    ],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "databricks-docs-mcp=__main__:main",
        ],
    },
    python_requires=">=3.11",
)

