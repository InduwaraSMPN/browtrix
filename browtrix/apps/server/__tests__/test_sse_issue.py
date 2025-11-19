import asyncio
import aiohttp
import json

async def test_sse_flow():
    """Reproduce the SSE transport issue"""
    print("=== SSE Transport Issue Reproduction ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Open SSE connection and keep it alive
            print("\n1. Opening SSE connection...")
            sse_response = await session.get('http://localhost:8000/sse')
            
            if sse_response.status != 200:
                print(f"✗ SSE connection failed: {sse_response.status}")
                return False
            
            print("✓ SSE connection opened")
            
            # Step 2: Read the session endpoint from SSE
            session_endpoint = None
            async for line in sse_response.content:
                line = line.decode().strip()
                print(f"SSE line: {line}")
                if line.startswith('data: '):
                    session_endpoint = f'http://localhost:8000{line[6:]}'
                    print(f"✓ Session endpoint: {session_endpoint}")
                    break
            
            if not session_endpoint:
                print("✗ No session endpoint received")
                return False
            
            # Step 3: Send a message while SSE is still "open"
            print("\n2. Sending MCP request...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            # The issue: SSE connection might be closing before we send this
            msg_response = await session.post(session_endpoint, json=tools_request)
            print(f"Message response status: {msg_response.status}")
            
            if msg_response.status == 202:
                print("✓ Request accepted")
                
                # Step 4: Try to read the response from SSE
                print("\n3. Reading SSE response...")
                try:
                    async for line in sse_response.content:
                        line = line.decode().strip()
                        if line:
                            print(f"SSE response: {line}")
                            # Look for actual MCP response
                            if line.startswith('data: ') and 'jsonrpc' in line:
                                print("✓ Got MCP response via SSE")
                                return True
                except Exception as e:
                    print(f"✗ Error reading SSE response: {e}")
                    return False
            else:
                text = await msg_response.text()
                print(f"✗ Request failed: {text}")
                return False
                
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

async def main():
    result = await test_sse_flow()
    print(f"\n=== SSE Test Result: {'PASSED' if result else 'FAILED'} ===")

if __name__ == "__main__":
    asyncio.run(main())
