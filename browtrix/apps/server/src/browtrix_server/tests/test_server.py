from unittest.mock import patch
from browtrix_server.server import BrowtrixServer, ServerConfig


@patch("browtrix_server.server.ConnectionManager")
@patch("browtrix_server.server.FastMCP")
@patch("browtrix_server.server.FastAPI")
def test_browtrix_server_init(mock_fastapi, mock_mcp, mock_connection):
    config = ServerConfig()
    BrowtrixServer(config)
    mock_connection.assert_called_once_with(max_connections=10, request_timeout=30.0)
    mock_mcp.assert_called_once_with("browtrix-server")
    mock_fastapi.assert_called_once()


def test_server_config_defaults():
    config = ServerConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 8000
    assert config.max_connections == 10


def test_server_config_custom():
    config = ServerConfig(host="localhost", port=9000, max_connections=5)
    assert config.host == "localhost"
    assert config.port == 9000
    assert config.max_connections == 5
