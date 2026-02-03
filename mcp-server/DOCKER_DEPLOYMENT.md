# Legal Intelligence MCP Hub - Docker Deployment Guide

## 🎯 Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
cd gpt-researcher/mcp-server
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

The server will be available at: `http://localhost:8000/mcp/`

### 2. Build Manually

```bash
cd gpt-researcher
docker build -f mcp-server/Dockerfile -t legal-mcp-hub .
```

### 3. Run Manually

```bash
docker run -d \
  --name legal-mcp-hub \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  -e COURTLISTENER_API_KEY=your_key \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_key \
  legal-mcp-hub
```

---

## 🔧 Required Environment Variables

### Core Services
| Variable | Required | Description | Get Key From |
|----------|----------|-------------|--------------|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API for AI research | [Google AI Studio](https://aistudio.google.com/apikey) |
| `TAVILY_API_KEY` | ✅ Yes | Web search retrieval | [Tavily](https://tavily.com/) |
| `COURTLISTENER_API_KEY` | ⚠️ Optional | Legal case search | [CourtListener](https://www.courtlistener.com/help/api/rest/) |

### AWS S3 (Optional - for report uploads)
| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | ⚠️ Optional | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | ⚠️ Optional | AWS credentials |
| `AWS_DEFAULT_REGION` | No | Default: `us-east-1` |
| `S3_DEFAULT_BUCKET` | No | Default: `legal-research-reports` |

### Server Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MCP_HOST` | No | `0.0.0.0` | Bind address |
| `MCP_PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### GPT Researcher (Auto-configured)
| Variable | Default | Description |
|----------|---------|-------------|
| `FAST_LLM` | `google_genai:gemini-2.5-pro` | Fast model |
| `SMART_LLM` | `google_genai:gemini-2.5-pro` | Smart model |
| `STRATEGIC_LLM` | `google_genai:gemini-2.5-pro` | Strategic model |
| `RETRIEVER` | `tavily` | Search provider |

---

## 🏥 Health Check

The container exposes a health endpoint:

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "legal-mcp-hub"}
```

Docker will automatically monitor this endpoint and restart if unhealthy.

---

## 🐳 Integration with AionUI

### docker-compose.yml (Multi-Container Setup)

```yaml
version: '3.8'

services:
  # Your AionUI application
  aionui:
    build: ./aionui
    ports:
      - "25808:25808"
    environment:
      - MCP_SERVER_URL=http://legal-mcp-hub:8000/mcp/
    depends_on:
      legal-mcp-hub:
        condition: service_healthy
    networks:
      - app-network

  # Legal Intelligence MCP Hub
  legal-mcp-hub:
    build:
      context: ./gpt-researcher
      dockerfile: mcp-server/Dockerfile
    container_name: legal-mcp-hub
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - COURTLISTENER_API_KEY=${COURTLISTENER_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
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

### MCP Client Configuration (AionUI)

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

---

## 🧪 Testing the Container

### 1. Verify Container is Running
```bash
docker ps | grep legal-mcp-hub
docker logs legal-mcp-hub
```

### 2. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### 3. Test MCP Endpoint (requires MCP client)
```bash
# Using Python MCP client
python -c "
import asyncio
from mcp import Client

async def test():
    async with Client('http://localhost:8000/mcp/') as client:
        tools = await client.list_tools()
        print(f'Available tools: {len(tools)}')

asyncio.run(test())
"
```

---

## 📦 Available Tools

The MCP server exposes these tools:

### GPT Researcher
- `deep_research` - Comprehensive research with citations
- `quick_search` - Fast web search
- `write_report` - Generate formatted reports
- `save_report_to_s3` - Upload reports to S3

### Court Listener
- `search_cases` - Search legal cases
- `get_opinion` - Retrieve full case opinions
- `lookup_citation` - Look up cases by citation

### Gemini
- `create_file_store` - Create document RAG store
- `upload_to_file_store` - Upload documents
- `file_search_query` - Query documents with RAG

---

## 🔍 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs legal-mcp-hub

# Common issues:
# 1. Missing API keys → Check .env file
# 2. Port conflict → Change MCP_PORT
# 3. Build failed → Rebuild with --no-cache
```

### Health check failing
```bash
# Test manually
docker exec legal-mcp-hub curl http://localhost:8000/health

# If fails, check server logs
docker logs legal-mcp-hub --tail 50
```

### Can't connect from AionUI
```bash
# Verify network
docker network inspect app-network

# Test connectivity
docker exec aionui curl http://legal-mcp-hub:8000/health
```

---

## 🚀 Production Deployment

### Security Recommendations
1. **Use secrets management** (Docker Secrets, AWS Secrets Manager)
2. **Enable TLS** (reverse proxy with nginx/traefik)
3. **Restrict network access** (firewall rules)
4. **Monitor logs** (ELK stack, CloudWatch)

### Resource Limits
```yaml
services:
  legal-mcp-hub:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 📝 Notes

- **Build Context**: The Dockerfile MUST be built from the `gpt-researcher` parent directory
- **Dependencies**: The server imports from the parent `gpt_researcher` library
- **Transport**: Defaults to `streamable-http` for container-to-container communication
- **Ports**: Exposes port 8000 by default (configurable via `MCP_PORT`)

