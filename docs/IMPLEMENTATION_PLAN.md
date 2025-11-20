# Browtrix Implementation Plan

## 1. Overview
Browtrix acts as a bridge between an MCP Client (e.g., Claude Desktop, Cursor) and a web browser.
- **Backend (Python/FastMCP)**: Exposes MCP tools. Manages WebSocket connections to the browser.
- **Frontend (Next.js)**: Connects to Backend via WebSocket. Executes commands (Alerts, Inputs, Snapshots) and returns results.

## 2. Architecture
`MCP Client` -> `FastMCP Server` <-> `WebSocket` <-> `Next.js Client`

### Key Components
1.  **Connection Manager (Server)**: Handles active WS connections and maps async MCP tool calls to WS messages using Request IDs and Futures.
2.  **WebSocket Provider (Client)**: Maintains persistent connection, handles reconnection, and routes messages.
3.  **Browtrix Overlay (Client)**: A React component responsible for rendering the interactive UI (Alerts, Popups) and handling logic (Snapshots).

---

## 3. Implementation Steps

### Phase 1: Backend Foundation (Python)

#### 1.1 Dependencies
Update `browtrix/apps/server/pyproject.toml` to include:
- `fastapi`
- `uvicorn[standard]`
- `websockets`
- `pydantic-settings`

#### 1.2 Directory Structure
Adopt the `fastmcp` example structure:
```
browtrix/apps/server/
├── src/
│   └── browtrix_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── connection_manager.py
│       ├── server.py
│       └── settings.py
├── fastmcp.json
└── pyproject.toml
```

#### 1.3 Connection Manager (`src/browtrix_server/connection_manager.py`)
Create a class `ConnectionManager` that:
- Stores active `WebSocket` connections.
- Stores pending requests (`dict[str, asyncio.Future]`).
- `connect(websocket)`: Accept and store connection.
- `disconnect(websocket)`: Remove connection.
- `send_request(method, params)`:
    - Generate `request_id`.
    - Create a `Future`.
    - Send JSON `{id, type, ...params}` to client.
    - Return the `Future`.
- `handle_message(data)`:
    - Parse incoming JSON.
    - If it's a result (`CONFIRM_RESULT`, etc.), resolve the corresponding `Future`.

#### 1.4 Settings (`src/browtrix_server/settings.py`)
Implement configuration using `pydantic-settings`:
- Host, Port, Log Level.

#### 1.5 Server Logic (`src/browtrix_server/server.py`)
Refactor to use `FastAPI` as the main wrapper to support WebSockets alongside FastMCP.
- Initialize `FastAPI` app.
- Initialize `FastMCP` server.
- Mount `FastMCP` app to FastAPI using `mcp.http_app(transport="sse")` for compatibility.
- Add `@app.websocket("/ws")` endpoint that uses `ConnectionManager`.
- Implement MCP Tools:
    - `html-snapshot()`: Calls `manager.send_request("GET_SNAPSHOT")`.
    - `confirmation-alert(message)`: Calls `manager.send_request("SHOW_CONFIRM", {msg})`.
    - `question-popup(question)`: Calls `manager.send_request("SHOW_INPUT", {question})`.

#### 1.6 Entry Point (`src/browtrix_server/__main__.py`)
- Use `uvicorn` to run the app based on settings.

### Phase 2: Frontend Foundation (Next.js)

#### 2.1 Dependencies
Install required packages in `browtrix/apps/web`:
- `turndown` (for HTML -> Markdown).
- `@types/turndown`.

#### 2.2 WebSocket Context (`browtrix/apps/web/src/lib/browtrix-context.tsx`)
Create a Context/Provider that:
- Connects to `ws://localhost:8000/ws` on mount.
- Handles connection status (Open/Closed/Error).
- Exposes `sendMessage` and `lastMessage`.

#### 2.3 Snapshot Logic (`browtrix/apps/web/src/lib/snapshot.ts`)
Implement `captureSnapshot()`:
- Use `TurndownService` to convert `document.body` to Markdown.
- Cleanup (remove scripts, styles) before conversion if needed.

### Phase 3: Frontend Feature Implementation

#### 3.1 Browtrix Overlay Component (`browtrix/apps/web/src/components/browtrix-overlay.tsx`)
This component will live in the root layout or page.
- **Hooks**: Listen to WebSocket messages.
- **State**:
    - `confirmation`: `{ show: boolean, message: string, id: string }`
    - `input`: `{ show: boolean, question: string, id: string }`
- **Handlers**:
    - On `GET_SNAPSHOT`: Run `captureSnapshot()`, send `SNAPSHOT_RESULT`.
    - On `SHOW_CONFIRM`: Set `confirmation` state.
    - On `SHOW_INPUT`: Set `input` state.
- **Render**:
    - `<AlertDialog>` for Confirmation.
    - `<Dialog>` with `<Input>` for Question.

#### 3.2 Integrate into App
- Add `<BrowtrixProvider>` and `<BrowtrixOverlay>` to `browtrix/apps/web/src/app/layout.tsx` (or `providers.tsx`).

### Phase 4: Integration & Verification

#### 4.1 Development Workflow
1. Start Server: `cd browtrix/apps/server && uv run browtrix-server`.
2. Start Web: `cd browtrix/apps/web && bun dev`.
3. Open Browser: `http://localhost:3001`.

#### 4.2 Testing
- **WebSocket**: Use `wscat` to verify the connection:
    ```bash
    wscat -c ws://localhost:8000/ws
    ```
- **Snapshot**: Use MCP Client to call `html-snapshot`. Verify Markdown is returned.
- **Alert**: Call `confirmation-alert`. Verify Modal appears. Click Confirm. Verify "True" returned.
- **Input**: Call `question-popup`. Verify Input appears. Type text. Verify text returned.

## 4. Detailed File Changes

### `apps/server/src/browtrix_server/connection_manager.py`
- Class `ConnectionManager` with `active_connections: List[WebSocket]` and `pending_futures: Dict[str, Future]`.

### `apps/server/src/browtrix_server/server.py`
- Import `FastAPI`, `WebSocket`.
- Create `app = FastAPI()`.
- Define `@mcp.tool` functions that await `manager.request(...)`.
- Mount `mcp.http_app(transport="sse")` to FastAPI.

### `apps/web/src/components/browtrix-overlay.tsx`
- Uses `shadcn/ui` components (`Dialog`, `AlertDialog`, `Button`, `Input`).
- Handles the "Event Loop" of the browser side.

## 5. Future Considerations
- Security: Add authentication to WS connection.
- Multiple Clients: Handle targeting specific browser sessions if scaling.
