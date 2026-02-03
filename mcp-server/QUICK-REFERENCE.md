# Quick Reference Guide - Legal Intelligence MCP Hub

## Common Commands

### MCP Server Management

```bash
# Start server
sudo systemctl start legal-mcp-hub

# Stop server
sudo systemctl stop legal-mcp-hub

# Restart server
sudo systemctl restart legal-mcp-hub

# Check status
sudo systemctl status legal-mcp-hub

# View logs (live)
sudo journalctl -u legal-mcp-hub -f

# View last 100 log lines
sudo journalctl -u legal-mcp-hub -n 100

# View log files
tail -f /var/log/legal-mcp-hub/output.log
tail -f /var/log/legal-mcp-hub/error.log
```

### Docker Container Management

```bash
# Start all containers
docker-compose up -d

# Stop all containers
docker-compose down

# Restart all containers
docker-compose restart

# View container status
docker-compose ps

# View logs (all containers)
docker-compose logs -f

# View logs (specific container)
docker-compose logs -f aionui-tenant1

# Enter container shell
docker exec -it aionui-tenant1 /bin/bash

# Restart specific container
docker-compose restart aionui-tenant1
```

### Testing Connectivity

```bash
# Test MCP server from host
curl http://127.0.0.1:8000/mcp/

# Test from inside container
docker exec -it aionui-tenant1 curl http://host.docker.internal:8000/mcp/

# Check if port is listening
sudo netstat -tlnp | grep 8000

# Check Docker bridge IP
ip addr show docker0 | grep inet
```

---

## File Locations

### MCP Server
- **Installation:** `/opt/legal-mcp-hub/`
- **Virtual Environment:** `/opt/legal-mcp-hub/.venv/`
- **Environment Config:** `/opt/legal-mcp-hub/.env`
- **Server Code:** `/opt/legal-mcp-hub/server.py`
- **systemd Service:** `/etc/systemd/system/legal-mcp-hub.service`
- **Logs:** `/var/log/legal-mcp-hub/`

### Docker Deployment
- **Compose Files:** `/opt/aionui-deployment/`
- **Tenant Configs:** `/opt/aionui-deployment/config/`
- **Container Data:** Docker volumes (managed by Docker)

---

## Configuration Files

### MCP Server Environment (.env)
```bash
# Location: /opt/legal-mcp-hub/.env

GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
COURTLISTENER_API_KEY=your_key_here
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO
```

### Tenant Settings (settings.json)
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

---

## Troubleshooting Checklist

### MCP Server Not Starting
1. Check service status: `sudo systemctl status legal-mcp-hub`
2. Check logs: `sudo journalctl -u legal-mcp-hub -n 50`
3. Verify .env file exists: `ls -la /opt/legal-mcp-hub/.env`
4. Check Python environment: `source /opt/legal-mcp-hub/.venv/bin/activate && python --version`
5. Test manually: `cd /opt/legal-mcp-hub && source .venv/bin/activate && python server.py --transport streamable-http --port 8000`

### Container Can't Connect to MCP Server
1. Check MCP server is running: `sudo systemctl status legal-mcp-hub`
2. Verify port is listening: `sudo netstat -tlnp | grep 8000`
3. Test from host: `curl http://127.0.0.1:8000/mcp/`
4. Check Docker networking: `docker network inspect bridge`
5. Verify extra_hosts in docker-compose.yml: `host.docker.internal:host-gateway`
6. Test from container: `docker exec -it aionui-tenant1 curl http://host.docker.internal:8000/mcp/`

### Connection Refused Errors
1. Check MCP_HOST in .env: Should be `0.0.0.0` for Docker access
2. Check firewall: `sudo ufw status`
3. Allow Docker network: `sudo ufw allow from 172.17.0.0/16 to any port 8000`
4. Restart MCP server: `sudo systemctl restart legal-mcp-hub`

### High CPU/Memory Usage
1. Check MCP server resources: `top -p $(pgrep -f "python server.py")`
2. Check container resources: `docker stats`
3. Review logs for errors: `sudo journalctl -u legal-mcp-hub | grep ERROR`
4. Consider scaling: Add more server resources or implement rate limiting

---

## Maintenance Tasks

### Update MCP Server Code
```bash
# Stop service
sudo systemctl stop legal-mcp-hub

# Backup current code
cd /opt/legal-mcp-hub
tar -czf backup-$(date +%Y%m%d).tar.gz *.py *.txt

# Update code (git pull or copy new files)
# ...

# Restart service
sudo systemctl start legal-mcp-hub

# Check status
sudo systemctl status legal-mcp-hub
```

### Update Dependencies
```bash
# Stop service
sudo systemctl stop legal-mcp-hub

# Activate virtual environment
cd /opt/legal-mcp-hub
source .venv/bin/activate

# Update packages
pip install --upgrade -r requirements.txt

# Test
python server.py --transport streamable-http --port 8000
# Press Ctrl+C after confirming it starts

# Restart service
sudo systemctl start legal-mcp-hub
```

### Rotate Logs
```bash
# Manual log rotation
sudo journalctl --vacuum-time=7d  # Keep last 7 days
sudo journalctl --vacuum-size=500M  # Keep max 500MB

# Or truncate log files
sudo truncate -s 0 /var/log/legal-mcp-hub/output.log
sudo truncate -s 0 /var/log/legal-mcp-hub/error.log
```

### Backup Configuration
```bash
# Backup MCP server config
sudo tar -czf mcp-backup-$(date +%Y%m%d).tar.gz \
  /opt/legal-mcp-hub/.env \
  /etc/systemd/system/legal-mcp-hub.service

# Backup Docker configs
tar -czf docker-backup-$(date +%Y%m%d).tar.gz \
  /opt/aionui-deployment/docker-compose*.yml \
  /opt/aionui-deployment/config/
```

---

## Performance Monitoring

### Check MCP Server Performance
```bash
# CPU and memory usage
top -p $(pgrep -f "python server.py")

# Network connections
sudo netstat -anp | grep :8000

# Request count (from logs)
sudo journalctl -u legal-mcp-hub --since today | grep "POST /mcp" | wc -l
```

### Check Container Performance
```bash
# All containers
docker stats

# Specific container
docker stats aionui-tenant1

# Container resource limits
docker inspect aionui-tenant1 | grep -A 10 "Memory"
```

---

## Emergency Procedures

### Complete System Restart
```bash
# Stop all containers
docker-compose down

# Stop MCP server
sudo systemctl stop legal-mcp-hub

# Wait 10 seconds
sleep 10

# Start MCP server
sudo systemctl start legal-mcp-hub

# Wait for MCP server to be ready
sleep 5

# Start containers
docker-compose up -d

# Verify everything is running
sudo systemctl status legal-mcp-hub
docker-compose ps
```

### Rollback to Previous Version
```bash
# Stop service
sudo systemctl stop legal-mcp-hub

# Restore from backup
cd /opt/legal-mcp-hub
tar -xzf backup-YYYYMMDD.tar.gz

# Restart service
sudo systemctl start legal-mcp-hub
```

---

## Support Information

- **Documentation:** See `DEPLOYMENT.md` and `DOCKER-INTEGRATION.md`
- **Logs Location:** `/var/log/legal-mcp-hub/`
- **Service Name:** `legal-mcp-hub`
- **Default Port:** 8000
- **Transport:** streamable-http

