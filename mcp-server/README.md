# ⚖️ Legal Intelligence MCP Hub

A unified Model Context Protocol (MCP) server providing legal research tools for AI assistants.

## Features

**12 Tools across 3 domains:**

### GPT Researcher (4 tools)
| Tool | Description |
|------|-------------|
| `deep_research` | Comprehensive research on any topic |
| `quick_search` | Fast web search |
| `write_report` | Generate formatted reports from research data |
| `save_report_to_s3` | Upload reports to AWS S3 |

### Court Listener (3 tools)
| Tool | Description |
|------|-------------|
| `search_cases` | Search legal cases by keyword, party, or citation |
| `get_opinion` | Retrieve full text of legal opinions |
| `lookup_citation` | Look up cases by legal citation (e.g., "384 U.S. 436") |

### Gemini (4 tools)
| Tool | Description |
|------|-------------|
| `web_search` | Web search with Gemini grounding |
| `create_file_store` | Create document stores for RAG |
| `upload_to_file_store` | Upload documents to stores |
| `file_search_query` | Query documents using RAG |

### Utility (1 tool)
| Tool | Description |
|------|-------------|
| `health_check` | Server health and tool listing |

## Quick Start

```bash
# Install dependencies
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python server.py
```

## Configuration

Create a `.env` file with:

```env
# Server
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=INFO

# Court Listener
COURTLISTENER_API_KEY=your_key_here

# Gemini
GOOGLE_API_KEY=your_key_here

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Usage

### With Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "legal-hub": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py", "--transport", "stdio"]
    }
  }
}
```

### HTTP Transport

```bash
python server.py --transport streamable-http --port 8000
```

Connect at: `http://localhost:8000/mcp/`

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Project Structure

```
mcp-server/
├── server.py           # Main MCP server with all 12 tools
├── config.py           # Pydantic configuration
├── clients/            # API clients
│   ├── s3_client.py    # AWS S3 client
│   └── gemini_client.py # Gemini API clients
├── tests/
│   └── test_integration.py
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.11+
- MCP SDK 1.23+
- gpt-researcher 0.14+
- httpx, pydantic, boto3

## License

MIT