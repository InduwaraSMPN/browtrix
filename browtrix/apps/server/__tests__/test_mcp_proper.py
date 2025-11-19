import asyncio
import aiohttp
import json

async def test_mcp_proper_flow():
    """Test MCP with proper initialization sequence"""
    print("=== Proper MCP Flow Test ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Open SSE connection
            print("\n1. Opening SSE connection...")
            sse_response = await session.get('http://localhost:8000/sse')
            
            session_endpoint = None
            async for line in sse_response.content:
                line = line.decode().strip()
                if line.startswith('data: '):
                    session_endpoint = f'http://localhost:8000{line[6:]}'
                    break
            
            print(f"✓ Session endpoint: {session_endpoint}")
            
            # Step 2: Initialize MCP session
            print("\n2. Initializing MCP session...")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            init_response = await session.post(session_endpoint, json=init_request)
            print(f"Init response status: {init_response.status}")
            
            # Step 3: Read initialization response
            async for line in sse_response.content:
                line = line.decode().strip()
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        print(f"✓ Init response: {data}")
                        break
                    except:
                        continue
            
            # Step 4: Now list tools
            print("\n3. Listing tools...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            tools_response = await session.post(session_endpoint, json=tools_request)
            print(f"Tools response status: {tools_response.status}")
            
            # Step 5: Read tools response
            async for line in sse_response.content:
                line = line.decode().strip()
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'result' in data and 'tools' in data['result']:
                            print(f"✓ Tools available: {len(data['result']['tools'])}")
                            for tool in data['result']['tools']:
                                print(f"  - {tool['name']}: {tool['description']}")
                            return True
                    except:
                        continue
            
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

async def main():
    result = await test_mcp_proper_flow()
    print(f"\n=== MCP Flow Result: {'PASSED' if result else 'FAILED'} ===")

if __name__ == "__main__":
    asyncio.run(main())
