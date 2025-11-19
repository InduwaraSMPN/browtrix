import asyncio
import aiohttp
import websockets
import json
import time

async def test_complete_system():
    """Test the complete Browtrix system"""
    results = []
    
    # Test 1: Server Health
    print('=== Test 1: Server Health ===')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/sse') as response:
                if response.status == 200:
                    print('✓ Server is running')
                    results.append(True)
                else:
                    print(f'✗ Server returned status {response.status}')
                    results.append(False)
    except Exception as e:
        print(f'✗ Server health check failed: {e}')
        results.append(False)
    
    # Test 2: WebSocket Connection
    print('\n=== Test 2: WebSocket Connection ===')
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            print('✓ WebSocket connection established')
            results.append(True)
    except Exception as e:
        print(f'✗ WebSocket connection failed: {e}')
        results.append(False)
    
    # Test 3: MCP Interface
    print('\n=== Test 3: MCP Interface ===')
    try:
        async with aiohttp.ClientSession() as session:
            # Get session
            async with session.get('http://localhost:8000/sse') as response:
                session_endpoint = None
                async for line in response.content:
                    line = line.decode().strip()
                    if line.startswith('data: '):
                        session_endpoint = f'http://localhost:8000{line[6:]}'
                        break
            
            if session_endpoint:
                # Test tools/list
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
                
                async with session.post(session_endpoint, json=tools_request) as response:
                    if response.status == 202:
                        print('✓ MCP tools/list accepted')
                        results.append(True)
                    else:
                        print(f'✗ MCP tools/list failed: {response.status}')
                        results.append(False)
            else:
                print('✗ Could not get MCP session')
                results.append(False)
                
    except Exception as e:
        print(f'✗ MCP interface test failed: {e}')
        results.append(False)
    
    # Test 4: Web App
    print('\n=== Test 4: Web App ===')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3001') as response:
                if response.status == 200:
                    content = await response.text()
                    if 'frontend' in content:
                        print('✓ Web app is running')
                        results.append(True)
                    else:
                        print('✗ Web app response unexpected')
                        results.append(False)
                else:
                    print(f'✗ Web app returned status {response.status}')
                    results.append(False)
    except Exception as e:
        print(f'✗ Web app test failed: {e}')
        results.append(False)
    
    return all(results), results

async def main():
    print("=== Complete Browtrix System Test ===")
    start_time = time.time()
    
    success, individual_results = await test_complete_system()
    
    elapsed = time.time() - start_time
    print(f"\n=== Test Results ===")
    print(f"Overall: {'PASSED' if success else 'FAILED'}")
    print(f"Individual tests: {individual_results}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    
    if success:
        print("\n✅ All core components are working!")
        print("📝 Next steps:")
        print("   1. Open http://localhost:3001 in a browser")
        print("   2. Check browser console for WebSocket connection")
        print("   3. Test MCP tools through an MCP client")
        print("   4. Verify UI interactions (alerts, inputs)")
    else:
        print("\n❌ Some components are not working correctly")
        print("🔧 Check the server logs for detailed error information")

if __name__ == "__main__":
    asyncio.run(main())
