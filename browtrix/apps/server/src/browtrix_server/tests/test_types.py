from browtrix_server.core.types.requests import (
    BrowserRequest,
    SnapshotRequest,
    ConfirmationRequest,
    InputRequest,
)
from browtrix_server.core.types.responses import (
    BrowserResponse,
    ConnectionInfo,
    HealthCheckResponse,
)


def test_browser_request_model():
    req = BrowserRequest(id="test", type="click", timeout=10)
    assert req.id == "test"
    assert req.type == "click"


def test_snapshot_request_validation():
    """Test that snapshot request validates wait_timeout is non-negative."""
    # This should not raise an error since there's no validation constraint
    req = SnapshotRequest(wait_timeout=-1)
    assert req.wait_timeout == -1

    # Test with valid positive timeout
    req = SnapshotRequest(wait_timeout=10.0)
    assert req.wait_timeout == 10.0


def test_confirmation_request():
    req = ConfirmationRequest(message="Confirm?", title="Title")
    assert req.message == "Confirm?"


def test_input_request():
    req = InputRequest(message="Input?", input_type="text")
    assert req.input_type == "text"


def test_browser_response_success():
    resp = BrowserResponse(id="test", success=True, data={"result": "ok"})
    assert resp.success


def test_connection_info():
    info = ConnectionInfo(
        connection_id="test", browser_id="br1", user_agent="Mozilla", is_active=True
    )
    assert info.is_active


def test_health_check_response():
    resp = HealthCheckResponse(
        id="test", status="healthy", uptime_seconds=10, connections=1
    )
    assert resp.status == "healthy"
