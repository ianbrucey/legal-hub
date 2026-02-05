# Legal Intelligence MCP Hub - Dockerfile
# Simplified single-stage build that mirrors the working production setup
#
# Build from the mcp-server directory:
#   docker build -t legal-mcp-hub .
#
# Run with environment variables:
#   docker run -p 8000:8000 --env-file .env legal-mcp-hub

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies in the same order as production
# This matches what's working on the server
RUN pip install --no-cache-dir \
    fastmcp[all] \
    gpt-researcher \
    langchain-google-genai \
    langchain-openai \
    langchain-community \
    boto3 \
    python-dotenv \
    pydantic \
    httpx

# Copy application code
COPY server.py config.py ./
COPY clients ./clients/

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp \
    && chown -R mcp:mcp /app

USER mcp

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/mcp/ || exit 1

# Run server with HTTP transport by default
ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--transport", "streamable-http"]
