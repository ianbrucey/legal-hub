#!/bin/bash
#
# Legal Intelligence MCP Hub - Automated Deployment Script
#
# Usage:
#   ./deploy.sh SERVER_IP [SSH_USER]
#
# Example:
#   ./deploy.sh 178.156.239.246
#   ./deploy.sh 178.156.239.246 ubuntu
#
# This script will:
# 1. Install system dependencies
# 2. Clone the repository
# 3. Set up Python virtual environment
# 4. Install Python dependencies
# 5. Configure systemd service
# 6. Start the MCP server
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/ianbrucey/legal-hub.git"
INSTALL_DIR="/opt/legal-hub"
SERVICE_NAME="legal-mcp"
MCP_PORT=8000

# Parse arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Server IP required${NC}"
    echo "Usage: $0 SERVER_IP [SSH_USER]"
    echo "Example: $0 178.156.239.246 ubuntu"
    exit 1
fi

SERVER_IP=$1
SSH_USER=${2:-root}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Legal Intelligence MCP Hub - Deployment Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Target Server:${NC} $SSH_USER@$SERVER_IP"
echo -e "${GREEN}Install Directory:${NC} $INSTALL_DIR"
echo -e "${GREEN}Service Name:${NC} $SERVICE_NAME"
echo -e "${GREEN}Port:${NC} $MCP_PORT"
echo ""

# Test SSH connection
echo -e "${YELLOW}[1/8] Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $SSH_USER@$SERVER_IP "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}Error: Cannot connect to $SSH_USER@$SERVER_IP${NC}"
    echo "Please ensure:"
    echo "  1. Server is accessible"
    echo "  2. SSH key is configured"
    echo "  3. User has sudo privileges"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"
echo ""

# Create deployment script to run on remote server
echo -e "${YELLOW}[2/8] Creating remote deployment script...${NC}"
cat > /tmp/remote_deploy.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git curl build-essential

echo "Checking if repository exists..."
if [ -d "/opt/legal-hub" ]; then
    echo "Repository exists, pulling latest changes..."
    cd /opt/legal-hub
    sudo git pull origin main
else
    echo "Cloning repository..."
    cd /opt
    sudo git clone https://github.com/ianbrucey/legal-hub.git
fi

echo "Setting permissions..."
sudo chown -R $USER:$USER /opt/legal-hub

echo "Creating virtual environment..."
cd /opt/legal-hub/mcp-server
if [ ! -d ".venv" ]; then
    python3.11 -m venv .venv
fi

echo "Installing Python dependencies..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "Checking .env file..."
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  WARNING: Please edit /opt/legal-hub/mcp-server/.env with your API keys!"
fi

echo "Creating systemd service..."
sudo tee /etc/systemd/system/legal-mcp.service > /dev/null << EOF
[Unit]
Description=Legal Intelligence MCP Hub
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/legal-hub/mcp-server
Environment="PATH=/opt/legal-hub/mcp-server/.venv/bin"
ExecStart=/opt/legal-hub/mcp-server/.venv/bin/python server.py --transport streamable-http --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable legal-mcp.service
sudo systemctl restart legal-mcp.service

echo "Waiting for service to start..."
sleep 5

echo "Checking service status..."
sudo systemctl status legal-mcp.service --no-pager || true

echo "Testing server health..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✓ Server is healthy!"
else
    echo "⚠️  Server health check failed. Check logs with: sudo journalctl -u legal-mcp.service -n 50"
fi

REMOTE_SCRIPT

echo -e "${GREEN}✓ Remote deployment script created${NC}"
echo ""

# Copy script to remote server
echo -e "${YELLOW}[3/8] Copying deployment script to server...${NC}"
scp /tmp/remote_deploy.sh $SSH_USER@$SERVER_IP:/tmp/
echo -e "${GREEN}✓ Script copied${NC}"
echo ""

# Execute deployment on remote server
echo -e "${YELLOW}[4/8] Executing deployment on remote server...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
ssh $SSH_USER@$SERVER_IP "bash /tmp/remote_deploy.sh"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment completed${NC}"
echo ""

# Verify deployment
echo -e "${YELLOW}[5/8] Verifying deployment...${NC}"
if ssh $SSH_USER@$SERVER_IP "curl -f http://localhost:8000/health" 2>/dev/null; then
    echo -e "${GREEN}✓ Server is responding${NC}"
else
    echo -e "${RED}✗ Server health check failed${NC}"
fi
echo ""

# Check service status
echo -e "${YELLOW}[6/8] Checking service status...${NC}"
ssh $SSH_USER@$SERVER_IP "sudo systemctl status legal-mcp.service --no-pager | head -20"
echo ""

# Display server info
echo -e "${YELLOW}[7/8] Retrieving server information...${NC}"
ssh $SSH_USER@$SERVER_IP "sudo journalctl -u legal-mcp.service -n 10 --no-pager"
echo ""

# Final instructions
echo -e "${YELLOW}[8/8] Deployment Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Server URL:${NC} http://$SERVER_IP:$MCP_PORT/mcp/"
echo -e "${YELLOW}Health Check:${NC} http://$SERVER_IP:$MCP_PORT/health"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure API keys in .env file:"
echo "   ssh $SSH_USER@$SERVER_IP"
echo "   nano /opt/legal-hub/mcp-server/.env"
echo ""
echo "2. Restart service after updating .env:"
echo "   sudo systemctl restart legal-mcp.service"
echo ""
echo "3. View logs:"
echo "   sudo journalctl -u legal-mcp.service -f"
echo ""
echo "4. Test from your local machine:"
echo "   curl http://$SERVER_IP:$MCP_PORT/health"
echo ""
echo -e "${YELLOW}Client Configuration:${NC}"
echo "Add to ~/.augment/settings.json or ~/.gemini/settings.json:"
echo ""
echo '  "mcpServers": {'
echo '    "legal-hub": {'
echo "      \"url\": \"http://$SERVER_IP:$MCP_PORT/mcp\""
echo '    }'
echo '  }'
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Cleanup
rm /tmp/remote_deploy.sh

exit 0

