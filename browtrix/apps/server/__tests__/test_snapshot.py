#!/usr/bin/env python3
"""
Test script for browtrix HTML snapshot functionality.
"""

import asyncio
import json
import httpx


async def test_snapshot():
    """Test the HTML snapshot functionality."""

    # First, establish SSE connection to get session ID
    print("Connecting to MCP SSE endpoint...")

    try:
        # Create SSE connection
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/mcp/sse", timeout=30)

            # Read initial SSE data to get session ID
            lines = response.text.split("\n")
            session_id = None

            for line in lines:
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if "sessionId" in data:
                            session_id = data["sessionId"]
                            break
                    except:
                        continue

            if not session_id:
                print("Could not get session ID from SSE")
                return

            print(f"Got session ID: {session_id}")

            # Now send tool call request
            tool_request = {
                "type": "tools/call",
                "id": "test-snapshot-1",
                "params": {"name": "browtrix_html_snapshot", "arguments": {}},
            }

            print("Sending tool request...")
            response = await client.post(
                f"http://localhost:8000/mcp/messages/?session_id={session_id}",
                json=tool_request,
                timeout=30,
            )

            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_snapshot())
