#!/bin/bash
# Legal Intelligence MCP Hub - Initial Server Setup Script
# This script sets up the MCP server on a fresh Ubuntu server
# Usage: ./setup-server.sh

set -e  # Exit on error

echo "🚀 Legal Intelligence MCP Hub - Server Setup"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required system packages
echo "📦 Installing required system packages..."
apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Set up project directory
PROJECT_DIR="/root/legal-hub"
echo ""
echo "📁 Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Directory $PROJECT_DIR already exists. Backing up..."
    mv "$PROJECT_DIR" "$PROJECT_DIR.backup-$(date +%Y%m%d-%H%M%S)"
fi

# Clone repository
echo "📥 Cloning repository from GitHub..."
cd /root
git clone https://github.com/ianbrucey/legal-hub.git

# Navigate to MCP server directory
cd "$PROJECT_DIR/mcp-server"

# Create Python virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install fastmcp[all]
pip install gpt-researcher
pip install langchain-google-genai
pip install langchain-openai
pip install langchain-community
pip install boto3
pip install python-dotenv
pip install pydantic
pip install httpx

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# API Keys - REPLACE WITH YOUR ACTUAL KEYS
TAVILY_API_KEY=your_tavily_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# LLM Configuration
FAST_LLM=gemini/gemini-2.0-flash-exp
SMART_LLM=gemini/gemini-2.0-flash-thinking-exp-01-21
STRATEGIC_LLM=gemini/gemini-2.0-flash-thinking-exp-01-21
EMBEDDING=openai:text-embedding-3-small
RETRIEVER=tavily

# AWS Configuration (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1
EOF
    echo "⚠️  IMPORTANT: Edit /root/legal-hub/mcp-server/.env with your actual API keys!"
else
    echo "✅ .env file already exists"
fi

# Install systemd service
echo ""
echo "🔧 Installing systemd service..."
cp legal-mcp.service /etc/systemd/system/legal-mcp.service

# Make deploy script executable
chmod +x deploy.sh

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service to start on boot
echo "✅ Enabling service to start on boot..."
systemctl enable legal-mcp

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit the .env file with your API keys:"
echo "   nano /root/legal-hub/mcp-server/.env"
echo ""
echo "2. Start the service:"
echo "   systemctl start legal-mcp"
echo ""
echo "3. Check service status:"
echo "   systemctl status legal-mcp"
echo ""
echo "4. View logs:"
echo "   journalctl -u legal-mcp -f"
echo ""
echo "5. Configure MCP clients (Augment/Gemini):"
echo "   Update ~/.augment/settings.json and ~/.gemini/settings.json"
echo "   to use: {\"url\": \"http://localhost:8000/mcp\"}"
echo ""
echo "📚 Documentation: /root/legal-hub/mcp-server/PRODUCTION-DEPLOYMENT.md"
echo ""

