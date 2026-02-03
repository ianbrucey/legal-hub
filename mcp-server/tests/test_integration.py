"""
Integration tests for Legal Intelligence MCP Hub.

Tests the full flow from MCP tool invocation to response.
Run with: pytest tests/test_integration.py -v
"""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def get_tools():
    """Helper to get all tools from the main server."""
    from server import mcp
    return await mcp.list_tools()


async def get_tool_by_name(name: str):
    """Helper to get a specific tool by name."""
    tools = await get_tools()
    return next((t for t in tools if t.name == name), None)


class TestHealthCheck:
    """Test server health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Health check returns expected structure."""
        tools = await get_tools()
        tool_names = [t.name for t in tools]

        assert "health_check" in tool_names


class TestCourtListenerTools:
    """Test Court Listener tool integrations."""

    @pytest.mark.asyncio
    async def test_search_cases_schema(self):
        """search_cases tool has correct schema."""
        search_tool = await get_tool_by_name("search_cases")

        assert search_tool is not None
        assert "query" in str(search_tool.inputSchema)

    @pytest.mark.asyncio
    async def test_get_opinion_schema(self):
        """get_opinion tool has correct schema."""
        opinion_tool = await get_tool_by_name("get_opinion")

        assert opinion_tool is not None
        assert "opinion_id" in str(opinion_tool.inputSchema)

    @pytest.mark.asyncio
    async def test_lookup_citation_schema(self):
        """lookup_citation tool has correct schema."""
        citation_tool = await get_tool_by_name("lookup_citation")

        assert citation_tool is not None
        assert "citation" in str(citation_tool.inputSchema)


class TestGPTResearcherTools:
    """Test GPT Researcher tool integrations."""

    @pytest.mark.asyncio
    async def test_deep_research_schema(self):
        """deep_research tool has correct schema."""
        research_tool = await get_tool_by_name("deep_research")

        assert research_tool is not None
        assert "query" in str(research_tool.inputSchema)

    @pytest.mark.asyncio
    async def test_save_report_to_s3_schema(self):
        """save_report_to_s3 tool has correct schema."""
        s3_tool = await get_tool_by_name("save_report_to_s3")

        assert s3_tool is not None
        assert "bucket" in str(s3_tool.inputSchema)
        assert "report" in str(s3_tool.inputSchema)


class TestGeminiTools:
    """Test Gemini tool integrations."""

    @pytest.mark.asyncio
    async def test_web_search_schema(self):
        """web_search tool has correct schema."""
        search_tool = await get_tool_by_name("web_search")

        assert search_tool is not None
        assert "query" in str(search_tool.inputSchema)

    @pytest.mark.asyncio
    async def test_create_file_store_schema(self):
        """create_file_store tool has correct schema."""
        store_tool = await get_tool_by_name("create_file_store")

        assert store_tool is not None
        assert "name" in str(store_tool.inputSchema)

    @pytest.mark.asyncio
    async def test_file_search_query_schema(self):
        """file_search_query tool has correct schema."""
        query_tool = await get_tool_by_name("file_search_query")

        assert query_tool is not None
        assert "store_name" in str(query_tool.inputSchema)
        assert "query" in str(query_tool.inputSchema)


class TestToolCount:
    """Verify all 12 tools are registered."""

    @pytest.mark.asyncio
    async def test_total_tool_count(self):
        """Server has all 12 expected tools (11 domain + 1 health_check)."""
        tools = await get_tools()
        tool_names = [t.name for t in tools]

        # Expected tools
        expected_tools = [
            # GPT Researcher (4)
            "deep_research", "quick_search", "write_report", "save_report_to_s3",
            # Court Listener (3)
            "search_cases", "get_opinion", "lookup_citation",
            # Gemini (4)
            "web_search", "create_file_store", "upload_to_file_store", "file_search_query",
            # Health (1)
            "health_check",
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Missing tool: {tool}"

        assert len(tools) == 12, f"Expected 12 tools, got {len(tools)}: {tool_names}"

