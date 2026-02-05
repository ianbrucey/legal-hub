# Legal Intelligence MCP Hub - Deployment Quick Start

## 🚀 Choose Your Deployment Method

### Option 1: systemd (Recommended for Single-Tenant)

**Best for:** Production servers, single-tenant deployments, simple management

**Setup Time:** ~5 minutes

```bash
# 1. Copy setup script to server
scp -i ~/.ssh/your-key setup-server.sh root@your-server:/root/

# 2. SSH to server and run setup
ssh -i ~/.ssh/your-key root@your-server
chmod +x /root/setup-server.sh
/root/setup-server.sh

# 3. Edit .env with your API keys
nano /root/legal-hub/mcp-server/.env

# 4. Start the service
systemctl start legal-mcp
systemctl status legal-mcp
```

**Management:**
```bash
# View logs
journalctl -u legal-mcp -f

# Restart
systemctl restart legal-mcp

# Update code
cd /root/legal-hub/mcp-server
./deploy.sh
```

**Documentation:** See `PRODUCTION-DEPLOYMENT.md`

---

### Option 2: Docker (For Testing/Multi-Tenant)

**Best for:** Local testing, multi-tenant deployments, cloud platforms

**Setup Time:** ~10 minutes

```bash
# 1. Navigate to mcp-server directory
cd /path/to/gpt-researcher/mcp-server

# 2. Create .env file with your API keys
cp .env.example .env
nano .env

# 3. Build and run
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

**Management:**
```bash
# Restart
docker-compose restart

# Update code
git pull origin main
docker-compose up -d --build

# Stop
docker-compose down
```

**Documentation:** See `DOCKER-DEPLOYMENT.md`

---

## 📋 Required API Keys

Edit your `.env` file with these keys:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional
OPENAI_API_KEY=your_openai_api_key_here
COURTLISTENER_API_KEY=your_courtlistener_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
```

---

## 🔧 MCP Client Configuration

### Augment CLI

Edit `~/.augment/settings.json`:

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

### Gemini CLI

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Note:** For remote servers, replace `localhost` with the server IP address.

---

## ✅ Verify Installation

```bash
# Test the endpoint
curl -I http://localhost:8000/mcp/

# Expected response:
# HTTP/1.1 307 Temporary Redirect

# Test with MCP client
auggie -p "use your health_check tool"
```

---

## 🛠️ Troubleshooting

### Service won't start (systemd)
```bash
journalctl -u legal-mcp -n 50 --no-pager
```

### Container won't start (Docker)
```bash
docker-compose logs
```

### Port 8000 already in use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Tools not working
```bash
# Check API keys are loaded
# systemd:
systemctl status legal-mcp | grep -i "api"

# Docker:
docker-compose exec legal-mcp-hub env | grep -i "api"
```

---

## 📚 Available Tools

1. **deep_research** - Comprehensive web research
2. **quick_search** - Fast web search  
3. **write_report** - Generate formatted reports
4. **save_report_to_s3** - Upload reports to S3
5. **search_cases** - Court Listener case search
6. **get_opinion** - Retrieve legal opinion text
7. **lookup_citation** - Look up legal citations
8. **create_file_store** - Create Gemini file store
9. **upload_to_file_store** - Upload to Gemini
10. **file_search_query** - Query Gemini file store
11. **health_check** - Server health check

---

## 🎯 Current Production Setup

**Server:** 178.156.239.246 (war-rooom)  
**Method:** systemd  
**Status:** ✅ Running  
**Endpoint:** http://178.156.239.246:8000/mcp/  

---

## 📖 Full Documentation

- **systemd Deployment:** `PRODUCTION-DEPLOYMENT.md`
- **Docker Deployment:** `DOCKER-DEPLOYMENT.md`
- **HTTP Migration:** `HTTP-MIGRATION-STEPS.md`
- **Server Setup Script:** `setup-server.sh`
- **Update Script:** `deploy.sh`

