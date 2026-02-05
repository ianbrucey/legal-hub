# HTTP/SSE Transport Migration - Local Testing

## Overview

Successfully migrated the Legal Intelligence MCP Hub from stdio transport to HTTP/SSE transport for production-ready deployment. This eliminates zombie process issues and provides proper lifecycle management.

## Date: February 5, 2026

---

## Steps Completed

### 1. Verified Server Already Supports HTTP/SSE

The server at `/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/server.py` was already built with HTTP/SSE support:

- Lines 384-406 show full transport support
- Default transport is `streamable-http` (line 387)
- Supports three transports: `stdio`, `streamable-http`, `sse`

### 2. Started MCP Server in HTTP Mode

**Command:**
```bash
cd /Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server
.venv/bin/python server.py --transport streamable-http --port 8000
```

**Server Output:**
```
2026-02-05 11:04:27,353 - legal-mcp-hub - INFO - Starting Legal Intelligence MCP Hub
2026-02-05 11:04:27,353 - legal-mcp-hub - INFO - Transport: streamable-http
2026-02-05 11:04:27,353 - legal-mcp-hub - INFO - Listening on http://0.0.0.0:8000/mcp/
INFO:     Started server process [78945]
INFO:     Waiting for application startup.
2026-02-05 11:04:27,439 - mcp.server.streamable_http_manager - INFO - StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Status:** ✅ Server running successfully on Terminal ID 97236

### 3. Updated Augment Settings

**File:** `~/.augment/settings.json`

**Before (stdio):**
```json
{
  "model": "haiku4.5",
  "indexingAllowDirs": [
    "/Users/ianbruce/Herd/surgery-stuff",
    "/Users/ianbruce/Herd/funlynk"
  ],
  "mcpServers": {
    "legal-hub": {
      "command": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "cwd": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server"
    }
  }
}
```

**After (HTTP):**
```json
{
  "model": "haiku4.5",
  "indexingAllowDirs": [
    "/Users/ianbruce/Herd/surgery-stuff",
    "/Users/ianbruce/Herd/funlynk"
  ],
  "mcpServers": {
    "legal-hub": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Key Change:** Replaced `command`, `args`, and `cwd` with simple `url` pointing to HTTP endpoint.

### 4. Updated Gemini Settings

**File:** `~/.gemini/settings.json`

**Before (stdio):**
```json
{
  "ide": {
    "hasSeenNudge": true
  },
  "mcpServers": {
    "augment-context-engine": { ... },
    "legal-hub": {
      "command": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/.venv/bin/python",
      "args": ["server.py", "--transport", "stdio"],
      "cwd": "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server"
    }
  },
  "security": { ... }
}
```

**After (HTTP):**
```json
{
  "ide": {
    "hasSeenNudge": true
  },
  "mcpServers": {
    "augment-context-engine": { ... },
    "legal-hub": {
      "url": "http://localhost:8000/mcp"
    }
  },
  "security": { ... }
}
```

**Key Change:** Same as Augment - replaced subprocess config with HTTP URL.

---

## Benefits Achieved

✅ **No More Zombie Processes** - Single long-lived server process  
✅ **Easy Environment Variable Updates** - Just restart the server, no process cleanup needed  
✅ **Proper Lifecycle Management** - Server can be monitored and restarted independently  
✅ **Production-Ready Architecture** - Industry standard HTTP/SSE transport  
✅ **Scalable** - Can handle multiple concurrent requests from same or different clients  

---

## Next Steps

### For Local Development

**To restart the server (e.g., after updating .env):**
1. Stop the server: `Ctrl+C` in Terminal 97236
2. Start again: `cd /Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server && .venv/bin/python server.py --transport streamable-http --port 8000`

### For Production Deployment (Remote Server)

See `PRODUCTION-DEPLOYMENT.md` for instructions on deploying to `178.156.239.246` with systemd service.

---

## Testing

To test the MCP server is working, use the Augment or Gemini CLI to call any of the 11 available tools:

1. `deep_research` - Comprehensive web research
2. `quick_search` - Fast web search
3. `write_report` - Generate formatted reports
4. `save_report_to_s3` - Upload reports to S3
5. `search_cases` - Court Listener case search
6. `get_opinion` - Retrieve legal opinion text
7. `lookup_citation` - Look up legal citations
8. `create_file_store` - Create Gemini file store
9. `upload_to_file_store` - Upload to Gemini
10. `file_search_query` - Query Gemini file store
11. `health_check` - Server health check

**Example:** Try using the `deep_research` tool from Augment CLI to verify the HTTP connection works.

