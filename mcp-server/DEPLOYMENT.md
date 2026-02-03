# Legal Intelligence MCP Hub - Production Deployment Guide

## Overview

This guide covers deploying the Legal Intelligence MCP Hub on a production server to serve multiple containerized AionUI instances (the "hotel strategy").

**Architecture:**
- **1 MCP Server** running directly on the host (not containerized)
- **8+ AionUI containers** connecting to the host MCP server via HTTP
- **Communication:** Containers use `http://host.docker.internal:8000/mcp/` to reach the host

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ or similar Linux distribution
- **Python:** 3.9 or higher (3.14 tested and working)
- **RAM:** 2GB minimum for MCP server
- **Disk:** 1GB for dependencies and logs

### Required Software
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

---

## Installation Steps

### 1. Clone Repository and Setup Directory

```bash
# Create application directory
sudo mkdir -p /opt/legal-mcp-hub
sudo chown $USER:$USER /opt/legal-mcp-hub

# Clone or copy the mcp-server directory
cd /opt/legal-mcp-hub
# (Copy your gpt-researcher/mcp-server files here)
```

### 2. Create Python Virtual Environment

```bash
cd /opt/legal-mcp-hub

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
python -c "import fastmcp; print('FastMCP installed successfully')"
```

**Note:** If you encounter LangChain dependency conflicts, the local `.venv` has working versions:
- `langchain==1.1.2`
- `langchain-classic==1.0.0`
- `langchain-community==0.4.1`
- `langchain-core==1.1.1`

### 4. Configure Environment Variables

```bash
# Create .env file
cat > /opt/legal-mcp-hub/.env << 'EOF'
# API Keys
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# LLM Configuration
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro

# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO
EOF

# Secure the .env file
chmod 600 /opt/legal-mcp-hub/.env
```

**Security Note:** For production, use `MCP_HOST=127.0.0.1` if only local containers need access, or `0.0.0.0` if remote containers need access (with firewall rules).

### 5. Test the Server

```bash
# Activate virtual environment
source /opt/legal-mcp-hub/.venv/bin/activate

# Start server in HTTP mode
python server.py --transport streamable-http --port 8000 --host 127.0.0.1

# You should see:
# INFO - Starting Legal Intelligence MCP Hub
# INFO - Transport: streamable-http
# INFO - Listening on http://127.0.0.1:8000/mcp/
# INFO - Uvicorn running on http://127.0.0.1:8000
```

Press `Ctrl+C` to stop the test server.

---

## Production Deployment with systemd

### 1. Create systemd Service File

```bash
sudo nano /etc/systemd/system/legal-mcp-hub.service
```

Paste the following configuration:

```ini
[Unit]
Description=Legal Intelligence MCP Hub
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/opt/legal-mcp-hub
Environment="PATH=/opt/legal-mcp-hub/.venv/bin"
EnvironmentFile=/opt/legal-mcp-hub/.env
ExecStart=/opt/legal-mcp-hub/.venv/bin/python server.py --transport streamable-http --port 8000 --host 127.0.0.1
Restart=always
RestartSec=10
StandardOutput=append:/var/log/legal-mcp-hub/output.log
StandardError=append:/var/log/legal-mcp-hub/error.log

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME`** with your actual username (e.g., `ubuntu`, `ianbruce`, etc.)

### 2. Create Log Directory

```bash
sudo mkdir -p /var/log/legal-mcp-hub
sudo chown $USER:$USER /var/log/legal-mcp-hub
```

### 3. Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable legal-mcp-hub

# Start the service
sudo systemctl start legal-mcp-hub

# Check status
sudo systemctl status legal-mcp-hub
```

### 4. Service Management Commands

```bash
# Start service
sudo systemctl start legal-mcp-hub

# Stop service
sudo systemctl stop legal-mcp-hub

# Restart service
sudo systemctl restart legal-mcp-hub

# View logs (live)
sudo journalctl -u legal-mcp-hub -f

# View logs (last 100 lines)
sudo journalctl -u legal-mcp-hub -n 100

# View log files directly
tail -f /var/log/legal-mcp-hub/output.log
tail -f /var/log/legal-mcp-hub/error.log
```

---

## Firewall Configuration

If using `MCP_HOST=0.0.0.0` (accessible from network):

```bash
# Allow port 8000 only from localhost (recommended for Docker)
sudo ufw allow from 127.0.0.1 to any port 8000

# Or allow from Docker bridge network
sudo ufw allow from 172.17.0.0/16 to any port 8000
```

For local-only access (recommended):
```bash
# No firewall rules needed if using 127.0.0.1
# Docker containers can still access via host.docker.internal
```

---

## Next Steps

See `DOCKER-INTEGRATION.md` for:
- Configuring AionUI containers to connect to the MCP server
- Docker Compose setup for multi-tenant deployment
- Container-to-host networking configuration

