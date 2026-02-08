#!/usr/bin/env python3
"""
Test script to verify MCP server stdio communication.
"""
import subprocess
import json
import sys

def test_mcp_stdio():
    """Test MCP server via stdio transport."""
    
    # Start the server
    server_path = "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/server.py"
    python_path = "/Users/ianbruce/Herd/gptr/gpt-researcher/mcp-server/.venv/bin/python"
    
    print("🚀 Starting MCP server...")
    proc = subprocess.Popen(
        [python_path, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        print("📥 Waiting for response...")
        response_line = proc.stdout.readline()
        
        if response_line:
            print(f"✅ Got response: {response_line[:100]}...")
            response = json.loads(response_line)
            print(f"✅ Server initialized successfully!")
            print(f"   Server name: {response.get('result', {}).get('serverInfo', {}).get('name')}")
            return True
        else:
            print("❌ No response from server")
            stderr = proc.stderr.read()
            if stderr:
                print(f"❌ Stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        proc.terminate()
        proc.wait(timeout=2)

if __name__ == "__main__":
    success = test_mcp_stdio()
    sys.exit(0 if success else 1)

