import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pending_futures: Dict[str, asyncio.Future] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(
                f"Client disconnected. Total connections: {len(self.active_connections)}"
            )

    async def send_request(
        self,
        request_type: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Any:
        if not self.active_connections:
            raise Exception("No browser connected. Please open the web app.")

        # For now, broadcast to the first available connection (or all, but we need a response)
        # Simplification: Use the last connected client (most recent)
        websocket = self.active_connections[-1]

        request_id = f"req_{uuid.uuid4().hex[:8]}"
        future = asyncio.Future()
        self.pending_futures[request_id] = future

        message = {"id": request_id, "type": request_type, **(params or {})}

        try:
            await websocket.send_json(message)
            # Wait for the result
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            del self.pending_futures[request_id]
            raise Exception("Browser did not respond in time.")
        except Exception as e:
            if request_id in self.pending_futures:
                del self.pending_futures[request_id]
            raise e

    async def handle_message(self, data: str):
        try:
            message = json.loads(data)
            msg_type = message.get("type")
            req_id = message.get("id")

            if req_id and req_id in self.pending_futures:
                future = self.pending_futures[req_id]
                if not future.done():
                    if msg_type == "ERROR":
                        future.set_exception(
                            Exception(message.get("msg", "Unknown error"))
                        )
                    else:
                        future.set_result(message)
                del self.pending_futures[req_id]

        except json.JSONDecodeError:
            print("Failed to decode JSON message")
        except Exception as e:
            print(f"Error handling message: {e}")
