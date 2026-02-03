# Docker Integration Guide - Multi-Tenant AionUI Setup

## Overview

This guide covers integrating containerized AionUI instances with the host-based MCP server.

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                      Production Server                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Host OS (Ubuntu)                                      │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  MCP Server (systemd service)                    │  │ │
│  │  │  http://127.0.0.1:8000/mcp/                      │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                          ▲                              │ │
│  │                          │ HTTP                         │ │
│  │                          │                              │ │
│  │  ┌───────────────────────┴──────────────────────────┐  │ │
│  │  │  Docker Bridge Network (172.17.0.1)              │  │ │
│  │  │                                                   │  │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │ │
│  │  │  │ AionUI-1 │  │ AionUI-2 │  │ AionUI-8 │       │  │ │
│  │  │  │ :3001    │  │ :3002    │  │ :3008    │       │  │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘       │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Container Configuration

### AionUI Settings File

Each AionUI container needs a `settings.json` file configured to connect to the host MCP server:

**File:** `/app/.augment/settings.json` (inside container)

```json
{
  "model": "haiku4.5",
  "mcpServers": {
    "legal-hub": {
      "url": "http://host.docker.internal:8000/mcp/",
      "transport": "streamable-http"
    }
  }
}
```

**Key Points:**
- `host.docker.internal` - Special DNS name that resolves to the host machine
- Works on Docker Desktop (Mac/Windows) automatically
- On Linux, requires `--add-host=host.docker.internal:host-gateway` flag

---

## Docker Compose Setup

### Single Tenant Example

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  aionui-tenant1:
    image: aionui:latest
    container_name: aionui-tenant1
    ports:
      - "3001:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Required for Linux
    volumes:
      - ./tenant1-settings.json:/app/.augment/settings.json:ro
      - tenant1-data:/app/data
    environment:
      - NODE_ENV=production
      - TENANT_ID=tenant1
    restart: unless-stopped
    networks:
      - aionui-network

volumes:
  tenant1-data:

networks:
  aionui-network:
    driver: bridge
```

### Multi-Tenant Example (8 Tenants)

**File:** `docker-compose-multi-tenant.yml`

```yaml
version: '3.8'

services:
  aionui-tenant1:
    image: aionui:latest
    container_name: aionui-tenant1
    ports:
      - "3001:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./config/tenant1-settings.json:/app/.augment/settings.json:ro
      - tenant1-data:/app/data
    environment:
      - TENANT_ID=tenant1
    restart: unless-stopped

  aionui-tenant2:
    image: aionui:latest
    container_name: aionui-tenant2
    ports:
      - "3002:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./config/tenant2-settings.json:/app/.augment/settings.json:ro
      - tenant2-data:/app/data
    environment:
      - TENANT_ID=tenant2
    restart: unless-stopped

  aionui-tenant3:
    image: aionui:latest
    container_name: aionui-tenant3
    ports:
      - "3003:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./config/tenant3-settings.json:/app/.augment/settings.json:ro
      - tenant3-data:/app/data
    environment:
      - TENANT_ID=tenant3
    restart: unless-stopped

  # ... Continue for tenant4 through tenant8 ...

volumes:
  tenant1-data:
  tenant2-data:
  tenant3-data:
  # ... Continue for tenant4 through tenant8 ...

networks:
  default:
    driver: bridge
```

---

## Configuration Files Structure

```
/opt/aionui-deployment/
├── docker-compose.yml
├── config/
│   ├── tenant1-settings.json
│   ├── tenant2-settings.json
│   ├── tenant3-settings.json
│   └── ... (tenant4-8)
└── .env
```

### Create Configuration Directory

```bash
mkdir -p /opt/aionui-deployment/config

# Create settings file for each tenant
for i in {1..8}; do
  cat > /opt/aionui-deployment/config/tenant${i}-settings.json << 'EOF'
{
  "model": "haiku4.5",
  "mcpServers": {
    "legal-hub": {
      "url": "http://host.docker.internal:8000/mcp/",
      "transport": "streamable-http"
    }
  }
}
EOF
done
```

---

## Deployment Steps

### 1. Ensure MCP Server is Running

```bash
# Check MCP server status
sudo systemctl status legal-mcp-hub

# If not running, start it
sudo systemctl start legal-mcp-hub

# Verify it's listening
curl http://127.0.0.1:8000/mcp/
```

### 2. Deploy Containers

```bash
cd /opt/aionui-deployment

# Start all containers
docker-compose -f docker-compose-multi-tenant.yml up -d

# Check status
docker-compose -f docker-compose-multi-tenant.yml ps

# View logs
docker-compose -f docker-compose-multi-tenant.yml logs -f
```

### 3. Test Container-to-Host Communication

```bash
# Enter a container
docker exec -it aionui-tenant1 /bin/bash

# Test connectivity to host MCP server
curl http://host.docker.internal:8000/mcp/

# Should return MCP protocol response
```

---

## Troubleshooting

### Issue: Container can't reach host.docker.internal

**Linux Systems:**
```bash
# Add to docker-compose.yml for each service:
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Alternative (use bridge IP directly):**
```bash
# Find Docker bridge IP
ip addr show docker0 | grep inet

# Use 172.17.0.1 instead of host.docker.internal
# Update settings.json:
{
  "url": "http://172.17.0.1:8000/mcp/"
}
```

### Issue: Connection refused

**Check MCP server is listening:**
```bash
sudo netstat -tlnp | grep 8000
# Should show: 127.0.0.1:8000 or 0.0.0.0:8000
```

**If only 127.0.0.1:** MCP server needs to listen on 0.0.0.0 for Docker access
```bash
# Edit /opt/legal-mcp-hub/.env
MCP_HOST=0.0.0.0

# Restart service
sudo systemctl restart legal-mcp-hub
```

### Issue: Firewall blocking connections

```bash
# Allow Docker bridge network
sudo ufw allow from 172.17.0.0/16 to any port 8000

# Check firewall status
sudo ufw status
```

---

## Monitoring

### View MCP Server Logs
```bash
# Real-time logs
sudo journalctl -u legal-mcp-hub -f

# Search for errors
sudo journalctl -u legal-mcp-hub | grep ERROR
```

### View Container Logs
```bash
# All containers
docker-compose logs -f

# Specific tenant
docker-compose logs -f aionui-tenant1
```

### Health Checks
```bash
# Check MCP server
curl http://127.0.0.1:8000/mcp/

# Check all containers
docker-compose ps
```

---

## Scaling Considerations

- **MCP Server Resources:** Monitor CPU/RAM usage as tenant count increases
- **Connection Pooling:** MCP server handles multiple concurrent connections
- **Rate Limiting:** Consider implementing rate limits per tenant if needed
- **Logging:** Rotate logs to prevent disk space issues

---

## Next Steps

- Set up reverse proxy (nginx) for HTTPS and domain routing
- Implement monitoring (Prometheus/Grafana)
- Set up automated backups for tenant data
- Configure log aggregation (ELK stack or similar)

