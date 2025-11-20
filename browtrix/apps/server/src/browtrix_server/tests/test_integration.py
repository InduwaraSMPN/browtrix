import pytest
import asyncio
import json
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from browtrix_server.server import app, get_global_server
from browtrix_server.core.connection.manager import ConnectionManager
from browtrix_server.core.tools.alert_tool import AlertTool, AlertOptions
from browtrix_server.core.tools.popup_tool import PopupTool, PopupOptions
from browtrix_server.core.tools.snapshot_tool import SnapshotTool, SnapshotOptions
from browtrix_server.core.types.requests import BrowserRequest
from browtrix_server.core.types.responses import BrowserResponse


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint returns degraded status when no connections."""
    response = client.get("/health")
    # Should return 503 when no active connections (status is "degraded")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"


def test_info_endpoint(client):
    """Test info endpoint returns server information."""
    response = client.get("/info")
    assert response.status_code == 200
    assert "name" in response.json()


@pytest.mark.asyncio
async def test_server_startup():
    """Test global server initialization and configuration."""
    server = get_global_server()
    assert server.connection_manager
    assert server.mcp.name == "browtrix-server"


class MockWebSocketClient:
    """Test WebSocket client for integration testing."""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.connection_id = None
        self.received_messages = []
        self.mock_ws = AsyncMock()

    async def connect(self):
        """Simulate WebSocket connection."""
        self.mock_ws.headers = {"user-agent": "TestBrowser/1.0"}
        self.mock_ws.accept = AsyncMock()
        self.connection_id = await self.connection_manager.connect(self.mock_ws)
        return self.connection_id

    async def send_message(self, message: dict):
        """Send a message to the connection manager."""
        json_message = json.dumps(message)
        if self.connection_id:
            await self.connection_manager.handle_message(
                json_message, self.connection_id
            )

    async def receive_response(
        self, request_id: str, timeout: float = 1.0
    ) -> BrowserResponse:
        """Wait for and return a response for the given request ID."""
        future = self.connection_manager.pending_futures.get(request_id)
        if future:
            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                raise TimeoutError(f"No response received for request {request_id}")
        raise ValueError(f"No pending future for request {request_id}")

    async def disconnect(self):
        """Disconnect the WebSocket."""
        if self.connection_id:
            self.connection_manager.disconnect(self.connection_id)


@pytest.fixture(scope="function")
def websocket_client():
    """Create a test WebSocket client connected to a fresh connection manager."""
    import asyncio

    manager = ConnectionManager(max_connections=5, request_timeout=5.0)
    client = MockWebSocketClient(manager)

    # Create event loop for fixture
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(client.connect())
        yield client
    finally:
        # Cleanup
        loop.run_until_complete(client.disconnect())
        manager.pending_futures.clear()
        loop.close()


@pytest.mark.asyncio
async def test_websocket_connection_lifecycle(websocket_client):
    """Test complete WebSocket connection lifecycle."""
    # Connection should be established
    assert websocket_client.connection_id is not None
    assert (
        websocket_client.connection_id
        in websocket_client.connection_manager.active_connections
    )

    # Connection info should be stored
    assert (
        websocket_client.connection_id
        in websocket_client.connection_manager.connection_info
    )
    info = websocket_client.connection_manager.connection_info[
        websocket_client.connection_id
    ]
    assert info.user_agent == "TestBrowser/1.0"
    assert info.is_active is True

    # Disconnect
    await websocket_client.disconnect()

    # Connection should be cleaned up from active connections
    assert (
        websocket_client.connection_id
        not in websocket_client.connection_manager.active_connections
    )

    # Connection info should still exist but marked as inactive
    assert (
        websocket_client.connection_id
        in websocket_client.connection_manager.connection_info
    )
    info = websocket_client.connection_manager.connection_info[
        websocket_client.connection_id
    ]
    assert info.is_active is False


@pytest.mark.asyncio
async def test_full_request_response_cycle(websocket_client):
    """Test complete request/response cycle through WebSocket."""

    # Mock the WebSocket to simulate browser response
    async def mock_send_json(message):
        # Simulate browser sending response back
        response_message = {
            "type": "response",
            "id": "test_request_123",
            "success": True,
            "data": {"result": "success"},
        }
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_message), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_send_json

    # Send a request through the connection manager
    request = BrowserRequest(
        id="test_request_123", type="TEST_REQUEST", params={"test": "data"}
    )

    # This should create a future and send the request
    task = asyncio.create_task(
        websocket_client.connection_manager.send_request(request)
    )

    # Wait for the response
    response = await asyncio.wait_for(task, timeout=2.0)

    # Verify the response
    assert response.success is True
    assert response.data["result"] == "success"
    assert response.id == "test_request_123"


@pytest.mark.asyncio
async def test_alert_tool_integration(websocket_client):
    """Test alert tool execution through full integration."""
    # Setup tool with real connection manager
    tool = AlertTool()
    tool._connection_manager = websocket_client.connection_manager

    # Mock browser response for alert
    async def mock_browser_response(message):
        # message is already a dict from send_json
        request_data = message
        # Create response data with extra fields included
        response_data = {"id": request_data["id"], "success": True, "approved": True}
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_data), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_browser_response

    # Execute alert tool
    options = AlertOptions(message="Integration test alert")
    result = await tool.execute(options=options)

    # Verify successful execution
    assert result.success is True
    assert result.data["approved"] is True


@pytest.mark.asyncio
async def test_popup_tool_integration(websocket_client):
    """Test popup tool execution through full integration."""
    tool = PopupTool()
    tool._connection_manager = websocket_client.connection_manager

    # Mock browser response for popup
    async def mock_browser_response(message):
        # message is already a dict from send_json
        request_data = message
        # Create response data with extra fields included
        response_data = {
            "id": request_data["id"],
            "success": True,
            "value": "user_input",
        }
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_data), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_browser_response

    # Execute popup tool
    options = PopupOptions(question="Integration test question?")
    result = await tool.execute(options=options)

    # Verify successful execution
    assert result.success is True
    assert result.data["value"] == "user_input"


@pytest.mark.asyncio
async def test_snapshot_tool_integration(websocket_client):
    """Test snapshot tool execution through full integration."""
    tool = SnapshotTool()
    tool._connection_manager = websocket_client.connection_manager

    # Mock browser response for snapshot
    async def mock_browser_response(message):
        # message is already a dict from send_json
        request_data = message
        response = BrowserResponse(
            id=request_data["id"],
            success=True,
            data={"html_content": "<html><body>Test</body></html>"},
        )
        response_message = response.model_dump(mode="json")
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_message), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_browser_response

    # Execute snapshot tool
    options = SnapshotOptions()
    result = await tool.execute(options=options)

    # Verify successful execution
    assert result.success is True
    assert "html_content" in result.data


@pytest.mark.asyncio
async def test_error_propagation_integration(websocket_client):
    """Test error propagation through the full stack."""
    tool = AlertTool()
    tool._connection_manager = websocket_client.connection_manager

    # Mock browser error response
    async def mock_browser_error(message):
        # message is already a dict from send_json
        request_data = message
        response = BrowserResponse(
            id=request_data["id"], success=False, error="Browser connection failed"
        )
        response_message = response.model_dump(mode="json")
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_message), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_browser_error

    # Execute tool - should propagate error
    options = AlertOptions(message="Error test")
    result = await tool.execute(options=options)

    # Verify error propagation
    assert result.success is False
    assert result.error is not None
    assert "Browser connection failed" in result.error


@pytest.mark.asyncio
async def test_concurrent_requests_integration(websocket_client):
    """Test handling multiple concurrent requests."""
    tool = AlertTool()
    tool._connection_manager = websocket_client.connection_manager

    request_count = 0

    # Mock browser responses for concurrent requests
    async def mock_concurrent_responses(message):
        nonlocal request_count
        # message is already a dict from send_json
        request_data = message
        request_count += 1

        # Simulate different response times
        await asyncio.sleep(0.01 * request_count)

        response_data = {"id": request_data["id"], "success": True, "approved": True}
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_data), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = mock_concurrent_responses

    # Execute multiple concurrent requests
    options = AlertOptions(message="Concurrent test")
    tasks = [tool.execute(options=options) for _ in range(5)]

    results = await asyncio.gather(*tasks)

    # Verify all requests succeeded
    assert len(results) == 5
    for result in results:
        assert result.success is True
        assert result.data["approved"] is True


@pytest.mark.asyncio
async def test_connection_limits_integration():
    """Test connection limit enforcement in integration."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)

    # Create multiple clients
    clients = []
    for i in range(3):  # Try to create more than max_connections
        client = MockWebSocketClient(manager)
        try:
            await client.connect()
            clients.append(client)
        except Exception:
            # Expected for the 3rd connection
            if i == 2:
                assert len(manager.active_connections) == 2
                break
            else:
                raise

    # Cleanup
    for client in clients:
        await client.disconnect()
    manager.pending_futures.clear()


@pytest.mark.asyncio
async def test_malformed_message_handling_integration(websocket_client):
    """Test handling of malformed messages in integration."""
    # Send malformed JSON
    await websocket_client.connection_manager.handle_message(
        '{"invalid": json}', websocket_client.connection_id
    )

    # Connection should still be active (error should be logged, not crash)
    assert (
        websocket_client.connection_id
        in websocket_client.connection_manager.active_connections
    )

    # Send message with missing required fields
    await websocket_client.connection_manager.handle_message(
        '{"type": "response"}', websocket_client.connection_id
    )

    # Connection should still be active
    assert (
        websocket_client.connection_id
        in websocket_client.connection_manager.active_connections
    )


@pytest.mark.asyncio
async def test_browser_refresh_during_pending_request(websocket_client):
    """Test behavior when browser refreshes during a pending request."""
    tool = AlertTool()
    tool._connection_manager = websocket_client.connection_manager

    # Start a request but don't wait for it
    task = asyncio.create_task(tool.execute(options=AlertOptions(message="Test")))

    # Simulate browser disconnecting (refresh) before response
    await asyncio.sleep(0.01)  # Let request start
    await websocket_client.disconnect()

    # Request should fail gracefully
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(task, timeout=1.0)


@pytest.mark.asyncio
async def test_network_partition_simulation(websocket_client):
    """Test behavior during network partition (simulated by slow responses)."""
    tool = AlertTool()
    tool._connection_manager = websocket_client.connection_manager

    # Simulate very slow network (longer than client timeout)
    async def very_slow_response(message):
        await asyncio.sleep(2)  # Longer than test timeout
        response = BrowserResponse(
            id=json.loads(message)["id"], success=True, data={"approved": True}
        )
        response_message = response.model_dump(mode="json")
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_message), websocket_client.connection_id
        )

    websocket_client.mock_ws.send_json = very_slow_response

    # Request should timeout due to slow network
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            tool.execute(options=AlertOptions(message="Slow test")), timeout=1.0
        )


@pytest.mark.asyncio
async def test_server_restart_simulation():
    """Test behavior when server restarts with active connections."""
    # Create manager and simulate active connections
    manager = ConnectionManager(max_connections=5, request_timeout=5.0)

    # Simulate connections that would exist before restart
    connection_ids = []
    for i in range(3):
        mock_ws = AsyncMock()
        mock_ws.headers = {"user-agent": f"Browser{i}"}
        mock_ws.accept = AsyncMock()
        cid = await manager.connect(mock_ws)
        connection_ids.append(cid)

    # Simulate some pending requests
    for i, cid in enumerate(connection_ids[:2]):
        future = AsyncMock()
        manager.pending_futures[f"req_{i}"] = future

    # "Server restart" - create new manager (simulating restart)
    new_manager = ConnectionManager(max_connections=5, request_timeout=5.0)

    # Old manager should still have its state (until cleanup)
    assert len(manager.active_connections) == 3
    assert len(manager.pending_futures) == 2

    # New manager starts clean
    assert len(new_manager.active_connections) == 0
    assert len(new_manager.pending_futures) == 0

    # Cleanup old manager
    for cid in connection_ids:
        manager.disconnect(cid)


@pytest.mark.asyncio
async def test_out_of_order_responses(websocket_client):
    """Test handling of responses that arrive out of order."""
    # Create futures manually to simulate pending requests
    futures = {}
    for i in range(3):
        from unittest.mock import Mock

        future = Mock()
        future.done.return_value = False
        future.set_result = Mock()
        future.set_exception = Mock()
        req_id = f"req_{i}"
        futures[req_id] = future
        websocket_client.connection_manager.pending_futures[req_id] = future

    # Simulate responses arriving out of order: 2, 0, 1
    response_order = [2, 0, 1]

    for req_index in response_order:
        req_id = f"req_{req_index}"
        response = BrowserResponse(
            id=req_id, success=True, data={"approved": True, "order": req_index}
        )
        response_message = response.model_dump(mode="json")
        await websocket_client.connection_manager.handle_message(
            json.dumps(response_message), websocket_client.connection_id
        )

    # All futures should have been called
    for future in futures.values():
        future.set_result.assert_called_once()

    # Pending futures should be cleared
    assert len(websocket_client.connection_manager.pending_futures) == 0
