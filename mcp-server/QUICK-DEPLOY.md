# Quick Deployment Guide

## One-Command Deployment

Deploy the Legal Intelligence MCP Hub to any server with a single command:

```bash
./deploy.sh SERVER_IP [SSH_USER]
```

### Examples

```bash
# Deploy to server with root user (default)
./deploy.sh 178.156.239.246

# Deploy to server with specific user
./deploy.sh 178.156.239.246 ubuntu

# Deploy to server with custom SSH key
ssh-add ~/.ssh/my-key.pem
./deploy.sh 178.156.239.246 ubuntu
```

---

## Prerequisites

Before running the deployment script, ensure:

1. **SSH Access**: You can SSH into the server without password (SSH key configured)
2. **Sudo Privileges**: The SSH user has sudo access
3. **Server Requirements**: Ubuntu 20.04+ or Debian 11+
4. **Port 8000**: Available on the server

### Test SSH Connection

```bash
ssh ubuntu@178.156.239.246 "echo 'Connection successful'"
```

---

## What the Script Does

The `deploy.sh` script automatically:

1. ✅ Tests SSH connection
2. ✅ Installs system dependencies (Python 3.11, git, etc.)
3. ✅ Clones the repository to `/opt/legal-hub`
4. ✅ Creates Python virtual environment
5. ✅ Installs all Python dependencies
6. ✅ Creates systemd service file
7. ✅ Starts the MCP server
8. ✅ Verifies deployment

**Total time:** ~3-5 minutes

---

## After Deployment

### Step 1: Configure API Keys

SSH into the server and edit the `.env` file:

```bash
ssh ubuntu@178.156.239.246
nano /opt/legal-hub/mcp-server/.env
```

Add your API keys:

```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
COURTLISTENER_API_KEY=...
GOOGLE_API_KEY=...
GEMINI_API_KEY=...
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 2: Restart Service

```bash
sudo systemctl restart legal-mcp.service
```

### Step 3: Verify Server

```bash
# Check service status
sudo systemctl status legal-mcp.service

# Test health endpoint
curl http://localhost:8000/health

# View logs
sudo journalctl -u legal-mcp.service -f
```

---

## Client Configuration

### For Augment CLI

Edit `~/.augment/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://178.156.239.246:8000/mcp"
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
      "url": "http://178.156.239.246:8000/mcp"
    }
  }
}
```

### Test Connection

```bash
# Test with Augment
auggie -p "use your health_check tool"

# Test with Gemini
gemini -p "use your health_check tool"
```

---

## Updating Deployment

To update an existing deployment:

```bash
# Run the deploy script again
./deploy.sh 178.156.239.246 ubuntu

# The script will:
# - Pull latest code from GitHub
# - Reinstall dependencies
# - Restart the service
```

---

## Troubleshooting

### Deployment Failed

```bash
# Check what went wrong
ssh ubuntu@178.156.239.246 "sudo journalctl -u legal-mcp.service -n 50"
```

### Server Not Responding

```bash
# Check if service is running
ssh ubuntu@178.156.239.246 "sudo systemctl status legal-mcp.service"

# Check if port is listening
ssh ubuntu@178.156.239.246 "sudo netstat -tlnp | grep 8000"

# Restart service
ssh ubuntu@178.156.239.246 "sudo systemctl restart legal-mcp.service"
```

### API Keys Not Working

```bash
# Verify .env file
ssh ubuntu@178.156.239.246 "cat /opt/legal-hub/mcp-server/.env | grep API_KEY"

# Make sure to restart after updating .env
ssh ubuntu@178.156.239.246 "sudo systemctl restart legal-mcp.service"
```

---

## Manual Deployment

If you prefer manual deployment, see [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) for detailed step-by-step instructions.

---

## Common Commands

```bash
# Deploy to server
./deploy.sh 178.156.239.246 ubuntu

# SSH into server
ssh ubuntu@178.156.239.246

# View logs
ssh ubuntu@178.156.239.246 "sudo journalctl -u legal-mcp.service -f"

# Restart service
ssh ubuntu@178.156.239.246 "sudo systemctl restart legal-mcp.service"

# Stop service
ssh ubuntu@178.156.239.246 "sudo systemctl stop legal-mcp.service"

# Check service status
ssh ubuntu@178.156.239.246 "sudo systemctl status legal-mcp.service"

# Test health endpoint
curl http://178.156.239.246:8000/health
```

---

## Security Notes

1. **Firewall**: The script does NOT configure firewall rules. You may need to allow port 8000:
   ```bash
   ssh ubuntu@178.156.239.246 "sudo ufw allow 8000/tcp"
   ```

2. **SSL/TLS**: For production, use a reverse proxy (nginx) with SSL certificates

3. **API Keys**: Never commit `.env` file to git. Keep API keys secure.

4. **Access Control**: Consider implementing authentication/authorization for production use

---

## Support

- **Full Documentation**: [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
- **GitHub Issues**: https://github.com/ianbrucey/legal-hub/issues
- **Server Logs**: `sudo journalctl -u legal-mcp.service -n 100`

