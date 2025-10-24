"""Example configuration file.

Copy this to config.py and customize as needed.
"""

# Server Configuration
HOST = "0.0.0.0"
PORT = 8100

# Cache Configuration
CACHE_DIR = "storage/data"
VECTOR_DB_DIR = "storage/chromadb"

# Embedding Model
# Options: "all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-MiniLM-L6-cos-v1"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Crawler Configuration
BASE_URL = "https://docs.databricks.com/aws/en/"
RATE_LIMIT = 0.5  # Seconds between requests
MAX_PAGES = None  # None for unlimited, or set a number for testing

# Scheduler Configuration
REFRESH_HOUR = 2  # 24-hour format
REFRESH_MINUTE = 0
ENABLE_SCHEDULER = True

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "docs_mcp_server.log"

