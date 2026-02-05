# Docker Deployment Guide - Legal Intelligence MCP Hub

## Overview

This guide covers deploying the Legal Intelligence MCP Hub using Docker. The Docker setup mirrors the working production configuration and uses a simplified single-stage build.

## Date: February 5, 2026

---

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- `.env` file with your API keys

---

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
cd /path/to/gpt-researcher/mcp-server

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop the container
docker-compose down
```

### 2. Build and Run with Docker CLI

```bash
cd /path/to/gpt-researcher/mcp-server

# Build the image
docker build -t legal-mcp-hub .

# Run the container
docker run -d \
  --name legal-mcp-hub \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  legal-mcp-hub

# View logs
docker logs -f legal-mcp-hub

# Stop the container
docker stop legal-mcp-hub
docker rm legal-mcp-hub
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `mcp-server` directory:

```bash
# API Keys
TAVILY_API_KEY=your_tavily_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# LLM Configuration
FAST_LLM=gemini/gemini-2.0-flash-exp
SMART_LLM=gemini/gemini-2.0-flash-thinking-exp-01-21
STRATEGIC_LLM=gemini/gemini-2.0-flash-thinking-exp-01-21
EMBEDDING=openai:text-embedding-3-small
RETRIEVER=tavily

# AWS Configuration (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1
```

---

## MCP Client Configuration

### For Augment CLI

Update `~/.augment/settings.json`:

```json
{
  "model": "haiku4.5",
  "mcpServers": {
    "legal-hub": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### For Gemini CLI

Update `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## Management Commands

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker CLI
docker logs -f legal-mcp-hub
```

### Restart Container

```bash
# Docker Compose
docker-compose restart

# Docker CLI
docker restart legal-mcp-hub
```

### Update Environment Variables

```bash
# 1. Edit .env file
nano .env

# 2. Restart container
docker-compose restart
# OR
docker restart legal-mcp-hub
```

### Update Code

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart
docker-compose up -d --build

# OR with Docker CLI
docker build -t legal-mcp-hub .
docker stop legal-mcp-hub
docker rm legal-mcp-hub
docker run -d --name legal-mcp-hub -p 8000:8000 --env-file .env --restart unless-stopped legal-mcp-hub
```

### Check Container Status

```bash
# Docker Compose
docker-compose ps

# Docker CLI
docker ps | grep legal-mcp-hub
```

### Access Container Shell

```bash
# Docker Compose
docker-compose exec legal-mcp-hub /bin/bash

# Docker CLI
docker exec -it legal-mcp-hub /bin/bash
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs

# Check if port 8000 is already in use
netstat -tulpn | grep 8000
# OR
lsof -i :8000
```

### Health Check Failing

```bash
# Test the endpoint manually
curl -I http://localhost:8000/mcp/

# Check container logs
docker-compose logs -f
```

### Environment Variables Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check environment variables inside container
docker-compose exec legal-mcp-hub env | grep -E "GOOGLE|GEMINI|TAVILY"
```

---

## Production Deployment

### Deploy to Remote Server

```bash
# 1. Copy files to remote server
scp -r mcp-server user@remote-server:/path/to/

# 2. SSH to remote server
ssh user@remote-server

# 3. Navigate to directory
cd /path/to/mcp-server

# 4. Build and run
docker-compose up -d

# 5. Verify
docker-compose ps
docker-compose logs -f
```

---

## Comparison: Docker vs systemd

| Feature | Docker | systemd |
|---------|--------|---------|
| **Isolation** | ✅ Full container isolation | ❌ Runs on host |
| **Portability** | ✅ Works anywhere | ❌ Linux-specific |
| **Setup Complexity** | ⚠️ Moderate | ✅ Simple |
| **Debugging** | ⚠️ Requires container access | ✅ Direct access |
| **Resource Overhead** | ⚠️ ~100MB extra | ✅ Minimal |
| **Update Speed** | ⚠️ Rebuild required | ✅ Just restart |

**Recommendation:** Use systemd for single-tenant deployments (current use case). Use Docker for multi-tenant or cloud deployments.

---

## Available Tools

The Docker container exposes all 11 MCP tools:

1. `deep_research` - Comprehensive web research
2. `quick_search` - Fast web search
3. `write_report` - Generate formatted reports
4. `save_report_to_s3` - Upload reports to S3
5. `search_cases` - Court Listener case search
6. `get_opinion` - Retrieve legal opinion text
7. `lookup_citation` - Look up legal citations
8. `create_file_store` - Create Gemini file store
9. `upload_to_file_store` - Upload to Gemini
10. `file_search_query` - Query Gemini file store
11. `health_check` - Server health check

---

## Next Steps

1. Test the Docker deployment locally
2. Verify all tools work correctly
3. If successful, consider Docker for future multi-tenant deployments
4. For current single-tenant use, systemd deployment is recommended (see PRODUCTION-DEPLOYMENT.md)

