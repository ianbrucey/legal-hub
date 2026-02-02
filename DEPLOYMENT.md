# Legal Intelligence Hub - Deployment Guide

## Overview

The Legal Intelligence Hub is an MCP (Model Context Protocol) server that provides AI agents with access to:
- **GPT Researcher** - Deep web research and report generation
- **Court Listener API** - Legal case search and opinion retrieval
- **Gemini File Search** - Document RAG (Retrieval-Augmented Generation)

This guide covers deployment via Docker for production use.

---

## Prerequisites

- Docker installed and running
- API keys for:
  - Google AI (Gemini) - `GOOGLE_API_KEY`
  - Tavily Search - `TAVILY_API_KEY`
  - Court Listener - `COURTLISTENER_API_KEY`
  - OpenAI (optional) - `OPENAI_API_KEY`

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ianbrucey/legal-hub.git
cd legal-hub
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required API Keys
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# Optional - OpenAI (if using OpenAI models)
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration (using Gemini by default)
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro

# Court Listener Configuration
COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v3
```

### 3. Build the Docker Image

```bash
docker build -t legal-hub:latest .
```

**Build time**: ~2-3 minutes on first build, <10 seconds on subsequent builds (cached layers)

### 4. Run the Container

```bash
docker run -d \
  --name legal-hub \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  legal-hub:latest
```

### 5. Verify Deployment

```bash
# Check container status
docker ps | grep legal-hub

# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"mcp-server"}
```

---

## Docker Compose Deployment

For easier management, use Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'

services:
  legal-hub:
    build: .
    container_name: legal-hub
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**Deploy with Docker Compose**:

```bash
docker-compose up -d
```

---

## MCP Client Configuration

### Augment AI Configuration

Edit `~/.augment/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "streamable-http"
    }
  }
}
```

### Google Gemini Configuration

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "streamable-http"
    }
  }
}
```

**Note**: After updating settings, restart your AI client to apply changes.

---

## Available Tools

The Legal Intelligence Hub provides 11 tools across 3 categories:

### GPT Researcher Tools (5)
1. `deep_research` - Comprehensive web research with citations
2. `quick_search` - Fast web search
3. `write_report` - Generate formatted research reports
4. `get_research_sources` - Retrieve research sources
5. `get_research_context` - Get research context

### Court Listener Tools (3)
6. `search_cases` - Search legal cases by keyword, party, or citation
7. `get_opinion` - Retrieve full text of legal opinions
8. `lookup_citation` - Look up cases by citation (e.g., "384 U.S. 436")

### Gemini File Search Tools (3)
9. `create_file_store` - Create document RAG store
10. `upload_to_file_store` - Upload files for RAG
11. `file_search_query` - Query documents with semantic search

---

## Production Deployment Considerations

### Port Configuration

By default, the server runs on port 8000. To use a different port:

```bash
docker run -d \
  --name legal-hub \
  -p 8080:8000 \
  --env-file .env \
  legal-hub:latest
```

Update your MCP client configuration accordingly:
```json
{
  "url": "http://127.0.0.1:8080/sse"
}
```

### Resource Requirements

**Minimum**:
- CPU: 1 core
- RAM: 512 MB
- Disk: 1 GB

**Recommended**:
- CPU: 2 cores
- RAM: 1 GB
- Disk: 2 GB

### Logging

View container logs:

```bash
# Follow logs in real-time
docker logs -f legal-hub

# View last 100 lines
docker logs --tail 100 legal-hub

# View logs since specific time
docker logs --since 1h legal-hub
```

Logs are also written to `researcher_mcp_server.log` inside the container.

### Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **Network**: Use firewall rules to restrict access to port 8000
3. **HTTPS**: For production, use a reverse proxy (nginx/traefik) with SSL
4. **Updates**: Regularly rebuild images to get security patches

### Backup and Recovery

**Backup Configuration**:
```bash
# Backup .env file
cp .env .env.backup

# Export container configuration
docker inspect legal-hub > legal-hub-config.json
```

**Recovery**:
```bash
# Stop and remove container
docker stop legal-hub
docker rm legal-hub

# Rebuild and restart
docker build -t legal-hub:latest .
docker run -d --name legal-hub -p 8000:8000 --env-file .env legal-hub:latest
```

---

## Troubleshooting

### Container Won't Start

**Check logs**:
```bash
docker logs legal-hub
```

**Common issues**:
- Missing API keys in `.env`
- Port 8000 already in use
- Insufficient memory

**Solution**:
```bash
# Check if port is in use
lsof -i :8000

# Check container status
docker ps -a | grep legal-hub

# Remove and recreate
docker rm -f legal-hub
docker run -d --name legal-hub -p 8000:8000 --env-file .env legal-hub:latest
```

### Health Check Failing

```bash
# Check if server is responding
curl -v http://localhost:8000/health

# Check container logs
docker logs legal-hub

# Restart container
docker restart legal-hub
```

### Tools Not Working

**Verify API keys**:
```bash
# Check environment variables inside container
docker exec legal-hub env | grep API_KEY
```

**Test specific tool**:
```bash
# Test Court Listener
curl -X POST http://localhost:8000/sse \
  -H "Content-Type: application/json" \
  -d '{"tool": "search_cases", "params": {"query": "Miranda v Arizona"}}'
```

### Performance Issues

**Check resource usage**:
```bash
docker stats legal-hub
```

**Increase resources** (if using Docker Desktop):
- Go to Docker Desktop → Settings → Resources
- Increase CPU and Memory allocation

---

## Monitoring

### Health Checks

The server includes a built-in health check endpoint:

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "mcp-server"
}
```

### Uptime Monitoring

Use tools like:
- **Uptime Kuma** - Self-hosted monitoring
- **Healthchecks.io** - Simple HTTP monitoring
- **Prometheus + Grafana** - Advanced metrics

Example Uptime Kuma configuration:
- Monitor Type: HTTP(s)
- URL: `http://localhost:8000/health`
- Interval: 60 seconds
- Expected Status Code: 200

---

## Updating

### Update to Latest Version

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker build -t legal-hub:latest .

# Stop old container
docker stop legal-hub
docker rm legal-hub

# Start new container
docker run -d --name legal-hub -p 8000:8000 --env-file .env legal-hub:latest
```

### Zero-Downtime Updates

For production, use blue-green deployment:

```bash
# Build new version
docker build -t legal-hub:v2 .

# Start new container on different port
docker run -d --name legal-hub-v2 -p 8001:8000 --env-file .env legal-hub:v2

# Test new version
curl http://localhost:8001/health

# Update reverse proxy to point to new port
# Then stop old container
docker stop legal-hub
docker rm legal-hub

# Rename new container
docker rename legal-hub-v2 legal-hub
```

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/ianbrucey/legal-hub/issues
- **Documentation**: https://github.com/ianbrucey/legal-hub

---

## License

See [LICENSE](LICENSE) file for details.


