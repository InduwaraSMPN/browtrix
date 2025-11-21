import pytest
from unittest.mock import AsyncMock, MagicMock
from browtrix_server.core.tools.alert_tool import AlertTool, AlertOptions
from browtrix_server.core.types.responses import BrowserResponse


@pytest.mark.asyncio
async def test_alert_tool_execute():
    """Test alert tool execution with mocked connection manager."""
    tool = AlertTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = True
    mock_response.approved = True
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = AlertOptions(message="Test alert")
    result = await tool.execute(options=options)

    assert result.success
    assert result.data["approved"] is True


@pytest.mark.asyncio
async def test_alert_tool_execute_failure():
    """Test alert tool execution when connection fails."""
    tool = AlertTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = False
    mock_response.error = "Connection failed"
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = AlertOptions(message="Test alert")
    result = await tool.execute(options=options)

    assert not result.success
    assert result.error == "Connection failed"


@pytest.mark.asyncio
async def test_alert_tool_connection_error():
    """Test alert tool execution when connection manager raises error."""
    tool = AlertTool()
    tool._connection_manager = MagicMock()
    tool._connection_manager.send_request = AsyncMock(
        side_effect=Exception("Connection error")
    )

    options = AlertOptions(message="Test alert")
    result = await tool.execute(options=options)

    assert not result.success
    assert result.error is not None
    assert "Connection error" in result.error
