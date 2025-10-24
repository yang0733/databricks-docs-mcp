# Deployment Guide

This guide covers different ways to deploy the Databricks Documentation MCP Server.

## Local Deployment

### Quick Start

```bash
# Clone and setup
git clone https://github.com/YOUR-USERNAME/databricks-docs-mcp.git
cd databricks-docs-mcp
./start_server.sh
```

The server will be available at `http://localhost:8100/mcp`

### Manual Deployment

```bash
# 1. Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Initial crawl
export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
python -m databricks_docs_mcp crawl --fast

# 3. Start server
python server.py --no-scheduler
```

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application
COPY . .

# Create storage directories
RUN mkdir -p storage/data/pages storage/chromadb

# Expose port
EXPOSE 8100

# Run server
CMD ["python", "server.py", "--no-scheduler"]
```

Build and run:

```bash
docker build -t databricks-docs-mcp .
docker run -p 8100:8100 -v $(pwd)/storage:/app/storage databricks-docs-mcp
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8100:8100"
    volumes:
      - ./storage:/app/storage
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

## Systemd Service (Linux)

Create `/etc/systemd/system/databricks-docs-mcp.service`:

```ini
[Unit]
Description=Databricks Documentation MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/databricks_docs_mcp
Environment="PYTHONPATH=/path/to/parent/directory"
ExecStart=/path/to/databricks_docs_mcp/.venv/bin/python server.py --no-scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable databricks-docs-mcp
sudo systemctl start databricks-docs-mcp
sudo systemctl status databricks-docs-mcp
```

## Cloud Deployment

### AWS EC2

1. Launch EC2 instance (t3.medium or larger recommended)
2. Install Python 3.11+
3. Clone repository
4. Run deployment script
5. Configure security group to allow port 8100 (if needed)

### Google Cloud Run

Create `cloudbuild.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/databricks-docs-mcp', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/databricks-docs-mcp']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'databricks-docs-mcp'
      - '--image'
      - 'gcr.io/$PROJECT_ID/databricks-docs-mcp'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
```

Deploy:

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Performance Tuning

### Memory Requirements

- Minimum: 2GB RAM
- Recommended: 4GB RAM for full documentation
- With embeddings: 4-8GB RAM

### Optimize for Large Deployments

```python
# In server.py or config
EMBEDDING_BATCH_SIZE = 32  # Reduce if OOM
MAX_CONCURRENT_REQUESTS = 20  # Increase for higher throughput
CACHE_SIZE_MB = 512  # Adjust based on available memory
```

## Monitoring

### Health Check

```bash
curl http://localhost:8100/health
```

### Logs

```bash
# View logs
tail -f /tmp/mcp_server.log

# Or with systemd
sudo journalctl -u databricks-docs-mcp -f
```

### Metrics

The server exposes basic metrics at `http://localhost:8100/metrics` (if enabled)

## Backup and Restore

### Backup

```bash
# Backup cached documentation
tar -czf databricks-docs-backup.tar.gz storage/data/

# Backup vector database
tar -czf chromadb-backup.tar.gz storage/chromadb/
```

### Restore

```bash
# Restore cached documentation
tar -xzf databricks-docs-backup.tar.gz

# Restore vector database
tar -xzf chromadb-backup.tar.gz
```

## Scheduled Crawls

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily crawl at 2 AM
0 2 * * * cd /path/to/databricks_docs_mcp && .venv/bin/python -m databricks_docs_mcp refresh >> /var/log/docs-refresh.log 2>&1
```

### Using Scheduler (Built-in)

Enable the scheduler when starting the server:

```bash
python server.py  # Scheduler enabled by default
```

The scheduler will refresh documentation daily at 2 AM.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8100
lsof -i :8100

# Kill the process
kill -9 <PID>
```

### Out of Memory

- Reduce `max_concurrent` in async crawler
- Use smaller embedding batch sizes
- Increase swap space
- Deploy on instance with more RAM

### Slow Queries

- Ensure ChromaDB is fully indexed
- Check system resources (CPU, RAM, disk I/O)
- Consider using a persistent ChromaDB instance
- Enable query caching

## Security

### Production Checklist

- [ ] Use environment variables for sensitive config
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication if exposed publicly
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Set up rate limiting
- [ ] Configure CORS appropriately

### Example Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /mcp {
        proxy_pass http://localhost:8100/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Support

For deployment issues:
1. Check logs: `tail -f /tmp/mcp_server.log`
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Open an [issue](https://github.com/YOUR-USERNAME/databricks-docs-mcp/issues)

