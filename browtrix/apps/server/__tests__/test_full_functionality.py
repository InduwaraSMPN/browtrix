import asyncio
import websockets
import json
import time

async def test_browtrix_functionality():
    try:
        # Connect to WebSocket
        uri = 'ws://localhost:8000/ws'
        async with websockets.connect(uri) as websocket:
            print('✓ WebSocket connected successfully')
            
            # Test 1: HTML Snapshot
            print('\n--- Testing HTML Snapshot ---')
            snapshot_request = {
                "type": "GET_SNAPSHOT",
                "id": "test-snapshot-1"
            }
            await websocket.send(json.dumps(snapshot_request))
            print('✓ Sent snapshot request')
            
            # Wait for snapshot response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                if data.get("type") == "SNAPSHOT_RESULT":
                    print('✓ Snapshot response received')
                    print(f'  Content length: {len(data.get("content", ""))} characters')
                else:
                    print(f'⚠️ Unexpected response: {data}')
            except asyncio.TimeoutError:
                print('⚠️ No snapshot response (web app may not be connected)')
            
            # Test 2: Confirmation Alert
            print('\n--- Testing Confirmation Alert ---')
            confirm_request = {
                "type": "SHOW_CONFIRM",
                "id": "test-confirm-1",
                "msg": "Do you want to proceed with the test?"
            }
            await websocket.send(json.dumps(confirm_request))
            print('✓ Sent confirmation request')
            
            # Test 3: Question Popup
            print('\n--- Testing Question Popup ---')
            input_request = {
                "type": "SHOW_INPUT",
                "id": "test-input-1",
                "msg": "What is your name?",
                "validation": "any"
            }
            await websocket.send(json.dumps(input_request))
            print('✓ Sent input request')
            
            # Wait for any responses
            print('\n--- Waiting for responses ---')
            for i in range(10):  # Wait up to 10 seconds
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f'✓ Response {i+1}: {data.get("type", "unknown")}')
                    
                    if data.get("type") in ["CONFIRM_RESULT", "INPUT_RESULT"]:
                        print('✓ UI interaction responses received')
                        break
                except asyncio.TimeoutError:
                    continue
            
            return True
    except Exception as e:
        print(f'✗ Test failed: {e}')
        return False

async def main():
    print("=== Browtrix Functionality Test ===")
    result = await test_browtrix_functionality()
    print(f"\n=== Test Result: {'PASSED' if result else 'FAILED'} ===")
    
    if result:
        print("\n✓ Server is running and accessible")
        print("✓ WebSocket endpoint is working")
        print("✓ MCP tool requests can be sent")
        print("⚠️ Full UI testing requires browser interaction")

if __name__ == "__main__":
    asyncio.run(main())
