import pytest
from fastapi.testclient import TestClient
from browtrix_server.server import app, get_global_server


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
