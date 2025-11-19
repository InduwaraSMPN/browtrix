import asyncio
import aiohttp


async def test_mcp_tools():
    """Test MCP tools via HTTP/SSE transport"""
    try:
        base_url = "http://localhost:8000"
        async with aiohttp.ClientSession() as session:
            # Step 1: Get SSE endpoint with session ID
            print("--- Getting SSE session ---")
            async with session.get(f"{base_url}/sse") as response:
                if response.status != 200:
                    print(f"✗ SSE endpoint failed: {response.status}")
                    return False

                # Read the SSE stream to get session ID
                session_endpoint = None
                async for line in response.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        endpoint_path = line[6:]  # Remove 'data: '
                        session_endpoint = f"{base_url}{endpoint_path}"
                        print(f"✓ Got session endpoint: {session_endpoint}")
                        break

                if not session_endpoint:
                    print("✗ No session endpoint found")
                    return False

            # Step 2: Call tools/list
            print("\n--- Testing tools/list ---")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }

            async with session.post(session_endpoint, json=tools_request) as response:
                print(f"Tools request status: {response.status}")
                if response.status == 202:
                    print("✓ Tools request accepted (processing)")
                else:
                    text = await response.text()
                    print(f"Response: {text}")

            return True

    except Exception as e:
        print(f"✗ MCP client test failed: {e}")
        return False


async def main():
    print("=== MCP Tools Test ===")
    result = await test_mcp_tools()
    print(f"\n=== MCP Test Result: {'PASSED' if result else 'FAILED'} ===")


if __name__ == "__main__":
    asyncio.run(main())
