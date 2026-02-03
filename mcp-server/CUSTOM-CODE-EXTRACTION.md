# 📦 Custom Code Extraction Guide

This document contains all custom code that needs to be added to the official MCP server.

---

## 1️⃣ Court Listener Client (Add to `server.py`)

### Location: After GPT Researcher imports, before tool definitions

```python
# ============================================================================
# Court Listener Tools
# ============================================================================
import httpx


class CourtListenerClient:
    """Lightweight Court Listener client."""

    def __init__(self):
        self.base_url = config.court_listener.base_url
        self.token = config.court_listener.api_key
        self.timeout = config.court_listener.timeout
        self.headers = {
            "Authorization": f"Token {self.token}" if self.token else "",
        }

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                data=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()


_court_client = None

def get_court_client():
    global _court_client
    if _court_client is None:
        _court_client = CourtListenerClient()
    return _court_client
```

---

## 2️⃣ Court Listener Tools (Add to `server.py`)

```python
@mcp.tool()
async def search_cases(
    query: str,
    court: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    max_results: int = 10,
) -> dict:
    """
    Search legal cases by keyword, party name, or citation.

    Args:
        query: Search query (keyword, party name, or citation)
        court: Court ID to filter by (e.g., 'scotus', 'ca9')
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        max_results: Maximum results to return (default 10)

    Returns:
        Dictionary with 'results' (list) and 'count' (int)
    """
    client = get_court_client()
    params = {
        "q": query,
        "court": court,
        "filed_after": date_from,
        "filed_before": date_to,
        "order_by": "score desc",
        "page_size": max_results,
    }
    result = await client.get("/search/", params=params)
    return {
        "results": result.get("results", []),
        "count": result.get("count", 0),
    }


@mcp.tool()
async def get_opinion(opinion_id: int) -> dict:
    """
    Retrieve the full text of a legal opinion by its ID.

    Args:
        opinion_id: Court Listener opinion ID

    Returns:
        Dictionary with opinion details including full text
    """
    client = get_court_client()
    return await client.get(f"/opinions/{opinion_id}/")


@mcp.tool()
async def lookup_citation(citation: str) -> dict:
    """
    Look up a legal citation and return the matching case.

    Args:
        citation: Legal citation (e.g., '384 U.S. 436')

    Returns:
        Dictionary with matched citations and case details
    """
    client = get_court_client()
    result = await client.post("/citation-lookup/", data={"text": citation})
    return {"citations": result if isinstance(result, list) else [result]}
```

---

## 3️⃣ Gemini File Search Tools (Add to `server.py`)

```python
# ============================================================================
# Gemini File Search Tools
# ============================================================================
from clients.gemini_client import GeminiFileSearch


@mcp.tool()
async def create_file_store(name: str, display_name: str | None = None) -> dict:
    """
    Create a new Gemini file store for document RAG.

    Args:
        name: Unique name for the store
        display_name: Human-readable display name

    Returns:
        Dictionary with 'store_name' and 'store_id'
    """
    fs = GeminiFileSearch()
    result = await fs.create_store(name=name, display_name=display_name)
    return result


@mcp.tool()
async def upload_to_file_store(
    store_name: str,
    file_path: str,
) -> dict:
    """
    Upload a file to a Gemini file store.

    Args:
        store_name: Name of the file store
        file_path: Local path to the file

    Returns:
        Dictionary with 'file_id' and 'status'
    """
    fs = GeminiFileSearch()
    return await fs.upload_file(store_name=store_name, file_path=file_path)


@mcp.tool()
async def file_search_query(
    store_name: str,
    query: str,
) -> dict:
    """
    Query documents in a Gemini file store using RAG.

    Args:
        store_name: Name of the file store
        query: Search query

    Returns:
        Dictionary with 'results' and 'answer'
    """
    fs = GeminiFileSearch()
    return await fs.query(store_name=store_name, query=query)
```

---

## 4️⃣ Health Check Tool (Add to `server.py`)

```python
# ============================================================================
# Health Check
# ============================================================================
@mcp.tool()
async def health_check() -> dict:
    """
    Check server health and list available tools.
    
    Returns:
        Dictionary with 'status', 'server_name', and 'tools' count
    """
    return {
        "status": "healthy",
        "server_name": "Legal Intelligence Hub",
        "version": "1.0.0",
        "tools": {
            "gpt_researcher": ["deep_research", "quick_search", "write_report", "save_report_to_s3"],
            "court_listener": ["search_cases", "get_opinion", "lookup_citation"],
            "gemini": ["create_file_store", "upload_to_file_store", "file_search_query"],
        },
    }
```

---

## 5️⃣ Config Extensions (Add to `config.py`)

```python
# Court Listener configuration
class CourtListenerConfig(BaseModel):
    base_url: str = "https://www.courtlistener.com/api/rest/v3"
    api_key: str = os.getenv("COURTLISTENER_API_KEY", "")
    timeout: int = 30

# Gemini configuration (if not already present)
class GeminiConfig(BaseModel):
    api_key: str = os.getenv("GOOGLE_API_KEY", "")

# Add to main Config class
class Config(BaseModel):
    # ... existing config ...
    court_listener: CourtListenerConfig = CourtListenerConfig()
    gemini: GeminiConfig = GeminiConfig()
```

---

## 6️⃣ Files to Copy Entirely

### `clients/gemini_client.py`
**Action**: Copy entire file from current implementation  
**Location**: `gpt-researcher/mcp-server/clients/gemini_client.py`  
**Size**: 242 lines

### `clients/s3_client.py`
**Action**: Copy entire file from current implementation  
**Location**: `gpt-researcher/mcp-server/clients/s3_client.py`

---

## 7️⃣ Environment Variables to Add

Add to `.env.example`:
```env
# Court Listener API
COURTLISTENER_API_KEY=your_courtlistener_api_key_here

# AWS S3 (optional - for report uploads)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

---

## 📋 Integration Checklist

- [ ] Add Court Listener client class to server.py
- [ ] Add 3 Court Listener tools to server.py
- [ ] Copy clients/gemini_client.py
- [ ] Copy clients/s3_client.py
- [ ] Add 3 Gemini File Search tools to server.py
- [ ] Add health_check tool to server.py
- [ ] Update config.py with court_listener and gemini sections
- [ ] Update .env.example with new environment variables
- [ ] Verify httpx is in requirements.txt
- [ ] Verify google-genai is in requirements.txt
- [ ] Test all 11 tools work

---

**Total Custom Code**: ~300 lines + 2 client files

