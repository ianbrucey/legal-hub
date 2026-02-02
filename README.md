<div align="center" id="top">

# ⚖️ Legal Intelligence Hub

> **AI-Powered Legal Research & Document Analysis MCP Server**

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## 🎯 Overview

The **Legal Intelligence Hub** is a comprehensive Model Context Protocol (MCP) server that provides AI agents with powerful legal research and document analysis capabilities. Built on top of GPT Researcher, it extends the platform with specialized legal tools for case law search, opinion retrieval, and document RAG.

### Why Legal Intelligence Hub?

While standard MCP servers provide basic web search, **Legal Intelligence Hub delivers specialized legal research capabilities**:

- ⚖️ **10M+ Legal Cases** - Search federal and state court opinions
- 📚 **Deep Research** - Comprehensive research with citations and sources
- 🤖 **Document RAG** - Semantic search across legal documents
- 🔍 **Citation Lookup** - Resolve legal citations instantly
- ✨ **Optimized for Legal Work** - Purpose-built for legal professionals and AI agents

### Key Features

- **GPT Researcher Integration** - Deep web research with citations
- **Court Listener API** - Access to 10M+ legal cases and opinions
- **Gemini File Search** - Document RAG for legal document analysis
- **Docker Ready** - Production-ready containerized deployment
- **MCP Compatible** - Works with Claude, Augment, and other MCP clients

## 🚀 Quick Start

### Prerequisites

- Docker (recommended) or Python 3.11+
- API Keys:
  - [Google AI (Gemini)](https://ai.google.dev/) - Required
  - [Tavily Search](https://tavily.com/) - Required
  - [Court Listener](https://www.courtlistener.com/help/api/) - Required
  - [OpenAI](https://platform.openai.com/) - Optional

### Installation with Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/ianbrucey/legal-hub.git
cd legal-hub

# 2. Create .env file with your API keys
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
COURTLISTENER_API_KEY=your_courtlistener_api_key
FAST_LLM=google_genai:gemini-2.5-pro
SMART_LLM=google_genai:gemini-2.5-pro
STRATEGIC_LLM=google_genai:gemini-2.5-pro
COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v3
EOF

# 3. Build and run
docker build -t legal-hub:latest .
docker run -d --name legal-hub -p 8000:8000 --env-file .env legal-hub:latest

# 4. Verify it's running
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"mcp-server"}
```

---

## 🔧 MCP Client Configuration

### Augment AI

Edit `~/.augment/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "streamable-http"
    }
  }
}
```

### Google Gemini

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "streamable-http"
    }
  }
}
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "streamable-http"
    }
  }
}
```

**Note**: Restart your AI client after updating settings.

---

## 📚 Available Tools (11 Total)

### 🔍 GPT Researcher Tools (5)

#### 1. `deep_research`
Conduct comprehensive research on a topic with citations.

**Parameters**:
- `query` (string, required) - Research question or topic
- `report_type` (string, optional) - Type of report: `research_report`, `detailed_report`, `quick_report`
- `max_sources` (int, optional) - Maximum sources to use (default: 10)

**Example**:
```python
deep_research(
    query="Legal implications of AI-generated content",
    report_type="research_report",
    max_sources=10
)
```

#### 2. `quick_search`
Fast web search for immediate answers.

**Parameters**:
- `query` (string, required) - Search query
- `max_results` (int, optional) - Maximum results (default: 5)

**Example**:
```python
quick_search(
    query="What is qualified immunity?",
    max_results=5
)
```

#### 3. `write_report`
Generate formatted research reports.

**Parameters**:
- `query` (string, required) - Original research question
- `research_data` (string, required) - Raw research data
- `report_type` (string, optional) - Report format

**Example**:
```python
write_report(
    query="AI regulation in the EU",
    research_data="...",
    report_type="research_report"
)
```

#### 4. `get_research_sources`
Retrieve sources used in research.

#### 5. `get_research_context`
Get full context of research.

---

### ⚖️ Court Listener Tools (3)

#### 6. `search_cases`
Search 10M+ legal cases by keyword, party name, or citation.

**Parameters**:
- `query` (string, required) - Search query
- `court` (string, optional) - Court ID filter (e.g., `scotus`, `ca9`)
- `date_from` (string, optional) - Start date (YYYY-MM-DD)
- `date_to` (string, optional) - End date (YYYY-MM-DD)
- `max_results` (int, optional) - Maximum results (default: 10)

**Example**:
```python
search_cases(
    query="Miranda v Arizona",
    court="scotus",
    date_from="2020-01-01",
    max_results=10
)
```

**Response**:
```json
{
  "results": [
    {
      "id": 107252,
      "case_name": "Miranda v. Arizona",
      "citation": "384 U.S. 436",
      "date_filed": "1966-06-13",
      "court": "Supreme Court of the United States",
      "snippet": "...",
      "citation_count": 57669
    }
  ],
  "count": 46909
}
```

#### 7. `get_opinion`
Retrieve full text of a legal opinion.

**Parameters**:
- `opinion_id` (int, required) - Court Listener opinion ID

**Example**:
```python
get_opinion(opinion_id=107252)
```

#### 8. `lookup_citation`
Look up a case by its legal citation.

**Parameters**:
- `citation` (string, required) - Legal citation (e.g., "384 U.S. 436")

**Example**:
```python
lookup_citation(citation="384 U.S. 436")
```

---

### 🤖 Gemini File Search Tools (3)

#### 9. `create_file_store`
Create a document store for RAG (Retrieval-Augmented Generation).

**Parameters**:
- `name` (string, required) - Unique store name
- `display_name` (string, optional) - Human-readable display name

**Example**:
```python
create_file_store(
    name="legal-contracts",
    display_name="Legal Contracts Database"
)
```

**Response**:
```json
{
  "store_name": "legal-contracts",
  "store_id": "corpora/legal-contracts-abc123"
}
```

#### 10. `upload_to_file_store`
Upload a file to a document store for semantic search.

**Parameters**:
- `store_name` (string, required) - Name of the file store
- `file_path` (string, required) - Local path to the file
- `display_name` (string, optional) - Display name for the file

**Example**:
```python
upload_to_file_store(
    store_name="legal-contracts",
    file_path="/path/to/contract.pdf"
)
```

**Response**:
```json
{
  "file_id": "files/abc123xyz",
  "status": "uploaded"
}
```

#### 11. `file_search_query`
Query documents in a file store using semantic search.

**Parameters**:
- `store_name` (string, required) - Name of the file store
- `query` (string, required) - Search query
- `model` (string, optional) - Gemini model to use (default: `gemini-2.5-flash`)

**Example**:
```python
file_search_query(
    store_name="legal-contracts",
    query="What are the termination clauses?"
)
```

**Response**:
```json
{
  "results": [
    {
      "content": "Section 12: Termination...",
      "relevance_score": 0.95
    }
  ],
  "answer": "The termination clauses are found in Section 12..."
}
```

---

## 📖 Usage Examples

### Example 1: Legal Case Research

```
User: Find recent Supreme Court cases about qualified immunity

AI Agent: [Uses search_cases tool]
- Query: "qualified immunity"
- Court: "scotus"
- Date from: "2020-01-01"

Results: Found 127 cases including:
1. Taylor v. Riojas (2020) - Qualified immunity denied
2. Brownback v. King (2021) - Qualified immunity analysis
...
```

### Example 2: Deep Legal Research

```
User: Research the legal implications of AI-generated content ownership

AI Agent: [Uses deep_research tool]
- Conducts comprehensive research across legal databases
- Analyzes copyright law, case precedents, and expert opinions
- Generates detailed report with citations

Report includes:
- Current legal framework
- Key court decisions
- Expert analysis
- Recommendations
```

### Example 3: Document Analysis

```
User: Analyze this contract for non-compete clauses

AI Agent:
1. [Uses create_file_store] - Creates "contract-analysis" store
2. [Uses upload_to_file_store] - Uploads contract.pdf
3. [Uses file_search_query] - Queries for "non-compete clauses"

Results: Found 3 non-compete clauses in Sections 8, 15, and 22...
```

---

## 🐳 Docker Deployment

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  legal-hub:
    build: .
    container_name: legal-hub
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

Deploy:

```bash
docker-compose up -d
```

### Production Considerations

1. **Port Configuration**: Change host port if 8000 is in use
2. **Resource Limits**: Add memory/CPU limits in docker-compose.yml
3. **Logging**: Configure log rotation and retention
4. **Security**: Use reverse proxy (nginx/traefik) with SSL
5. **Monitoring**: Set up health check monitoring
6. **Backups**: Backup .env file and configuration

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

---

## 🔧 Troubleshooting

### Container Won't Start

**Check logs**:
```bash
docker logs legal-hub
```

**Common issues**:
- Missing API keys in `.env`
- Port 8000 already in use
- Insufficient memory

**Solution**:
```bash
# Check if port is in use
lsof -i :8000

# Remove and recreate
docker rm -f legal-hub
docker run -d --name legal-hub -p 8000:8000 --env-file .env legal-hub:latest
```

### Health Check Failing

```bash
# Check if server is responding
curl -v http://localhost:8000/health

# Restart container
docker restart legal-hub
```

### Tools Not Working

**Verify API keys**:
```bash
# Check environment variables inside container
docker exec legal-hub env | grep API_KEY
```

### Performance Issues

**Check resource usage**:
```bash
docker stats legal-hub
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Legal Intelligence Hub                    │
│                      (MCP Server)                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ GPT Research │  │ Court Listen │  │ Gemini File  │      │
│  │   (5 tools)  │  │   (3 tools)  │  │Search (3 tools)│    │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FastMCP Framework                       │    │
│  │         (HTTP/SSE Transport Layer)                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ MCP Protocol
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Augment │         │  Gemini │        │  Claude │
   │   AI    │         │   AI    │        │ Desktop │
   └─────────┘         └─────────┘        └─────────┘
```

---

## 🚀 Development

### Local Development (Without Docker)

```bash
# 1. Clone repository
git clone https://github.com/ianbrucey/legal-hub.git
cd legal-hub

# 2. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 5. Run server
python server.py
```

### Running Tests

```bash
# Test MCP server
python tests/test_mcp_server.py

# Test Court Listener integration
python test_court_listener.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📚 Resources

- **[Deployment Guide](DEPLOYMENT.md)** - Comprehensive deployment documentation
- **[GPT Researcher Docs](https://docs.gptr.dev/)** - GPT Researcher documentation
- **[Court Listener API](https://www.courtlistener.com/help/api/)** - Court Listener API documentation
- **[Gemini API](https://ai.google.dev/)** - Google Gemini API documentation
- **[MCP Protocol](https://docs.anthropic.com/claude/docs/model-context-protocol)** - Model Context Protocol specification

---

## 🏗️ Built With

- **[GPT Researcher](https://github.com/assafelovic/gpt-researcher)** - Deep web research framework
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python MCP server framework
- **[Court Listener](https://www.courtlistener.com/)** - Legal case database
- **[Google Gemini](https://ai.google.dev/)** - AI and document analysis
- **[Docker](https://www.docker.com/)** - Containerization platform

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues**: [https://github.com/ianbrucey/legal-hub/issues](https://github.com/ianbrucey/legal-hub/issues)
- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🙏 Acknowledgments

- Built on top of [GPT Researcher](https://github.com/assafelovic/gpt-researcher) by Assaf Elovic
- Court Listener data provided by [Free Law Project](https://free.law/)
- Powered by Google's Gemini AI

---

<p align="center">
  <strong>Legal Intelligence Hub</strong> - Empowering AI agents with legal research capabilities
</p>

<p align="right">
  <a href="#top">⬆️ Back to Top</a>
</p>
