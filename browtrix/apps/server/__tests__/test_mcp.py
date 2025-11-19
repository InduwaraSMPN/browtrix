import asyncio
import websockets
import json

async def test_websocket():
    try:
        uri = 'ws://localhost:8000/ws'
        async with websockets.connect(uri) as websocket:
            print('✓ WebSocket connected successfully')
            
            # Send a test message to see if the server responds
            test_message = json.dumps({
                "type": "test",
                "data": "Hello from test client"
            })
            
            await websocket.send(test_message)
            print('✓ Test message sent')
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f'✓ Server response: {response}')
            except asyncio.TimeoutError:
                print('⚠️ No response from server (this may be expected)')
            
            return True
    except Exception as e:
        print(f'✗ WebSocket test failed: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    print(f"WebSocket test result: {'PASSED' if result else 'FAILED'}")
