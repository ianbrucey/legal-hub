# 🔄 Migration Plan: Fresh MCP Server + Custom Tools

**Date**: 2026-02-02  
**Goal**: Rebuild MCP server from official repo + add custom legal tools  
**Strategy**: Start clean, add incrementally, test at each step

---

## 📊 Current Custom Implementation Analysis

### Custom Tools Added (11 total)

#### 1. **GPT Researcher Tools** (4 tools - ALREADY IN OFFICIAL REPO)
- `deep_research` - Comprehensive research
- `quick_search` - Quick web search
- `write_report` - Format research into report
- `save_report_to_s3` - Upload report to S3

**Status**: ✅ These should already exist in official MCP server

---

#### 2. **Court Listener Tools** (3 tools - CUSTOM ADDITIONS)
- `search_cases` - Search legal cases by keyword/citation
- `get_opinion` - Retrieve full opinion text by ID
- `lookup_citation` - Look up legal citation

**Implementation**: 
- Inline `CourtListenerClient` class in `server.py` (lines 158-200)
- Uses `httpx` for async HTTP requests
- Requires `COURTLISTENER_API_KEY` environment variable

**Dependencies**:
- `httpx` (already in requirements)
- Config: `config.court_listener.base_url`, `config.court_listener.api_key`, `config.court_listener.timeout`

---

#### 3. **Gemini File Search Tools** (3 tools - CUSTOM ADDITIONS)
- `create_file_store` - Create Gemini file store for RAG
- `upload_to_file_store` - Upload files to store
- `file_search_query` - Query documents with RAG

**Implementation**:
- `clients/gemini_client.py` - `GeminiFileSearch` class
- Uses Google Gemini API for document RAG
- Requires `GOOGLE_API_KEY` environment variable

**Dependencies**:
- `google-genai` package
- Config: `config.gemini.api_key`

---

#### 4. **Health Check Tool** (1 tool - CUSTOM ADDITION)
- `health_check` - Server health status

**Implementation**: Simple status endpoint (lines 347-365)

---

## 📁 Custom Files to Preserve

### 1. `clients/gemini_client.py` (242 lines)
**Purpose**: Gemini File Search implementation  
**Key Classes**:
- `GeminiFileSearch` - Main RAG client
- `WebSearchResult`, `FileStoreResult`, `FileUploadResult`, `Citation`, `FileSearchResult` - Pydantic models

### 2. `clients/s3_client.py`
**Purpose**: AWS S3 upload functionality  
**Key Class**: `S3Client`

### 3. Court Listener Client Code
**Purpose**: Legal case search  
**Location**: Inline in `server.py` (lines 158-200)  
**Key Class**: `CourtListenerClient`

### 4. Configuration Extensions
**Purpose**: Config for custom tools  
**Location**: `config.py`  
**Additions**:
- `court_listener` section (base_url, api_key, timeout)
- `gemini` section (api_key)

---

## 🎯 Migration Strategy

### Phase 1: Clone & Verify Official Repo ✅ **COMPLETE**

**Status**: ✅ **CLONED SUCCESSFULLY**

**Location**: `/Users/ianbruce/Herd/gptr/gptr-mcp-official`

**Key Findings**:
- ✅ Uses Python 3.11 (not 3.14 - more stable)
- ✅ Simple, clean Dockerfile (31 lines)
- ✅ Minimal requirements.txt (17 lines)
- ✅ Uses `gpt-researcher>=0.14.0` package (not local copy)
- ✅ Has SSE transport for Docker (auto-detects)
- ✅ Includes health check endpoint
- ✅ Has test script (`test_mcp_server.py`)

**Official Tools** (5 tools):
1. `deep_research` - Deep web research
2. `quick_search` - Fast search
3. `write_report` - Generate report
4. `get_research_sources` - Get sources
5. `get_research_context` - Get context

**Next Step**: Build and test the official Docker image

```bash
cd /Users/ianbruce/Herd/gptr/gptr-mcp-official

# Build Docker image
docker build -t gptr-mcp-official .

# Test it works
docker run -d --name gptr-test \
  -p 8001:8000 \
  -e OPENAI_API_KEY=xxx \
  -e TAVILY_API_KEY=xxx \
  gptr-mcp-official

# Verify
docker logs gptr-test
curl http://localhost:8001/health
```

**Success Criteria**:
- ✅ Docker build completes without errors
- ✅ Container starts and stays running
- ✅ Health endpoint responds
- ✅ No import errors in logs

---

### Phase 2: Add Court Listener Tools 🎯
**What to Add**:
1. Copy `CourtListenerClient` class to `server.py`
2. Add 3 Court Listener tool functions
3. Add `court_listener` config section
4. Add `COURTLISTENER_API_KEY` to environment

**Files to Modify**:
- `server.py` - Add client class + 3 tools
- `config.py` - Add court_listener config
- `.env.example` - Document COURTLISTENER_API_KEY
- `Dockerfile` - Ensure httpx is installed (should already be)

**Test**:
```bash
docker build -t legal-mcp-v2 .
docker run -d --name legal-test-v2 \
  -p 8002:8000 \
  -e GOOGLE_API_KEY=xxx \
  -e TAVILY_API_KEY=xxx \
  -e COURTLISTENER_API_KEY=xxx \
  legal-mcp-v2

# Test Court Listener tools work
```

---

### Phase 3: Add Gemini File Search Tools 🎯
**What to Add**:
1. Copy `clients/gemini_client.py`
2. Add 3 Gemini File Search tool functions
3. Ensure `google-genai` package is installed

**Files to Add/Modify**:
- `clients/gemini_client.py` - Full file (242 lines)
- `server.py` - Add 3 Gemini tools
- `requirements.txt` - Ensure `google-genai>=1.0.0`

**Test**:
```bash
docker build -t legal-mcp-v3 .
docker run -d --name legal-test-v3 \
  -p 8003:8000 \
  -e GOOGLE_API_KEY=xxx \
  -e TAVILY_API_KEY=xxx \
  -e COURTLISTENER_API_KEY=xxx \
  legal-mcp-v3

# Test Gemini File Search tools work
```

---

### Phase 4: Final Integration & Testing 🎯
**What to Add**:
1. Add health_check tool
2. Update server description
3. Final testing of all 11 tools

**Test All Tools**:
- ✅ deep_research
- ✅ quick_search
- ✅ write_report
- ✅ save_report_to_s3
- ✅ search_cases
- ✅ get_opinion
- ✅ lookup_citation
- ✅ create_file_store
- ✅ upload_to_file_store
- ✅ file_search_query
- ✅ health_check

---

## 📦 Final Deliverable

**New Repository**: `legal-intelligence-mcp-hub`

**Structure**:
```
legal-intelligence-mcp-hub/
├── server.py                    # Main server with all 11 tools
├── config.py                    # Config with court_listener + gemini
├── clients/
│   ├── gemini_client.py        # Gemini File Search
│   └── s3_client.py            # S3 uploads
├── Dockerfile                   # Working Docker setup
├── docker-compose.yml          # Easy deployment
├── requirements.txt            # All dependencies
├── .env.example                # All required env vars
└── README.md                   # Complete documentation
```

---

## 🔑 Environment Variables Needed

```env
# Core (from official repo)
GOOGLE_API_KEY=xxx
TAVILY_API_KEY=xxx
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro

# Custom additions
COURTLISTENER_API_KEY=xxx
AWS_ACCESS_KEY_ID=xxx          # Optional (for S3)
AWS_SECRET_ACCESS_KEY=xxx      # Optional (for S3)
```

---

## ✅ Success Criteria

- [ ] Official MCP server Docker image builds and runs
- [ ] Court Listener tools added and tested
- [ ] Gemini File Search tools added and tested
- [ ] All 11 tools functional in Docker
- [ ] No dependency conflicts
- [ ] No import errors
- [ ] Clean, maintainable codebase
- [ ] Comprehensive documentation

---

**Next Step**: Execute Phase 1 - Clone and verify official repo works

