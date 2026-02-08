# Legal Intelligence MCP Hub - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Legal Intelligence MCP Hub on a fresh Ubuntu/Debian server. The deployment uses systemd for process management and runs the server in HTTP mode for production use.

---

## Prerequisites

- Fresh Ubuntu 20.04+ or Debian 11+ server
- Root or sudo access
- Server accessible via SSH
- Domain name or IP address (e.g., `178.156.239.246`)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Production Server                   │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         systemd (legal-mcp.service)        │    │
│  │                                            │    │
│  │  ┌──────────────────────────────────┐     │    │
│  │  │   Python 3.11+ Virtual Env       │     │    │
│  │  │                                  │     │    │
│  │  │   Legal Intelligence MCP Hub     │     │    │
│  │  │   - GPT Researcher Tools         │     │    │
│  │  │   - Court Listener API           │     │    │
│  │  │   - Gemini File Search           │     │    │
│  │  │                                  │     │    │
│  │  │   Listening: 0.0.0.0:8000        │     │    │
│  │  │   Transport: streamable-http     │     │    │
│  │  └──────────────────────────────────┘     │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  Clients connect via: http://SERVER_IP:8000/mcp/   │
└─────────────────────────────────────────────────────┘
```

---

## Deployment Steps

### Step 1: Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Verify Python version (must be 3.11+)
python3.11 --version
```

### Step 2: Clone the Repository

```bash
# Clone the repository
cd /opt
sudo git clone https://github.com/ianbrucey/legal-hub.git
sudo chown -R $USER:$USER legal-hub

# Navigate to MCP server directory
cd legal-hub/mcp-server
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

**Required Configuration:**

```bash
# OpenAI API key (REQUIRED)
OPENAI_API_KEY=your-openai-key-here

# Tavily API key (REQUIRED)
TAVILY_API_KEY=your-tavily-key-here

# Court Listener API key (REQUIRED for legal tools)
COURTLISTENER_API_KEY=your-courtlistener-key-here

# Gemini API key (REQUIRED for file search tools)
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_API_KEY=your-google-api-key-here

# LLM Configuration
EMBEDDING=openai:text-embedding-3-small
FAST_LLM=openai:gpt-4o-mini
SMART_LLM=openai:gpt-4o-mini
STRATEGIC_LLM=openai:gpt-4o-mini
MAX_ITERATIONS=2

# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO
```

### Step 5: Test the Server

```bash
# Test server startup
.venv/bin/python server.py --transport streamable-http --host 0.0.0.0 --port 8000

# In another terminal, test the health endpoint
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}

# Stop the test server (Ctrl+C)
```

---

## Production Deployment with systemd

### Step 6: Create systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/legal-mcp.service
```

**Service Configuration:**

```ini
[Unit]
Description=Legal Intelligence MCP Hub
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/legal-hub/mcp-server
Environment="PATH=/opt/legal-hub/mcp-server/.venv/bin"
ExecStart=/opt/legal-hub/mcp-server/.venv/bin/python server.py --transport streamable-http --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username!**

### Step 7: Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable legal-mcp.service

# Start the service
sudo systemctl start legal-mcp.service

# Check service status
sudo systemctl status legal-mcp.service

# View logs
sudo journalctl -u legal-mcp.service -f
```

---

## Verification

### Check Server Health

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test MCP endpoint
curl http://localhost:8000/mcp/

# Check if port is listening
sudo netstat -tlnp | grep 8000
```

### Expected Output

```json
{
  "status": "healthy",
  "server_name": "Legal Intelligence Hub",
  "version": "1.0.0",
  "tools": {
    "gpt_researcher": ["deep_research", "quick_search", "write_report", "save_report_to_s3"],
    "court_listener": ["search_cases", "get_opinion", "lookup_citation"],
    "gemini": ["create_file_store", "upload_to_file_store", "file_search_query"]
  }
}
```

---

## Firewall Configuration

```bash
# Allow port 8000 (if using UFW)
sudo ufw allow 8000/tcp
sudo ufw reload

# Verify firewall rules
sudo ufw status
```

---

## Client Configuration

### For Augment CLI

Edit `~/.augment/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://SERVER_IP:8000/mcp"
    }
  }
}
```

### For Gemini CLI

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://SERVER_IP:8000/mcp"
    }
  }
}
```

Replace `SERVER_IP` with your server's IP address or domain name.

---

## Maintenance

### View Logs

```bash
# Real-time logs
sudo journalctl -u legal-mcp.service -f

# Last 100 lines
sudo journalctl -u legal-mcp.service -n 100

# Logs since today
sudo journalctl -u legal-mcp.service --since today
```

### Restart Service

```bash
sudo systemctl restart legal-mcp.service
```

### Stop Service

```bash
sudo systemctl stop legal-mcp.service
```

### Update Deployment

```bash
# Navigate to repository
cd /opt/legal-hub

# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart legal-mcp.service
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status legal-mcp.service

# Check logs for errors
sudo journalctl -u legal-mcp.service -n 50

# Common issues:
# 1. Missing API keys in .env file
# 2. Wrong Python path in service file
# 3. Port 8000 already in use
# 4. Incorrect file permissions
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 PID
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/legal-hub

# Fix permissions
chmod +x /opt/legal-hub/mcp-server/server.py
```

---

## Security Recommendations

1. **Use a reverse proxy** (nginx) with SSL/TLS for production
2. **Implement rate limiting** to prevent abuse
3. **Use environment-specific API keys** (don't share production keys)
4. **Enable firewall** and only allow necessary ports
5. **Regular updates** - keep system and dependencies updated
6. **Monitor logs** for suspicious activity
7. **Backup .env file** securely (contains sensitive keys)

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `sudo systemctl start legal-mcp` | Start the service |
| `sudo systemctl stop legal-mcp` | Stop the service |
| `sudo systemctl restart legal-mcp` | Restart the service |
| `sudo systemctl status legal-mcp` | Check service status |
| `sudo journalctl -u legal-mcp -f` | View live logs |
| `curl http://localhost:8000/health` | Test server health |

---

## Support

For issues or questions:
- GitHub: https://github.com/ianbrucey/legal-hub
- Check logs: `sudo journalctl -u legal-mcp.service -n 100`

