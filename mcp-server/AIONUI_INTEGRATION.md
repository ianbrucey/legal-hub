# AionUI Integration Guide - Legal Intelligence MCP Hub

## 🎯 Quick Start

### Step 1: Create Unified docker-compose.yml

In your **project root** (where both `aionui` and `gpt-researcher` directories exist):

```yaml
version: '3.8'

services:
  # AionUI Application
  aionui:
    build: ./aionui
    container_name: aionui
    ports:
      - "25808:25808"
    environment:
      # Point to MCP server via Docker network
      - MCP_SERVER_URL=http://legal-mcp-hub:8000/mcp/
    depends_on:
      legal-mcp-hub:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  # Legal Intelligence MCP Hub
  legal-mcp-hub:
    build:
      context: ./gpt-researcher
      dockerfile: mcp-server/Dockerfile
    container_name: legal-mcp-hub
    expose:
      - "8000"
    # Optional: expose to host for debugging
    # ports:
    #   - "8000:8000"
    env_file:
      - ./gpt-researcher/mcp-server/.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge
```

### Step 2: Update AionUI MCP Client Config

**Before (stdio - subprocess)**:
```json
{
  "mcpServers": {
    "legal-hub": {
      "command": "/path/to/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "cwd": "/path/to/mcp-server",
      "env": { ... }
    }
  }
}
```

**After (HTTP - container)**:
```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://legal-mcp-hub:8000/mcp/",
      "transport": "http"
    }
  }
}
```

### Step 3: Deploy

```bash
# From project root
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test connectivity from AionUI
docker exec aionui curl http://legal-mcp-hub:8000/health
```

---

## 🔧 Configuration Details

### Environment Variables (in .env file)

**Required**:
```env
GOOGLE_API_KEY=AIzaSyDgKYeN-rOL9FeLLVDLF0QhU4OT6uv4jPI
TAVILY_API_KEY=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
```

**Optional**:
```env
COURTLISTENER_API_KEY=e3e0c9e0e2e1e4e5e6e7e8e9eaebecedeeeff0f1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_key
```

### Network Communication

- **Service Name**: `legal-mcp-hub` (DNS name in Docker network)
- **Port**: `8000` (internal to Docker network)
- **Endpoint**: `/mcp/` (MCP protocol)
- **Health Check**: `/health` (JSON response)

---

## 🧪 Testing

### 1. Test Health Endpoint
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "legal-mcp-hub"}
```

### 2. Test from AionUI Container
```bash
docker exec aionui curl http://legal-mcp-hub:8000/health
# Expected: {"status": "healthy", "service": "legal-mcp-hub"}
```

### 3. Test MCP Tools (from AionUI)
```javascript
// In AionUI code
const client = new MCPClient('http://legal-mcp-hub:8000/mcp/');
const tools = await client.listTools();
console.log('Available tools:', tools);
```

---

## 📦 Available MCP Tools

### GPT Researcher
- `deep_research(query, report_type, max_sources)` - Comprehensive research
- `quick_search(query, max_results)` - Fast web search
- `write_report(query, research_data, report_type)` - Generate reports
- `save_report_to_s3(report, bucket, key)` - Upload to S3

### Court Listener
- `search_cases(query, court, date_from, date_to)` - Search legal cases
- `get_opinion(opinion_id)` - Get full case opinion
- `lookup_citation(citation)` - Look up by citation

### Gemini
- `create_file_store(name, display_name)` - Create RAG store
- `upload_to_file_store(store_name, file_path)` - Upload documents
- `file_search_query(store_name, query)` - Query documents

---

## 🔍 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs legal-mcp-hub

# Common issues:
# 1. Missing API keys → Check .env file
# 2. Port conflict → Change port in docker-compose.yml
# 3. Build failed → Run: docker-compose build --no-cache
```

### AionUI can't connect
```bash
# Test network connectivity
docker exec aionui ping legal-mcp-hub

# Test HTTP connectivity
docker exec aionui curl http://legal-mcp-hub:8000/health

# Check if both containers are on same network
docker network inspect app-network
```

### Health check failing
```bash
# Check health status
docker inspect legal-mcp-hub | grep -A 10 Health

# Test manually
docker exec legal-mcp-hub curl http://localhost:8000/health

# View detailed logs
docker logs legal-mcp-hub --tail 100
```

---

## 🚀 Production Recommendations

### 1. Security
- Use Docker Secrets for API keys
- Enable TLS with reverse proxy (nginx/traefik)
- Restrict network access with firewall rules

### 2. Monitoring
- Add logging aggregation (ELK, CloudWatch)
- Set up alerts for health check failures
- Monitor resource usage

### 3. Scaling
```yaml
services:
  legal-mcp-hub:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 4. Backup
- Backup .env file securely
- Document API key rotation process
- Keep docker-compose.yml in version control

---

## 📞 Support

**Documentation**:
- Full deployment guide: `DOCKER_DEPLOYMENT.md`
- Technical details: `HANDOFF_REPORT.md`
- Test script: `test-docker.sh`

**Quick Commands**:
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart MCP server
docker-compose restart legal-mcp-hub

# View logs
docker-compose logs -f legal-mcp-hub

# Check health
curl http://localhost:8000/health
```

