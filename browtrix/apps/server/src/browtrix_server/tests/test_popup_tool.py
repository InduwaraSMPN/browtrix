import pytest
from unittest.mock import AsyncMock, MagicMock
from browtrix_server.core.tools.popup_tool import PopupTool, PopupOptions
from browtrix_server.core.types.responses import BrowserResponse


@pytest.mark.asyncio
async def test_popup_tool_execute():
    """Test popup tool execution with mocked connection manager."""
    tool = PopupTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = True
    mock_response.value = "test input"
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = PopupOptions(question="Test question")
    result = await tool.execute(options=options)

    assert result.success
    assert result.data["value"] == "test input"


@pytest.mark.asyncio
async def test_popup_tool_execute_with_empty_response():
    """Test popup tool execution with empty user input (should fail for required field)."""
    tool = PopupTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = True
    mock_response.value = ""
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = PopupOptions(question="Test question")  # required=True by default
    result = await tool.execute(options=options)

    # Should fail because required field is empty
    assert not result.success
    assert result.error == "Required field was not filled"


@pytest.mark.asyncio
async def test_popup_tool_execute_with_optional_empty_response():
    """Test popup tool execution with empty user input for optional field."""
    tool = PopupTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = True
    mock_response.value = ""
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = PopupOptions(question="Test question", required=False)
    result = await tool.execute(options=options)

    # Should succeed because field is optional
    assert result.success
    assert result.data["value"] == ""


@pytest.mark.asyncio
async def test_popup_tool_execute_failure():
    """Test popup tool execution when connection fails."""
    tool = PopupTool()
    tool._connection_manager = MagicMock()
    mock_response = MagicMock(spec=BrowserResponse)
    mock_response.success = False
    mock_response.error = "User cancelled"
    tool._connection_manager.send_request = AsyncMock(return_value=mock_response)

    options = PopupOptions(question="Test question")
    result = await tool.execute(options=options)

    assert not result.success
    assert result.error == "User cancelled"
