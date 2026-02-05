# Production Deployment - Legal Intelligence MCP Hub

## Overview

Successfully deployed the Legal Intelligence MCP Hub to production server at `178.156.239.246` using systemd for process management and HTTP/SSE transport for production-ready architecture.

## Date: February 5, 2026

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Production Server: 178.156.239.246 (war-rooom)         │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ systemd Service: legal-mcp.service                │ │
│  │  - Auto-start on boot                             │ │
│  │  - Auto-restart on crash                          │ │
│  │  - Logging to journald                            │ │
│  └───────────────────────────────────────────────────┘ │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Python Process (PID 113400)                       │ │
│  │  - server.py --transport streamable-http          │ │
│  │  - Listening on 0.0.0.0:8000                      │ │
│  │  - Uvicorn ASGI server                            │ │
│  └───────────────────────────────────────────────────┘ │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │ HTTP/SSE Endpoint: http://0.0.0.0:8000/mcp/      │ │
│  │  - 11 MCP tools available                         │ │
│  │  - StreamableHTTP session manager                 │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment Steps Completed

### 1. Created systemd Service File

**File:** `/etc/systemd/system/legal-mcp.service`

**Key Features:**
- Auto-restart on failure (RestartSec=10)
- Loads environment variables from `.env`
- Runs as root user
- Logs to systemd journal
- Starts on boot (enabled)

### 2. Deployed to Production

**Commands executed:**
```bash
# On remote server
cd /root/legal-hub
git pull origin main
cp mcp-server/legal-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable legal-mcp
systemctl start legal-mcp
```

**Result:** ✅ Service running successfully (PID 113400)

### 3. Verified Server Status

**Service Status:**
```
● legal-mcp.service - Legal Intelligence MCP Hub
     Loaded: loaded (/etc/systemd/system/legal-mcp.service; enabled)
     Active: active (running) since Thu 2026-02-05 16:11:47 UTC
   Main PID: 113400 (python)
      Tasks: 4
     Memory: 183.2M
```

**Server Logs:**
```
2026-02-05 16:11:50 - legal-mcp-hub - INFO - Starting Legal Intelligence MCP Hub
2026-02-05 16:11:50 - legal-mcp-hub - INFO - Transport: streamable-http
2026-02-05 16:11:50 - legal-mcp-hub - INFO - Listening on http://0.0.0.0:8000/mcp/
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**HTTP Test:**
```bash
curl -I http://localhost:8000/mcp/
# HTTP/1.1 307 Temporary Redirect ✅
```

---

## Production Management

### Common Operations

**View Live Logs:**
```bash
ssh -i ~/.ssh/justicequest root@178.156.239.246
journalctl -u legal-mcp -f
```

**Check Service Status:**
```bash
systemctl status legal-mcp
```

**Restart Service:**
```bash
systemctl restart legal-mcp
```

**Stop Service:**
```bash
systemctl stop legal-mcp
```

**Start Service:**
```bash
systemctl start legal-mcp
```

**View Recent Logs:**
```bash
journalctl -u legal-mcp -n 100 --no-pager
```

### Deployment Workflow

**To deploy code updates:**
```bash
# Option 1: Use deployment script
ssh -i ~/.ssh/justicequest root@178.156.239.246
cd /root/legal-hub/mcp-server
./deploy.sh

# Option 2: Manual deployment
ssh -i ~/.ssh/justicequest root@178.156.239.246
cd /root/legal-hub
git pull origin main
systemctl restart legal-mcp
systemctl status legal-mcp
```

### Environment Variable Updates

**To update API keys or configuration:**
```bash
ssh -i ~/.ssh/justicequest root@178.156.239.246
nano /root/legal-hub/mcp-server/.env
# Make your changes
systemctl restart legal-mcp
```

**No more zombie process cleanup needed!** Just restart the service.

---

## Server Details

**Server:** 178.156.239.246 (war-rooom)  
**OS:** Ubuntu 24.04.3 LTS  
**Hostname:** war-rooom  
**Service Name:** legal-mcp  
**Port:** 8000  
**Endpoint:** http://178.156.239.246:8000/mcp/  
**Process ID:** 113400  
**Memory Usage:** 183.2M  

---

## Available Tools

The production server exposes 11 MCP tools:

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

## Benefits Achieved

✅ **Production-Ready Architecture** - HTTP/SSE transport, not stdio  
✅ **No Zombie Processes** - Single managed process  
✅ **Auto-Restart on Crash** - systemd handles failures  
✅ **Start on Boot** - Service enabled for automatic startup  
✅ **Centralized Logging** - All logs in systemd journal  
✅ **Easy Updates** - Git pull + restart  
✅ **Environment Variable Management** - Edit .env + restart  
✅ **Resource Monitoring** - systemd tracks memory/CPU  

---

## Troubleshooting

**Service won't start:**
```bash
journalctl -u legal-mcp -n 50 --no-pager
```

**Check if port 8000 is in use:**
```bash
netstat -tulpn | grep 8000
```

**Test server locally:**
```bash
curl -I http://localhost:8000/mcp/
```

**Restart from scratch:**
```bash
systemctl stop legal-mcp
systemctl start legal-mcp
systemctl status legal-mcp
```

