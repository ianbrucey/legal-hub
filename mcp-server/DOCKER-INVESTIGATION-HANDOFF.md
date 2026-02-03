# 🔬 Docker Investigation Handoff - Legal Intelligence MCP Hub

**Status**: ❌ DOCKER BUILD FAILING
**Date**: 2026-02-02
**Priority**: HIGH - Blocks containerized deployment

---

## 🎯 Mission

**Goal**: Get the Legal Intelligence MCP Hub running in a Docker container.

**Constraint**: ⚠️ **NO CHANGES TO PYTHON FILES ALLOWED** ⚠️

The code works perfectly locally. The problem is purely environmental - we need to replicate the working local environment in Docker.

---

## ✅ What Works (Local Environment)

The MCP server runs **perfectly** in the local `.venv` environment:

```bash
# This works flawlessly:
cd /Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server
source .venv/bin/activate
python server.py --transport streamable-http --port 8000 --host 127.0.0.1

# Server starts successfully:
# INFO - Starting Legal Intelligence MCP Hub
# INFO - Transport: streamable-http
# INFO - Listening on http://127.0.0.1:8000/mcp/
# INFO - Uvicorn running on http://127.0.0.1:8000
```

**All MCP tools work**: `search_cases`, `lookup_citation`, `deep_research`, etc.

---

## ❌ What Fails (Docker)

Every Docker build attempt fails with **dependency conflicts** during `pip install`.

**Typical Error Pattern**:
```
ERROR: Cannot install langchain==0.2.x and langchain-core==0.3.x
ERROR: ResolutionImpossible: different versions conflict
```

---

## 🔍 Root Cause Analysis

### The Working Local Environment

| Component | Version |
|-----------|---------|
| **Python** | 3.14.0 |
| **langchain** | 1.1.2 |
| **langchain-classic** | 1.0.0 |
| **langchain-community** | 0.4.1 |
| **langchain-core** | 1.1.1 |
| **mcp** | 1.23.1 |
| **gpt-researcher** | 0.14.5 |

### The Broken Docker Attempts

| Component | Version in requirements.txt |
|-----------|----------------------------|
| **Python** | 3.12 (Dockerfile) |
| **langchain-community** | >=0.3.17 |
| **langchain-core** | >=0.3.61 |

### Why It Works Locally But Fails in Docker

1. **Local venv was built incrementally** - packages upgraded over time, pip resolved conflicts dynamically
2. **Docker does fresh install** - all constraints evaluated simultaneously, conflicts detected
3. **Version mismatch** - Local has LangChain 1.x, requirements.txt has LangChain 0.3.x constraints
4. **Python version difference** - Local uses 3.14, Docker uses 3.12

---

## 📁 Critical Files

### Working Environment Export
**File**: `gpt-researcher/mcp-server/working-requirements-frozen.txt`

This is a `pip freeze` export of the working local .venv (175 packages).
**This is your golden reference** - these exact versions work together.

### Key LangChain Packages (from working venv)
```
langchain==1.1.2
langchain-classic==1.0.0
langchain-community==0.4.1
langchain-core==1.1.1
langchain-google-genai==3.2.0
langchain-ollama==1.0.0
langchain-openai==1.1.0
langchain-text-splitters==1.0.0
langgraph==1.0.4
langgraph-checkpoint==3.0.1
langsmith==0.4.56
```

### Parent Requirements (CONFLICTING)
**File**: `gpt-researcher/requirements.txt`

This file has OLDER LangChain version constraints that conflict with the working environment.

### Current Dockerfile (BROKEN)
**File**: `gpt-researcher/mcp-server/Dockerfile`

Uses Python 3.12 and installs from parent requirements.txt - causes conflicts.

---

## 🎯 Your Mission

1. **Investigate** the working local environment thoroughly
2. **Replicate** that exact environment in Docker
3. **DO NOT** modify any Python source files (server.py, config.py, clients/*.py)
4. **You CAN** modify: Dockerfile, docker-compose.yml, requirements files, build scripts

---

## 💡 Suggested Approaches

### Approach 1: Use Frozen Requirements
```dockerfile
# Use the exact frozen requirements from working venv
COPY working-requirements-frozen.txt /app/
RUN pip install --no-cache-dir -r working-requirements-frozen.txt
```

### Approach 2: Match Python Version
```dockerfile
# Use Python 3.14 to match local environment
FROM python:3.14-slim
```

### Approach 3: Multi-stage with Exact Versions
Build a requirements file that pins exact versions matching the working venv.

### Approach 4: Copy the venv
Some projects copy a pre-built venv into Docker (less portable but guaranteed to work).

---

## 🧪 Testing Your Solution

### 1. Build the Image
```bash
cd /Users/ianbruce/Herd/gptr/gpt-researcher
docker build -f mcp-server/Dockerfile -t legal-mcp-hub .
```

### 2. Run the Container
```bash
docker run -d --name legal-mcp-test \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=AIzaSyDgKYeN-rOL9FeLLVDLF0QhU4OT6uv4jPI \
  -e TAVILY_API_KEY=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 \
  -e COURTLISTENER_API_KEY=b3d40566197ce78198a1562a6c66053f755db24c \
  legal-mcp-hub
```

### 3. Verify It Works
```bash
# Check logs
docker logs legal-mcp-test

# Test endpoint
curl http://localhost:8000/mcp/

# Expected: Server running, no import errors
```

### 4. Cleanup
```bash
docker stop legal-mcp-test && docker rm legal-mcp-test
```

---

## 📋 Success Criteria

- [ ] Docker image builds without errors
- [ ] Container starts without import errors
- [ ] Server logs show "Listening on http://0.0.0.0:8000/mcp/"
- [ ] `curl http://localhost:8000/mcp/` returns MCP protocol response
- [ ] No Python source files were modified

---

## 🚫 What NOT To Do

1. ❌ Don't modify `server.py`
2. ❌ Don't modify `config.py`

---

## 📊 Additional Technical Context

### How the Local venv Was Created

The local venv was built incrementally over time:
1. Started with `gpt-researcher` package installation
2. Added MCP dependencies
3. Upgraded LangChain packages as new versions released
4. pip resolved conflicts dynamically during each upgrade

This incremental approach allowed pip to find a working set of versions. A fresh Docker install tries to resolve ALL constraints at once, which fails.

### The LangChain Migration

LangChain underwent a major refactor from 0.x to 1.x:
- Old: `langchain==0.2.x`, `langchain-core==0.2.x`
- New: `langchain==1.x`, `langchain-core==1.x`, `langchain-classic==1.0.0`

The working local environment has the NEW versions. The parent `requirements.txt` has OLD version constraints.

### Import Chain

The server imports work like this:
```
server.py
  └── from gpt_researcher import GPTResearcher
        └── from langchain_community.xxx import ...
        └── from langchain_core.xxx import ...
```

So the gpt_researcher library needs LangChain, but it needs the SAME versions as the working venv.

### Build Context Requirement

The Dockerfile must be built from the parent `gpt-researcher` directory because `server.py` imports from `gpt_researcher`:

```bash
# CORRECT (from parent directory):
cd gpt-researcher
docker build -f mcp-server/Dockerfile -t legal-mcp-hub .

# WRONG (from mcp-server directory):
cd mcp-server
docker build -t legal-mcp-hub .  # Will fail - can't find gpt_researcher
```

### Server Startup Sequence

When the server starts, it:
1. Imports all dependencies (LangChain, MCP, etc.)
2. Loads config from environment variables
3. Registers MCP tools
4. Starts Uvicorn HTTP server

If ANY import fails, the server won't start. The local environment passes all imports.

---

## 🔧 Debugging Commands

### Check What's Installed in Docker
```bash
docker run -it legal-mcp-hub pip freeze | grep langchain
```

### Test Imports in Docker
```bash
docker run -it legal-mcp-hub python -c "from gpt_researcher import GPTResearcher; print('OK')"
```

### Interactive Shell
```bash
docker run -it legal-mcp-hub /bin/bash
```

### Compare Versions
```bash
# Local working versions:
cat working-requirements-frozen.txt | grep langchain

# What Docker installed:
docker run -it legal-mcp-hub pip freeze | grep langchain
```

---

## 🏁 Final Notes

The key insight is: **the code is correct, the dependencies are wrong**.

The local venv proves the code works with the right package versions. Your job is to make Docker install those same versions.

Think of it like this:
- Local venv = "this recipe works with these exact ingredients"
- Docker = "trying to make the recipe with different ingredients and it tastes wrong"

Match the ingredients (package versions) and it will work.

```
gpt-researcher/
├── mcp-server/
│   ├── server.py                        # DO NOT MODIFY
│   ├── config.py                        # DO NOT MODIFY
│   ├── clients/                         # DO NOT MODIFY
│   ├── .venv/                           # WORKING LOCAL ENVIRONMENT
│   ├── working-requirements-frozen.txt  # EXPORTED WORKING PACKAGES
│   ├── Dockerfile                       # CAN MODIFY
│   ├── docker-compose.yml               # CAN MODIFY
│   ├── requirements-docker.txt          # CAN MODIFY/REPLACE
│   └── pyproject.toml                   # CAN MODIFY IF NEEDED
├── gpt_researcher/                      # Parent library (needed)
├── requirements.txt                     # Parent requirements (conflicting)
└── pyproject.toml                       # Parent project config
```

---

## 🔑 Environment Variables Needed

```env
GOOGLE_API_KEY=AIzaSyDgKYeN-rOL9FeLLVDLF0QhU4OT6uv4jPI
TAVILY_API_KEY=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
COURTLISTENER_API_KEY=b3d40566197ce78198a1562a6c66053f755db24c
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro
```

---

## 📞 Questions?

If you need clarification:
1. The local venv at `mcp-server/.venv/` is the source of truth
2. `working-requirements-frozen.txt` has the exact package versions
3. Python 3.14.0 is the working Python version
4. The goal is HTTP transport on port 8000

Good luck! 🚀

