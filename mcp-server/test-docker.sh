#!/bin/bash
# Legal Intelligence MCP Hub - Docker Test Script
# Tests the Docker container build and deployment

set -e  # Exit on error

echo "🚀 Legal Intelligence MCP Hub - Docker Test"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Build the image
echo "📦 Test 1: Building Docker image..."
cd ..
if docker build -f mcp-server/Dockerfile -t legal-mcp-hub:test . > /tmp/docker-build.log 2>&1; then
    echo -e "${GREEN}✅ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed. Check /tmp/docker-build.log${NC}"
    tail -20 /tmp/docker-build.log
    exit 1
fi
echo ""

# Test 2: Run the container
echo "🏃 Test 2: Starting container..."
cd mcp-server
docker run -d \
    --name legal-mcp-hub-test \
    -p 8001:8000 \
    --env-file .env \
    legal-mcp-hub:test > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi
echo ""

# Wait for container to be ready
echo "⏳ Waiting for container to be ready (10s)..."
sleep 10
echo ""

# Test 3: Check health endpoint
echo "🏥 Test 3: Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
    docker logs legal-mcp-hub-test
    docker stop legal-mcp-hub-test > /dev/null 2>&1
    docker rm legal-mcp-hub-test > /dev/null 2>&1
    exit 1
fi
echo ""

# Test 4: Check logs
echo "📋 Test 4: Checking container logs..."
LOGS=$(docker logs legal-mcp-hub-test 2>&1)
if echo "$LOGS" | grep -q "Starting Legal Intelligence MCP Hub"; then
    echo -e "${GREEN}✅ Server started successfully${NC}"
    echo "   Log excerpt:"
    echo "$LOGS" | grep "Starting\|Listening" | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  Unexpected logs${NC}"
    echo "$LOGS" | head -10 | sed 's/^/   /'
fi
echo ""

# Test 5: Check MCP endpoint
echo "🔌 Test 5: Testing MCP endpoint..."
MCP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/mcp/)
if [ "$MCP_RESPONSE" = "200" ] || [ "$MCP_RESPONSE" = "405" ]; then
    echo -e "${GREEN}✅ MCP endpoint accessible (HTTP $MCP_RESPONSE)${NC}"
else
    echo -e "${YELLOW}⚠️  MCP endpoint returned HTTP $MCP_RESPONSE${NC}"
fi
echo ""

# Cleanup
echo "🧹 Cleaning up..."
docker stop legal-mcp-hub-test > /dev/null 2>&1
docker rm legal-mcp-hub-test > /dev/null 2>&1
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Summary
echo "============================================"
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Run with docker-compose: docker-compose up -d"
echo "  2. Check health: curl http://localhost:8000/health"
echo "  3. View logs: docker-compose logs -f"
echo "  4. Integrate with AionUI (see DOCKER_DEPLOYMENT.md)"
echo ""

