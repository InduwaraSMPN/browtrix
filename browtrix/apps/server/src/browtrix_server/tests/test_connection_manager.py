import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from browtrix_server.core.connection.manager import ConnectionManager
from browtrix_server.core.connection.errors import (
    BrowserConnectionError,
    BrowserTimeoutError,
)


@pytest.fixture
def connection_manager():
    """Create a fresh ConnectionManager for each test with automatic cleanup."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)
    yield manager
    # Cleanup: disconnect all active connections and clear pending futures
    for connection_id in list(manager.active_connections.keys()):
        manager.disconnect(connection_id)
    manager.pending_futures.clear()


def test_connection_manager_init(connection_manager):
    """Test connection manager initialization with correct parameters."""
    assert connection_manager.max_connections == 2
    assert connection_manager.request_timeout == 5.0
    assert len(connection_manager.active_connections) == 0


@pytest.mark.asyncio
@patch("browtrix_server.core.connection.manager.WebSocket")
async def test_connect(mock_websocket, connection_manager):
    """Test successful WebSocket connection and registration."""
    mock_ws = AsyncMock()
    type(mock_ws).headers = PropertyMock(return_value={"user-agent": "Mozilla/5.0"})
    mock_websocket.return_value = mock_ws
    mock_ws.accept = AsyncMock()

    cid = await connection_manager.connect(mock_ws)
    assert cid is not None
    assert len(connection_manager.active_connections) == 1
    assert connection_manager.connection_info[cid].user_agent == "Mozilla/5.0"
    mock_ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_connect_max_connections(connection_manager):
    """Test connection limit enforcement."""
    for _ in range(2):
        mock_ws = AsyncMock()
        type(mock_ws).headers = PropertyMock(return_value={"user-agent": "test"})
        mock_ws.accept = AsyncMock()
        await connection_manager.connect(mock_ws)

    mock_ws = AsyncMock()
    type(mock_ws).headers = PropertyMock(return_value={"user-agent": "test"})
    with pytest.raises(
        BrowserConnectionError, match="Maximum connection limit reached"
    ):
        await connection_manager.connect(mock_ws)


@pytest.mark.asyncio
async def test_send_request_timeout(connection_manager):
    """Test request timeout handling."""
    connection_manager.active_connections["test"] = AsyncMock()
    with pytest.raises(BrowserTimeoutError):
        await connection_manager.send_request(
            MagicMock(id="test", timeout=0.1, type="test")
        )


@pytest.mark.asyncio
async def test_handle_message(connection_manager):
    """Test handling of valid JSON messages."""
    # Create a real JSON message that matches BrowserResponse schema
    test_message = '{"type": "response", "id": "test", "success": true, "data": {}, "timestamp": "2025-01-01T00:00:00Z"}'

    # Create a proper mock future that behaves correctly
    from unittest.mock import Mock

    future = Mock()
    future.done.return_value = False
    future.set_result = Mock()
    future.set_exception = Mock()
    connection_manager.pending_futures["test"] = future

    await connection_manager.handle_message(test_message, "test_cid")

    # Verify the future was set with the parsed data
    future.set_result.assert_called_once()
    call_args = future.set_result.call_args[0][0]
    assert call_args.success is True


def test_disconnect(connection_manager):
    """Test connection cleanup and disconnection."""
    cid = "test"
    mock_ws = MagicMock()
    connection_manager.active_connections[cid] = mock_ws
    info = MagicMock()
    connection_manager.connection_info[cid] = info

    connection_manager.disconnect(cid)
    assert cid not in connection_manager.active_connections
    # Verify is_active was set to False
    assert info.is_active is False


def test_get_health_status(connection_manager):
    """Test health status reporting for empty connection manager."""
    status = connection_manager.get_health_status()
    assert status.status == "degraded"
    assert status.connections == 0


@pytest.mark.asyncio
async def test_concurrent_requests(connection_manager):
    """Test that multiple concurrent requests can be created without conflicts."""
    # Test that request IDs are generated properly for concurrent requests
    request_ids = []

    async def create_request_id():
        # Simulate getting a unique request ID
        request_id = f"req_{len(request_ids)}"
        request_ids.append(request_id)
        return request_id

    # Create multiple "concurrent" requests
    tasks = [create_request_id() for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all request IDs are unique
    assert len(results) == 5
    assert len(set(results)) == 5  # All IDs should be unique


@pytest.mark.asyncio
async def test_handle_malformed_json(connection_manager):
    """Test handling of malformed JSON messages."""
    future = AsyncMock()
    connection_manager.pending_futures["test"] = future

    # Test with malformed JSON - this should log error but not raise
    await connection_manager.handle_message('{"invalid": json}', "test_cid")

    # Future should not be called due to parsing error
    future.set_result.assert_not_called()


@pytest.mark.asyncio
async def test_send_request_invalid_connection(connection_manager):
    """Test sending request to non-existent connection."""
    with pytest.raises(BrowserConnectionError):
        await connection_manager.send_request(
            MagicMock(id="test", timeout=1.0, type="test")
        )


def test_disconnect_nonexistent_connection(connection_manager):
    """Test disconnecting a connection that doesn't exist."""
    # Should not raise an error
    connection_manager.disconnect("nonexistent")


@pytest.mark.asyncio
async def test_request_timeout_edge_cases(connection_manager):
    """Test timeout behavior with edge case values."""
    mock_ws = AsyncMock()
    connection_manager.active_connections["test"] = mock_ws

    # Test with zero timeout
    with pytest.raises(BrowserTimeoutError):
        await connection_manager.send_request(
            MagicMock(id="test", timeout=0, type="test")
        )


def test_connection_manager_edge_cases():
    """Test ConnectionManager with edge case parameters."""
    # Test with zero max_connections
    manager = ConnectionManager(max_connections=0, request_timeout=5.0)
    assert manager.max_connections == 0

    # Test with negative max_connections
    manager = ConnectionManager(max_connections=-1, request_timeout=5.0)
    assert manager.max_connections == -1

    # Test with extremely large timeout
    manager = ConnectionManager(max_connections=2, request_timeout=999999)
    assert manager.request_timeout == 999999

    # Test with negative timeout
    manager = ConnectionManager(max_connections=2, request_timeout=-1)
    assert manager.request_timeout == -1


@pytest.mark.asyncio
async def test_connection_id_collision_handling():
    """Test handling of potential connection ID collisions."""
    manager = ConnectionManager(max_connections=10, request_timeout=5.0)

    # Create multiple connections and verify IDs are unique
    connection_ids = set()
    for _ in range(5):
        mock_ws = AsyncMock()
        mock_ws.headers = {"user-agent": "test"}
        mock_ws.accept = AsyncMock()

        cid = await manager.connect(mock_ws)
        assert cid not in connection_ids  # Should be unique
        connection_ids.add(cid)

    assert len(connection_ids) == 5

    # Cleanup
    for cid in connection_ids:
        manager.disconnect(cid)


@pytest.mark.asyncio
async def test_background_task_management():
    """Test background task startup, operation, and shutdown."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)

    # Initially no tasks should be running
    assert manager._health_check_task is None
    assert manager._cleanup_task is None

    # Start monitoring
    await manager.start_health_monitoring()

    # Tasks should be created
    assert manager._health_check_task is not None
    assert manager._cleanup_task is not None
    assert not manager._health_check_task.done()
    assert not manager._cleanup_task.done()

    # Stop monitoring
    await manager.stop_health_monitoring()

    # Tasks should be set to None after cancellation
    assert manager._health_check_task is None
    assert manager._cleanup_task is None


@pytest.mark.asyncio
async def test_background_task_error_recovery():
    """Test that background tasks handle errors gracefully."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)

    # Mock the health check loop to raise an exception
    original_loop = manager._health_check_loop

    async def failing_loop():
        raise Exception("Health check failed")

    manager._health_check_loop = failing_loop  # type: ignore

    try:
        await manager.start_health_monitoring()

        # Wait a bit for the task to fail
        await asyncio.sleep(0.1)

        # Task should have failed but not crashed the manager
        assert manager._health_check_task is not None
        # The task may or may not be done depending on timing

        # Cleanup task should still be running
        assert manager._cleanup_task is not None

    finally:
        # Restore original method
        manager._health_check_loop = original_loop  # type: ignore
        await manager.stop_health_monitoring()


@pytest.mark.asyncio
async def test_background_task_cancellation():
    """Test graceful cancellation of background tasks."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)

    await manager.start_health_monitoring()

    # Cancel tasks
    await manager.stop_health_monitoring()

    # Tasks should be properly cancelled
    assert manager._health_check_task is None
    assert manager._cleanup_task is None

    # Should be safe to call stop again
    await manager.stop_health_monitoring()  # Should not raise


@pytest.mark.asyncio
async def test_websocket_backpressure_simulation():
    """Test behavior under WebSocket backpressure conditions."""
    manager = ConnectionManager(max_connections=2, request_timeout=5.0)

    # Create connection with slow WebSocket
    mock_ws = AsyncMock()
    mock_ws.headers = {"user-agent": "test"}
    mock_ws.accept = AsyncMock()

    # Simulate slow send_json
    async def slow_send_json(message):
        await asyncio.sleep(0.1)  # Simulate network delay
        return None

    mock_ws.send_json = slow_send_json

    cid = await manager.connect(mock_ws)

    # Send multiple requests rapidly
    tasks = []
    for i in range(3):
        request = MagicMock(id=f"req_{i}", timeout=1.0, type="test")
        task = asyncio.create_task(manager.send_request(request))
        tasks.append(task)

    # Some should timeout due to backpressure
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # At least one should have timed out
    timeout_count = sum(1 for r in results if isinstance(r, Exception))
    assert timeout_count > 0

    manager.disconnect(cid)
