"""
GPT Researcher MCP Server

This script implements an MCP server for GPT Researcher, allowing AI assistants
to conduct web research and generate reports via the MCP protocol.
"""

import os
import sys
import uuid
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from gpt_researcher import GPTResearcher

# Load environment variables
load_dotenv()

from utils import (
    research_store,
    create_success_response, 
    handle_exception,
    get_researcher_by_id, 
    format_sources_for_response,
    format_context_with_sources, 
    store_research_results,
    create_research_prompt
)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s] - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="GPT Researcher"
)

# Initialize researchers dictionary
if not hasattr(mcp, "researchers"):
    mcp.researchers = {}


@mcp.resource("research://{topic}")
async def research_resource(topic: str) -> str:
    """
    Provide research context for a given topic directly as a resource.
    
    This allows LLMs to access web-sourced information without explicit function calls.
    
    Args:
        topic: The research topic or query
        
    Returns:
        String containing the research context with source information
    """
    # Check if we've already researched this topic
    if topic in research_store:
        logger.info(f"Returning cached research for topic: {topic}")
        return research_store[topic]["context"]
    
    # If not, conduct the research
    logger.info(f"Conducting new research for resource on topic: {topic}")
    
    # Initialize GPT Researcher
    researcher = GPTResearcher(topic)
    
    try:
        # Conduct the research
        await researcher.conduct_research()
        
        # Get the context and sources
        context = researcher.get_research_context()
        sources = researcher.get_research_sources()
        source_urls = researcher.get_source_urls()
        
        # Format with sources included
        formatted_context = format_context_with_sources(topic, context, sources)
        
        # Store for future use
        store_research_results(topic, context, sources, source_urls, formatted_context)
        
        return formatted_context
    except Exception as e:
        return f"Error conducting research on '{topic}': {str(e)}"


@mcp.tool()
async def deep_research(query: str) -> Dict[str, Any]:
    """
    Conduct a web deep research on a given query using GPT Researcher. 
    Use this tool when you need time-sensitive, real-time information like stock prices, news, people, specific knowledge, etc.
    
    Args:
        query: The research query or topic
        
    Returns:
        Dict containing research status, ID, and the actual research context and sources
        that can be used directly by LLMs for context enrichment
    """
    logger.info(f"Conducting research on query: {query}...")
    
    # Generate a unique ID for this research session
    research_id = str(uuid.uuid4())
    
    # Initialize GPT Researcher
    researcher = GPTResearcher(query)
    
    # Start research
    try:
        await researcher.conduct_research()
        mcp.researchers[research_id] = researcher
        logger.info(f"Research completed for ID: {research_id}")
        
        # Get the research context and sources
        context = researcher.get_research_context()
        sources = researcher.get_research_sources()
        source_urls = researcher.get_source_urls()
        
        # Store in the research store for the resource API
        store_research_results(query, context, sources, source_urls)
        
        return create_success_response({
            "research_id": research_id,
            "query": query,
            "source_count": len(sources),
            "context": context,
            "sources": format_sources_for_response(sources),
            "source_urls": source_urls
        })
    except Exception as e:
        return handle_exception(e, "Research")


@mcp.tool()
async def quick_search(query: str) -> Dict[str, Any]:
    """
    Perform a quick web search on a given query and return search results with snippets.
    This optimizes for speed over quality and is useful when an LLM doesn't need in-depth
    information on a topic.
    
    Args:
        query: The search query
        
    Returns:
        Dict containing search results and snippets
    """
    logger.info(f"Performing quick search on query: {query}...")
    
    # Generate a unique ID for this search session
    search_id = str(uuid.uuid4())
    
    # Initialize GPT Researcher
    researcher = GPTResearcher(query)
    
    try:
        # Perform quick search
        search_results = await researcher.quick_search(query=query)
        mcp.researchers[search_id] = researcher
        logger.info(f"Quick search completed for ID: {search_id}")
        
        return create_success_response({
            "search_id": search_id,
            "query": query,
            "result_count": len(search_results) if search_results else 0,
            "search_results": search_results
        })
    except Exception as e:
        return handle_exception(e, "Quick search")


@mcp.tool()
async def write_report(research_id: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a report based on previously conducted research.
    
    Args:
        research_id: The ID of the research session from deep_research
        custom_prompt: Optional custom prompt for report generation
        
    Returns:
        Dict containing the report content and metadata
    """
    success, researcher, error = get_researcher_by_id(mcp.researchers, research_id)
    if not success:
        return error
    
    logger.info(f"Generating report for research ID: {research_id}")
    
    try:
        # Generate report
        report = await researcher.write_report(custom_prompt=custom_prompt)
        
        # Get additional information
        sources = researcher.get_research_sources()
        costs = researcher.get_costs()
        
        return create_success_response({
            "report": report,
            "source_count": len(sources),
            "costs": costs
        })
    except Exception as e:
        return handle_exception(e, "Report generation")


@mcp.tool()
async def get_research_sources(research_id: str) -> Dict[str, Any]:
    """
    Get the sources used in the research.
    
    Args:
        research_id: The ID of the research session
        
    Returns:
        Dict containing the research sources
    """
    success, researcher, error = get_researcher_by_id(mcp.researchers, research_id)
    if not success:
        return error
    
    sources = researcher.get_research_sources()
    source_urls = researcher.get_source_urls()
    
    return create_success_response({
        "sources": format_sources_for_response(sources),
        "source_urls": source_urls
    })


@mcp.tool()
async def get_research_context(research_id: str) -> Dict[str, Any]:
    """
    Get the full context of the research.
    
    Args:
        research_id: The ID of the research session
        
    Returns:
        Dict containing the research context
    """
    success, researcher, error = get_researcher_by_id(mcp.researchers, research_id)
    if not success:
        return error
    
    context = researcher.get_research_context()
    
    return create_success_response({
        "context": context
    })


@mcp.prompt()
def research_query(topic: str, goal: str, report_format: str = "research_report") -> str:
    """
    Create a research query prompt for GPT Researcher.

    Args:
        topic: The topic to research
        goal: The goal or specific question to answer
        report_format: The format of the report to generate

    Returns:
        A formatted prompt for research
    """
    return create_research_prompt(topic, goal, report_format)


# ============================================================================
# Court Listener Tools
# ============================================================================
import httpx


class CourtListenerClient:
    """Lightweight Court Listener client."""

    def __init__(self):
        self.base_url = os.getenv("COURTLISTENER_BASE_URL", "https://www.courtlistener.com/api/rest/v3")
        self.token = os.getenv("COURTLISTENER_API_KEY", "")
        self.timeout = 30.0
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
        "type": "o",
        "q": query,
        "page_size": max_results,
    }
    if court:
        params["court"] = court
    if date_from:
        params["filed_after"] = date_from
    if date_to:
        params["filed_before"] = date_to

    result = await client.get("/search/", params)
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


# ============================================================================
# Gemini File Search Tools
# ============================================================================
from clients import GeminiFileSearch


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
    return result.model_dump()


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
    result = await fs.upload(store_name=store_name, file_path=file_path)
    return result.model_dump()


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
        Dictionary with 'answer' and 'citations'
    """
    fs = GeminiFileSearch()
    result = await fs.query(
        store_name=store_name,
        query=query,
    )
    return result.model_dump()


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})

def run_server():
    """Run the MCP server using FastMCP's built-in event loop handling."""
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    # Determine transport based on environment
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    
    # Auto-detect Docker environment
    if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
        transport = "sse"
        logger.info("Docker environment detected, using SSE transport")
    
    # Add startup message
    logger.info(f"Starting GPT Researcher MCP Server with {transport} transport...")
    print(f"🚀 GPT Researcher MCP Server starting with {transport} transport...")
    print("   Check researcher_mcp_server.log for details")

    # Let FastMCP handle the event loop
    try:
        if transport == "stdio":
            logger.info("Using STDIO transport (Claude Desktop compatible)")
            mcp.run(transport="stdio")
        elif transport == "sse":
            mcp.run(transport="sse", host="0.0.0.0", port=8000)
        elif transport == "streamable-http":
            mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
        else:
            raise ValueError(f"Unsupported transport: {transport}")
            
        # Note: If we reach here, the server has stopped
        logger.info("MCP Server is running...")
        while True:
            pass  # Keep the process alive
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
        print(f"❌ MCP Server error: {str(e)}")
        return
        
    print("✅ MCP Server stopped")


if __name__ == "__main__":
    # Use the non-async approach to avoid asyncio nesting issues
    run_server()
