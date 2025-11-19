from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastmcp import FastMCP
from .connection_manager import ConnectionManager
import asyncio

# Initialize Connection Manager
manager = ConnectionManager()

# Initialize MCP Server
mcp = FastMCP("browtrix")


@mcp.tool()
async def browtrix_html_snapshot() -> str:
    """Take a HTML snapshot of the current page."""
    result = await manager.send_request("GET_SNAPSHOT")
    return result.get("content", "")


@mcp.tool()
async def browtrix_confirmation_alert(message: str) -> bool:
    """Show a confirmation alert (Yes/No) on the user's page."""
    result = await manager.send_request("SHOW_CONFIRM", {"msg": message})
    return result.get("approved", False)


@mcp.tool()
async def browtrix_question_popup(question: str) -> str:
    """Show a question popup and get the user's answer."""
    # Defaulting validation to 'any' for generic questions, can be improved
    result = await manager.send_request(
        "SHOW_INPUT", {"msg": question, "validation": "any"}
    )
    return result.get("value", "")


# Initialize FastAPI App
app = FastAPI()


# Add WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket)


# Mount MCP App
try:
    # Use SSE transport for standard MCP compatibility
    # Using 'sse' transport creates endpoints for /sse and /messages
    mcp_app = mcp.http_app(transport="sse")
    app.mount("/", mcp_app)
except Exception as e:
    print(f"Failed to mount MCP app: {e}")
