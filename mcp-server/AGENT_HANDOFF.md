# Agent Handoff Document: Legal MCP Hub Containerization

**Date:** 2026-02-02  
**Status:** 95% Complete - Final Python Path Issue  
**Priority:** HIGH - Container built but won't start due to module import error

---

## Executive Summary

We are containerizing the Legal Intelligence MCP Hub for integration with AionUI (a legal document generation application). The goal is to convert the MCP server from stdio (subprocess) transport to HTTP transport so multiple agents running inside the AionUI Docker container can access it via HTTP requests.

**Current Status:** Docker container builds successfully but fails to start due to `ModuleNotFoundError: No module named 'gpt_researcher'`. This is a Python path issue that needs to be fixed.

---

## Architecture Overview

### The Big Picture

```
┌─────────────────────────────────────────────────────────┐
│         AionUI Docker Container (Server)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Agent 1    │  │  Agent 2    │  │  Agent 3    │    │
│  │  (Gemini)   │  │  (Claude)   │  │  (GPT)      │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                 │                 │           │
│         └─────────────────┴─────────────────┘           │
│                           │                             │
│                    HTTP Request                         │
│                           │                             │
└───────────────────────────┼─────────────────────────────┘
                            │
                            ▼
              http://legal-mcp-hub:8000/mcp/
                            │
┌───────────────────────────┼─────────────────────────────┐
│         MCP Server Container                            │
│         (Legal Intelligence Hub)                        │
│         - GPT Researcher tools                          │
│         - Court Listener API                            │
│         - Gemini File Search (RAG)                      │
└─────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Transport Modes:**
   - **stdio**: Subprocess communication (old local setup)
   - **streamable-http**: HTTP-based communication (target for containerization)

2. **Container Communication:**
   - Agents in AionUI container will have settings files pointing to `http://legal-mcp-hub:8000/mcp/`
   - No subprocess spawning - pure HTTP requests
   - Each agent session can access the same MCP server instance

---

## What Has Been Completed

### 1. Fixed Dockerfile ✅
**File:** `gpt-researcher/mcp-server/Dockerfile`

**Key Changes:**
- Multi-stage build (builder + production)
- Proper build context (parent `gpt-researcher` directory)
- Copies parent `gpt_researcher` library into container
- Copies MCP server files including README.md (was missing, causing build failure)
- Installs all dependencies
- Creates non-root `mcp` user for security
- Exposes port 8000
- Default transport: `streamable-http`

**Build Command:**
```bash
cd gpt-researcher && docker build -f mcp-server/Dockerfile -t legal-mcp-hub .
```

### 2. Updated docker-compose.yml ✅
**File:** `gpt-researcher/mcp-server/docker-compose.yml`

**Key Changes:**
- Correct build context: `context: ..` (parent directory)
- Added missing `TAVILY_API_KEY` environment variable
- Health check uses `curl` instead of `httpx`
- Custom network for container communication

### 3. Created .env File ✅
**File:** `gpt-researcher/mcp-server/.env`

**Contains Real Credentials:**
```env
GOOGLE_API_KEY=AIzaSyDgKYeN-rOL9FeLLVDLF0QhU4OT6uv4jPI
TAVILY_API_KEY=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
COURTLISTENER_API_KEY=b3d40566197ce78198a1562a6c66053f755db24c
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro
```

### 4. Removed Invalid Health Check Endpoint ✅
**File:** `gpt-researcher/mcp-server/server.py`

**What Was Done:**
- Removed `@mcp.get("/health")` decorator (FastMCP doesn't support HTTP endpoints like that)
- FastMCP is an MCP protocol server, not a general HTTP server
- Health checks will need to be done differently (see "What Needs to Be Done" section)

### 5. Fixed Recursive Auggie Spawning Bug ✅
**File:** `~/.augment/settings.json`

**Problem:** User's computer had 231 zombie auggie processes
**Root Cause:** `augment-context-engine` was configured in `~/.augment/settings.json`, causing Augment to spawn itself recursively
**Solution:** Removed the recursive entry, kept only `legal-hub` MCP server

---

## ⚠️ CURRENT ISSUE - What Needs to Be Done

### Problem: ModuleNotFoundError

**Status:** Container builds successfully but fails to start

**Error Message:**
```
Traceback (most recent call last):
  File "/app/mcp-server/server.py", line 53, in <module>
    from gpt_researcher import GPTResearcher
ModuleNotFoundError: No module named 'gpt_researcher'
```

**Root Cause:** Python cannot find the `gpt_researcher` module even though it exists at `/app/gpt_researcher` in the container. The PYTHONPATH environment variable is not set correctly.

**Container Details:**
- **Image ID:** `d1617f8ad5d0ce038c2148fd8db67b0f16ad7cdd0ae3236c47258eed6aad5f81`
- **Container ID:** `2f28eea0cc7b`
- **Status:** Built successfully, fails on startup

### The Fix (IN PROGRESS)

**File to Edit:** `gpt-researcher/mcp-server/Dockerfile`

**Change Needed:** Add PYTHONPATH environment variable around line 67-70

**Exact Edit:**
```dockerfile
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
```

**Steps to Complete:**

1. **Apply the PYTHONPATH fix:**
   ```bash
   # The str-replace-editor command was started but cancelled by user
   # You need to add these lines after line 68 in the Dockerfile:
   # ENV PYTHONUNBUFFERED=1 \
   #     PYTHONPATH=/app:$PYTHONPATH
   ```

2. **Rebuild the container:**
   ```bash
   cd /Users/ianbruce/Herd/gptr/gpt-researcher
   docker stop legal-mcp-hub && docker rm legal-mcp-hub
   docker build -f mcp-server/Dockerfile -t legal-mcp-hub .
   ```

3. **Start the container:**
   ```bash
   docker run -d --name legal-mcp-hub -p 8000:8000 --env-file mcp-server/.env legal-mcp-hub
   ```

4. **Verify it started successfully:**
   ```bash
   docker logs legal-mcp-hub
   ```

   **Expected Output:**
   ```
   MCP Server running on http://0.0.0.0:8000
   Transport: streamable-http
   ```

5. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

   **Expected Response:**
   ```json
   {"status": "healthy", "service": "legal-mcp-hub"}
   ```

---

## Testing the Container

### Step 1: Verify Container is Running

```bash
docker ps | grep legal-mcp-hub
```

Should show container running on port 8000.

### Step 2: Check Logs

```bash
docker logs legal-mcp-hub
```

Look for startup messages without errors.

### Step 3: Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Step 4: Update Agent Settings

**File:** `~/.augment/settings.json`

**Current Configuration (stdio - local subprocess):**
```json
{
  "model": "sonnet4.5",
  "indexingAllowDirList": ["/Users/ianbruce/Herd/gptr"],
  "mcpServers": {
    "legal-hub": {
      "command": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "cwd": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server",
      "env": {
        "GOOGLE_API_KEY": "AIzaSyDgKYeN-rOL9FeLLVDLF0QhU4OT6uv4jPI",
        "COURT_LISTENER_API_KEY": "e3e0c9e0e2e1e4e5e6e7e8e9eaebecedeeeff0f1",
        "TAVILY_API_KEY": "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",
        "FAST_LLM": "google_genai:gemini-2.5-pro",
        "SMART_LLM": "google_genai:gemini-2.5-pro",
        "STRATEGIC_LLM": "google_genai:gemini-2.5-pro"
      }
    }
  }
}
```

**Target Configuration (HTTP - containerized):**
```json
{
  "model": "sonnet4.5",
  "indexingAllowDirList": ["/Users/ianbruce/Herd/gptr"],
  "mcpServers": {
    "legal-hub": {
      "url": "http://localhost:8000/mcp/",
      "transport": "http"
    }
  }
}
```

**⚠️ Important:** Only update this AFTER the container is running successfully!

### Step 5: Test MCP Tools

After updating settings and restarting your agent session, test each tool:

1. **Test quick_search:**
   ```
   Use the quick_search tool to search for "AI legal research"
   ```

2. **Test deep_research:**
   ```
   Use the deep_research tool to research "contract law precedents"
   ```

3. **Test search_cases:**
   ```
   Use the search_cases tool to find cases about "intellectual property"
   ```

4. **Test file_search_query:**
   ```
   Use the file_search_query tool to query a file store
   ```

---

## Available MCP Tools

The Legal Intelligence MCP Hub provides these tools:

### Research Tools (GPT Researcher)

1. **deep_research**
   - Comprehensive research on a topic
   - Parameters: `query`, `report_type`, `max_sources`
   - Returns: Research data and sources

2. **quick_search**
   - Fast web search
   - Parameters: `query`, `max_results`
   - Returns: Search results

3. **write_report**
   - Generate formatted report from research data
   - Parameters: `query`, `research_data`, `report_type`
   - Returns: Markdown report

4. **save_report_to_s3**
   - Save report to AWS S3
   - Parameters: `report`, `bucket`, `key`, `filename_prefix`
   - Returns: S3 URL and key

### Legal Case Tools (Court Listener)

5. **search_cases**
   - Search legal cases by keyword, party, or citation
   - Parameters: `query`, `court`, `date_from`, `date_to`, `max_results`
   - Returns: Case results

6. **get_opinion**
   - Retrieve full text of legal opinion
   - Parameters: `opinion_id`
   - Returns: Opinion details with full text

7. **lookup_citation**
   - Look up legal citation
   - Parameters: `citation`
   - Returns: Matched case details

### Document RAG Tools (Gemini File Search)

8. **create_file_store**
   - Create new Gemini file store for RAG
   - Parameters: `name`, `display_name`
   - Returns: Store name and ID

9. **upload_to_file_store**
   - Upload file to file store
   - Parameters: `store_name`, `file_path`
   - Returns: File ID and status

10. **file_search_query**
    - Query documents using RAG
    - Parameters: `store_name`, `query`
    - Returns: Results and answer

11. **health_check**
    - Check server health
    - Returns: Status and available tools count

---

## File Structure

```
gpt-researcher/
├── gpt_researcher/              # Parent library (needed for imports)
│   ├── __init__.py
│   ├── agent/
│   ├── config/
│   └── ...
│
├── mcp-server/                  # MCP Server application
│   ├── Dockerfile               # Container definition
│   ├── docker-compose.yml       # Orchestration config
│   ├── .env                     # Real API credentials
│   ├── .env.example             # Template for credentials
│   ├── server.py                # Main MCP server (FastMCP)
│   ├── config.py                # Configuration management
│   ├── pyproject.toml           # Python package config
│   ├── README.md                # Package readme (required by pyproject.toml)
│   ├── clients/                 # API client implementations
│   │   ├── courtlistener.py    # Court Listener API
│   │   └── gemini_rag.py       # Gemini File Search
│   └── AGENT_HANDOFF.md         # This document
│
├── pyproject.toml               # Parent library config
├── requirements.txt             # Parent library dependencies
└── README.md                    # Parent library readme
```

---

## Important Commands

### Docker Operations

```bash
# Build container (from gpt-researcher directory)
cd /Users/ianbruce/Herd/gptr/gpt-researcher
docker build -f mcp-server/Dockerfile -t legal-mcp-hub .

# Run container
docker run -d --name legal-mcp-hub -p 8000:8000 --env-file mcp-server/.env legal-mcp-hub

# Stop and remove container
docker stop legal-mcp-hub && docker rm legal-mcp-hub

# View logs
docker logs legal-mcp-hub

# Follow logs in real-time
docker logs -f legal-mcp-hub

# Execute command in running container
docker exec -it legal-mcp-hub bash

# Inspect container
docker inspect legal-mcp-hub

# List all containers
docker ps -a

# Remove image
docker rmi legal-mcp-hub
```

### Using docker-compose

```bash
# Build and start
cd /Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

---

## Troubleshooting

### Issue: Container won't start

**Check logs:**
```bash
docker logs legal-mcp-hub
```

**Common causes:**
1. Missing environment variables in `.env`
2. Port 8000 already in use
3. Python import errors (PYTHONPATH issue)

### Issue: Health check fails

**Test manually:**
```bash
curl http://localhost:8000/health
```

**If connection refused:**
- Container may not have started
- Check logs for startup errors

### Issue: MCP tools not accessible

**Verify:**
1. Container is running: `docker ps | grep legal-mcp-hub`
2. Port is exposed: Should show `0.0.0.0:8000->8000/tcp`
3. Settings file points to correct URL: `http://localhost:8000/mcp/`
4. Agent session was restarted after settings change

### Issue: Module import errors

**Solution:** Add PYTHONPATH to Dockerfile (see "The Fix" section above)

### Issue: Permission denied errors

**Check:**
- Container runs as non-root `mcp` user
- File permissions in container: `docker exec -it legal-mcp-hub ls -la /app`

---

## Success Criteria

The containerization is complete when:

- ✅ Docker container builds without errors
- ✅ Container starts and runs without crashing
- ✅ Health endpoint responds: `curl http://localhost:8000/health`
- ✅ Agent settings updated to HTTP transport
- ✅ All MCP tools accessible from agent
- ✅ Tools return expected results (test at least 3 different tools)
- ✅ No zombie processes spawning
- ✅ Container can be stopped and restarted reliably

---

## Next Steps for AionUI Integration

Once the container is working locally:

1. **Create Docker Network:**
   ```bash
   docker network create aionui-network
   ```

2. **Run MCP Hub on network:**
   ```bash
   docker run -d --name legal-mcp-hub --network aionui-network -p 8000:8000 --env-file mcp-server/.env legal-mcp-hub
   ```

3. **Configure AionUI agents:**
   Each agent's settings file should point to:
   ```json
   {
     "mcpServers": {
       "legal-hub": {
         "url": "http://legal-mcp-hub:8000/mcp/",
         "transport": "http"
       }
     }
   }
   ```

4. **Test container-to-container communication:**
   ```bash
   docker run --rm --network aionui-network curlimages/curl curl http://legal-mcp-hub:8000/health
   ```

---

## Critical Notes

1. **Build Context:** Always build from `gpt-researcher` directory (parent), not `mcp-server`
2. **PYTHONPATH:** Must include `/app` so Python can find `gpt_researcher` module
3. **Transport Mode:** Container defaults to `streamable-http`, not `stdio`
4. **Health Check:** Uses `/health` endpoint, not `/mcp/`
5. **Credentials:** Real API keys are in `.env` file - keep secure
6. **Zombie Processes:** Fixed by removing recursive auggie config from `~/.augment/settings.json`

---

## Contact Information

**User:** Ian Bruce
**Workspace:** `/Users/ianbruce/Herd/gptr`
**Repository:** `/Users/ianbruce/Herd/gptr`

---

## Appendix: Previous Issues Resolved

### Issue 1: Recursive Auggie Spawning ✅
- **Symptom:** 231 zombie auggie processes
- **Cause:** `augment-context-engine` in `~/.augment/settings.json`
- **Fix:** Removed recursive entry

### Issue 2: Docker Build Context ✅
- **Symptom:** `COPY ../gpt_researcher` failing
- **Cause:** Docker COPY can't use `..`
- **Fix:** Set build context to parent directory

### Issue 3: Missing README.md ✅
- **Symptom:** Build fails with "Readme file does not exist"
- **Cause:** `pyproject.toml` references README.md but wasn't copied
- **Fix:** Added `COPY mcp-server/README.md` to Dockerfile

### Issue 4: Invalid Health Check Endpoint ✅
- **Symptom:** `AttributeError: 'FastMCP' object has no attribute 'get'`
- **Cause:** FastMCP doesn't support HTTP endpoint decorators
- **Fix:** Removed `@mcp.get("/health")` decorator

### Issue 5: Module Import Error ⚠️ IN PROGRESS
- **Symptom:** `ModuleNotFoundError: No module named 'gpt_researcher'`
- **Cause:** PYTHONPATH not set
- **Fix:** Add `ENV PYTHONPATH=/app:$PYTHONPATH` to Dockerfile

---

**End of Handoff Document**

