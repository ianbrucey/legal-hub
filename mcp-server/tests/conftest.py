"""
Pytest configuration.

Ensures tests use the pip-installed gpt-researcher package 
rather than the local gpt_researcher folder.
"""
import sys
from pathlib import Path

# Remove any parent paths that would shadow the pip-installed package
mcp_server_path = Path(__file__).parent.parent
gpt_researcher_path = mcp_server_path.parent

# Filter out the gpt-researcher parent directory from sys.path
# This ensures the pip-installed gpt-researcher is used
sys.path = [p for p in sys.path if not str(p).startswith(str(gpt_researcher_path)) or str(p).startswith(str(mcp_server_path))]

# Add mcp-server to path for local imports
if str(mcp_server_path) not in sys.path:
    sys.path.insert(0, str(mcp_server_path))

