import pytest
from unittest.mock import AsyncMock, MagicMock
from browtrix_server.core.tools.snapshot_tool import SnapshotTool, SnapshotOptions


@pytest.mark.asyncio
async def test_snapshot_tool_execute():
    """Test snapshot tool execution with mocked connection manager."""
    tool = SnapshotTool()
    mock_cm = MagicMock()
    mock_response = MagicMock()
    mock_response.success = True
    mock_response.html_content = "<html><body>Test</body></html>"
    mock_cm.send_request = AsyncMock(return_value=mock_response)
    tool._connection_manager = mock_cm

    options = SnapshotOptions()
    result = await tool.execute(
        options=options
    )  # Fixed: use execute instead of safe_execute

    assert result.success
    assert "html_content" in result.data
    assert result.data["html_content"] == "<html><body>Test</body></html>"
