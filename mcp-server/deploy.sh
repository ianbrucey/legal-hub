#!/bin/bash
# Legal Intelligence MCP Hub - Deployment Script
# Usage: ./deploy.sh

set -e  # Exit on error

echo "🚀 Deploying Legal Intelligence MCP Hub..."
echo ""

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

echo ""
echo "✅ Code updated successfully!"
echo ""

# Restart the service
echo "🔄 Restarting legal-mcp service..."
systemctl restart legal-mcp

# Wait a moment for service to start
sleep 2

# Check service status
echo ""
echo "📊 Service Status:"
systemctl status legal-mcp --no-pager -l

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 To view logs: journalctl -u legal-mcp -f"
echo "📝 To check status: systemctl status legal-mcp"

