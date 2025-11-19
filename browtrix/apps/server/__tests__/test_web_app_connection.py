import asyncio
import websockets
import json


async def simulate_web_app():
    """Simulate the web app's WebSocket connection and behavior"""
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✓ Web app simulation connected")

            # Listen for messages from server (MCP tool calls)
            message_count = 0
            while message_count < 5:  # Listen for a few messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    message_count += 1
                    print(
                        f"✓ Received message {message_count}: {data.get('type', 'unknown')}"
                    )

                    # Simulate web app responses
                    msg_type = data.get("type")
                    msg_id = data.get("id")

                    if msg_type == "GET_SNAPSHOT":
                        # Simulate snapshot response
                        response = {
                            "type": "SNAPSHOT_RESULT",
                            "id": msg_id,
                            "content": "<html><body>Test snapshot content</body></html>",
                        }
                        await websocket.send(json.dumps(response))
                        print("✓ Sent snapshot response")

                    elif msg_type == "SHOW_CONFIRM":
                        # Simulate user clicking "Yes"
                        response = {
                            "type": "CONFIRM_RESULT",
                            "id": msg_id,
                            "approved": True,
                        }
                        await websocket.send(json.dumps(response))
                        print("✓ Sent confirmation response (approved)")

                    elif msg_type == "SHOW_INPUT":
                        # Simulate user input
                        response = {
                            "type": "INPUT_RESULT",
                            "id": msg_id,
                            "value": "Test user input",
                        }
                        await websocket.send(json.dumps(response))
                        print("✓ Sent input response")

                except asyncio.TimeoutError:
                    print("⚠️ No more messages, ending simulation")
                    break

            return True

    except Exception as e:
        print(f"✗ Web app simulation failed: {e}")
        return False


async def main():
    print("=== Web App Connection Simulation ===")
    print("This simulates what the React web app should do")
    result = await simulate_web_app()
    print(f"\n=== Simulation Result: {'PASSED' if result else 'FAILED'} ===")


if __name__ == "__main__":
    asyncio.run(main())
