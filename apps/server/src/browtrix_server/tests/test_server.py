from unittest.mock import patch
from browtrix_server.server import BrowtrixServer, ServerConfig
from browtrix_server.settings import settings


@patch("browtrix_server.server.ConnectionManager")
@patch("browtrix_server.server.FastMCP")
@patch("browtrix_server.server.FastAPI")
def test_browtrix_server_init(mock_fastapi, mock_mcp, mock_connection):
    config = ServerConfig()
    BrowtrixServer(config)
    mock_connection.assert_called_once_with(
        max_connections=settings.max_connections,
        request_timeout=settings.request_timeout,
    )
    mock_mcp.assert_called_once_with(settings.mcp_server_name)
    mock_fastapi.assert_called_once()


def test_server_config_defaults():
    config = ServerConfig()
    assert config.host == settings.host
    assert config.port == settings.port
    assert config.max_connections == settings.max_connections


def test_server_config_custom():
    config = ServerConfig(host="localhost", port=9000, max_connections=5)
    assert config.host == "localhost"
    assert config.port == 9000
    assert config.max_connections == 5
