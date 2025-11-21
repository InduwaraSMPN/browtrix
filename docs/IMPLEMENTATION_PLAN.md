# Browtrix Implementation Plan

## 1. Overview
Browtrix acts as a bridge between an MCP Client (e.g., Claude Desktop, Cursor) and a web browser.
- **Backend (Python/FastMCP)**: Exposes MCP tools. Manages WebSocket connections to the browser.
- **Frontend (Next.js)**: Connects to Backend via WebSocket. Executes commands (Alerts, Inputs, Snapshots) and returns results.

## 2. Architecture
`MCP Client` -> `FastMCP Server` <-> `WebSocket` <-> `Next.js Client`

### Key Components
1.  **Connection Manager (Server)**: Handles active WS connections, health monitoring, statistics, and maps async MCP tool calls to WS messages using Request IDs and Futures.
2.  **WebSocket Provider (Client)**: Maintains persistent connection, handles reconnection, and routes messages.
3.  **Browtrix Overlay (Client)**: A React component responsible for rendering the interactive UI (Alerts, Popups) and handling logic (Snapshots).

---

## 3. Implementation Status

### Phase 1: Backend Foundation (Python) - ✅ Completed

#### 1.1 Dependencies
- `fastapi`, `uvicorn[standard]`, `websockets`, `pydantic-settings`, `structlog` installed.

#### 1.2 Directory Structure
Implemented structure:
```
browtrix/apps/server/src/browtrix_server/
├── __init__.py
├── __main__.py
├── server.py
├── settings.py
└── core/
    ├── connection/
    │   ├── errors.py
    │   └── manager.py
    ├── tools/
    │   ├── alert_tool.py
    │   ├── base.py
    │   ├── popup_tool.py
    │   └── snapshot_tool.py
    ├── types/
    └── resources.py
```

#### 1.3 Connection Manager (`src/browtrix_server/core/connection/manager.py`)
Implemented `ConnectionManager` with:
- Active connection tracking (`active_connections`).
- Request/Response handling with `asyncio.Future`.
- Health monitoring (`ConnectionHealthMonitor`) to detect stale connections.
- Statistics tracking (request counts, response times).
- `connect`/`disconnect` logic with connection limits.

#### 1.4 Settings (`src/browtrix_server/settings.py`)
Implemented configuration using `pydantic-settings`.

#### 1.5 Server Logic (`src/browtrix_server/server.py`)
- `FastAPI` wrapper initialized.
- `FastMCP` server mounted.
- WebSocket endpoint `/ws` connected to `ConnectionManager`.
- Health check (`/health`) and stats (`/stats`) endpoints added.
- MCP Tools implemented:
    - `html_snapshot()`: Uses `SnapshotTool`.
    - `confirmation_alert()`: Uses `AlertTool`.
    - `question_popup()`: Uses `PopupTool`.

#### 1.6 Entry Point (`src/browtrix_server/__main__.py`)
- Uses `uvicorn` to run the app.

### Phase 2: Frontend Foundation (Next.js) - ✅ Completed

#### 2.1 Dependencies
- Next.js project set up.

#### 2.2 WebSocket Context (`browtrix/apps/web/src/lib/contexts/browtrix-context.tsx`)
- `BrowtrixProvider` implemented.
- Handles connection, reconnection, and message sending.
- Exposes `isConnected`, `lastMessage`, `sendMessage`.

#### 2.3 Snapshot Logic (`browtrix/apps/web/src/lib/utils/snapshot.ts`)
- `captureSnapshot()` implemented.
- Captures full HTML (`document.documentElement.outerHTML`).
- Cleans up scripts and hidden elements before capture.
- *Note: Changed from Markdown conversion to raw HTML capture for better fidelity.*

### Phase 3: Frontend Feature Implementation - ✅ Completed

#### 3.1 Browtrix Overlay Component (`browtrix/apps/web/src/components/overlay/browtrix-overlay.tsx`)
- Implemented using `shadcn/ui` components (`Card`, `Button`, `Input`).
- Handles:
    - `GET_SNAPSHOT`: Captures HTML and sends back immediately.
    - `SHOW_CONFIRM`: Displays confirmation dialog.
    - `SHOW_INPUT`: Displays input dialog with validation.
- State management for active requests.

#### 3.2 Integrate into App
- `BrowtrixProvider` and `BrowtrixOverlay` integrated into the app layout.

### Phase 4: Integration & Verification - ✅ Completed

#### 4.1 Development Workflow
- Server runs on port 8000.
- Web app runs on port 3001.

## 4. Detailed Implementation Notes

### Server-Side Tools (`apps/server/src/browtrix_server/core/tools/`)
- **SnapshotTool**: Handles `html_snapshot` requests. Supports `wait_for` selector, `full_page` flag, and timeouts.
- **AlertTool**: Handles `confirmation_alert` requests. Supports custom titles and timeouts.
- **PopupTool**: Handles `question_popup` requests. Supports input types (`text`, `email`, `password`, `number`) and validation (`any`, `email`, `number`, `url`, `regex`).

### Client-Side Handling (`apps/web/src/components/overlay/browtrix-overlay.tsx`)
- **Snapshot**: Returns `html_content`, `url`, `title`, and metadata.
- **Confirmation**: Returns `approved` (boolean) and `button_clicked`.
- **Input**: Returns `value`, `input_type`, and `validation_passed`. Client-side validation implemented for email.

## 5. Future Considerations
- **Security**: Add authentication to WS connection (currently open).
- **Multiple Clients**: Better handling of targeting specific browser sessions (currently selects best/last active).
- **Markdown Support**: Re-evaluate adding Markdown conversion for snapshots if needed.
- **Screenshot Support**: Add ability to capture image screenshots (canvas/html2canvas).
