# Deployment Checklist - Legal Intelligence MCP Hub

Use this checklist to ensure a complete and correct deployment.

---

## Pre-Deployment

### Server Preparation
- [ ] Server provisioned (Ubuntu 20.04+ recommended)
- [ ] SSH access configured
- [ ] Sudo/root access available
- [ ] Server has adequate resources (2GB+ RAM, 1GB+ disk)
- [ ] Server hostname/IP documented

### Required Information
- [ ] Google API Key obtained
- [ ] Tavily API Key obtained
- [ ] Court Listener API Key obtained
- [ ] Domain name (if using) configured
- [ ] SSL certificates (if using HTTPS) ready

---

## Phase 1: System Setup

### Install System Dependencies
- [ ] System updated: `sudo apt update && sudo apt upgrade -y`
- [ ] Python 3.9+ installed: `python3 --version`
- [ ] pip installed: `pip3 --version`
- [ ] venv module available: `python3 -m venv --help`
- [ ] Build tools installed: `sudo apt install build-essential -y`

### Create Application Directory
- [ ] Directory created: `/opt/legal-mcp-hub/`
- [ ] Ownership set correctly: `sudo chown $USER:$USER /opt/legal-mcp-hub`
- [ ] Code files copied to server

---

## Phase 2: MCP Server Installation

### Python Environment
- [ ] Virtual environment created: `/opt/legal-mcp-hub/.venv/`
- [ ] Virtual environment activated
- [ ] pip upgraded: `pip install --upgrade pip`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] FastMCP verified: `python -c "import fastmcp; print('OK')"`

### Configuration
- [ ] `.env` file created: `/opt/legal-mcp-hub/.env`
- [ ] API keys added to `.env`
- [ ] LLM models configured in `.env`
- [ ] MCP_HOST set (127.0.0.1 or 0.0.0.0)
- [ ] MCP_PORT set (default: 8000)
- [ ] `.env` file secured: `chmod 600 .env`

### Manual Test
- [ ] Server starts manually: `python server.py --transport streamable-http --port 8000`
- [ ] Server logs show "Listening on http://..."
- [ ] Server responds to curl: `curl http://127.0.0.1:8000/mcp/`
- [ ] No errors in startup logs
- [ ] Manual test stopped (Ctrl+C)

---

## Phase 3: systemd Service Setup

### Service Configuration
- [ ] Service file created: `/etc/systemd/system/legal-mcp-hub.service`
- [ ] Username updated in service file
- [ ] WorkingDirectory correct: `/opt/legal-mcp-hub`
- [ ] ExecStart path correct: `/opt/legal-mcp-hub/.venv/bin/python`
- [ ] EnvironmentFile path correct: `/opt/legal-mcp-hub/.env`

### Log Directory
- [ ] Log directory created: `/var/log/legal-mcp-hub/`
- [ ] Ownership set: `sudo chown $USER:$USER /var/log/legal-mcp-hub`
- [ ] Permissions correct: `ls -ld /var/log/legal-mcp-hub`

### Service Activation
- [ ] systemd reloaded: `sudo systemctl daemon-reload`
- [ ] Service enabled: `sudo systemctl enable legal-mcp-hub`
- [ ] Service started: `sudo systemctl start legal-mcp-hub`
- [ ] Service status checked: `sudo systemctl status legal-mcp-hub`
- [ ] Service shows "active (running)"
- [ ] Logs accessible: `sudo journalctl -u legal-mcp-hub -n 20`

### Service Verification
- [ ] Server responds: `curl http://127.0.0.1:8000/mcp/`
- [ ] Logs show successful startup
- [ ] No error messages in logs
- [ ] Service survives reboot test (optional but recommended)

---

## Phase 4: Docker Integration (if applicable)

### Docker Setup
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] User added to docker group: `sudo usermod -aG docker $USER`
- [ ] Docker service running: `sudo systemctl status docker`

### Deployment Directory
- [ ] Directory created: `/opt/aionui-deployment/`
- [ ] Config directory created: `/opt/aionui-deployment/config/`
- [ ] docker-compose.yml file created
- [ ] Tenant settings files created (tenant1-settings.json, etc.)

### Container Configuration
- [ ] `extra_hosts` configured in docker-compose.yml
- [ ] Port mappings correct (3001-3008)
- [ ] Volume mounts configured
- [ ] Settings files reference correct MCP URL: `http://host.docker.internal:8000/mcp/`

### Container Deployment
- [ ] Containers started: `docker-compose up -d`
- [ ] All containers running: `docker-compose ps`
- [ ] No error messages in logs: `docker-compose logs`
- [ ] Container can reach host: `docker exec -it aionui-tenant1 curl http://host.docker.internal:8000/mcp/`

---

## Phase 5: Networking & Security

### Firewall Configuration
- [ ] Firewall status checked: `sudo ufw status`
- [ ] Docker network allowed (if needed): `sudo ufw allow from 172.17.0.0/16 to any port 8000`
- [ ] External ports secured (only expose what's needed)
- [ ] SSH port secured (change from 22 if needed)

### Network Verification
- [ ] MCP server listening: `sudo netstat -tlnp | grep 8000`
- [ ] Docker bridge network exists: `docker network ls`
- [ ] Container networking works: Test from inside container
- [ ] No unexpected open ports: `sudo netstat -tlnp`

---

## Phase 6: Monitoring & Verification

### Health Checks
- [ ] MCP server responds: `curl http://127.0.0.1:8000/mcp/`
- [ ] Service status healthy: `sudo systemctl status legal-mcp-hub`
- [ ] Containers running: `docker-compose ps`
- [ ] No errors in MCP logs: `sudo journalctl -u legal-mcp-hub -n 50`
- [ ] No errors in container logs: `docker-compose logs --tail=50`

### Functional Testing
- [ ] Test MCP tool from container (if possible)
- [ ] Verify API keys work (check logs for API calls)
- [ ] Test with actual AionUI application
- [ ] Verify multiple concurrent connections work

### Performance Baseline
- [ ] CPU usage recorded: `top -p $(pgrep -f "python server.py")`
- [ ] Memory usage recorded: `free -h`
- [ ] Disk space checked: `df -h`
- [ ] Network connections counted: `sudo netstat -anp | grep :8000 | wc -l`

---

## Phase 7: Documentation & Handoff

### Documentation
- [ ] Server IP/hostname documented
- [ ] API keys stored securely (password manager)
- [ ] Service commands documented
- [ ] Emergency contacts listed
- [ ] Backup procedures documented

### Backup
- [ ] Configuration backed up: `.env`, service file, docker-compose.yml
- [ ] Backup location documented
- [ ] Restore procedure tested (optional but recommended)

### Access
- [ ] SSH keys distributed to team
- [ ] Sudo access configured for team
- [ ] Log access configured
- [ ] Monitoring access configured (if applicable)

---

## Post-Deployment

### Monitoring Setup (Optional)
- [ ] Log rotation configured
- [ ] Monitoring tools installed (Prometheus, Grafana, etc.)
- [ ] Alerts configured for service down
- [ ] Alerts configured for high resource usage

### Maintenance Schedule
- [ ] Weekly health check scheduled
- [ ] Monthly security updates scheduled
- [ ] Quarterly dependency updates scheduled
- [ ] Backup verification scheduled

---

## Rollback Plan

### If Deployment Fails
1. [ ] Stop service: `sudo systemctl stop legal-mcp-hub`
2. [ ] Stop containers: `docker-compose down`
3. [ ] Review logs for errors
4. [ ] Fix issues or restore from backup
5. [ ] Restart services
6. [ ] Re-verify all checks

### Emergency Contacts
- [ ] Primary contact: _______________
- [ ] Secondary contact: _______________
- [ ] Escalation contact: _______________

---

## Sign-Off

- [ ] All checklist items completed
- [ ] System tested and verified working
- [ ] Documentation complete
- [ ] Team trained on operations
- [ ] Deployment approved

**Deployed by:** _______________  
**Date:** _______________  
**Verified by:** _______________  
**Date:** _______________

---

## Notes

Use this section to document any deviations from the standard deployment or special considerations:

```
[Add deployment-specific notes here]
```

