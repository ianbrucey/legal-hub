# Legal Intelligence MCP Hub - Dockerfile
# Multi-stage build for optimized production image
#
# IMPORTANT: This Dockerfile must be built from the parent directory:
#   docker build -f mcp-server/Dockerfile -t legal-mcp-hub .
#
# Or use docker-compose which sets the correct context automatically.

# =============================================================================
# Build Stage
# =============================================================================
FROM python:3.14-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the frozen requirements first (for layer caching)
COPY mcp-server/working-requirements-frozen.txt /build/requirements.txt

# Install all dependencies from the frozen requirements
# This uses the EXACT versions that work in the local venv
RUN pip install --no-cache-dir -r requirements.txt

# Copy parent gpt_researcher library (needed for imports)
COPY gpt_researcher /build/gpt_researcher

# Copy MCP server files
COPY mcp-server/pyproject.toml /build/mcp-server/
COPY mcp-server/README.md /build/mcp-server/
COPY mcp-server/*.py /build/mcp-server/
COPY mcp-server/clients /build/mcp-server/clients

# Install the gpt_researcher package in development mode
WORKDIR /build
COPY pyproject.toml setup.py README.md ./
RUN pip install --no-cache-dir --no-deps -e .

# Install MCP server package (no-deps to avoid overriding frozen versions)
WORKDIR /build/mcp-server
RUN pip install --no-cache-dir --no-deps .

# =============================================================================
# Production Stage
# =============================================================================
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy gpt_researcher library
COPY --from=builder /build/gpt_researcher /app/gpt_researcher

# Copy MCP server application code
COPY --from=builder /build/mcp-server /app/mcp-server

# Set working directory to mcp-server
WORKDIR /app/mcp-server

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp \
    && chown -R mcp:mcp /app

USER mcp

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:$PYTHONPATH

# Health check - use curl instead of httpx to avoid import issues
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server with HTTP transport by default
ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--transport", "streamable-http"]
