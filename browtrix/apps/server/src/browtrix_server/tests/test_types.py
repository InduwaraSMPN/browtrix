import pytest
from pydantic import ValidationError
from pydantic_core import ValidationError as PydanticCoreError
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
    """Test that snapshot request validates wait_timeout constraints."""
    # Test valid timeout
    req = SnapshotRequest(wait_timeout=10.0)
    assert req.wait_timeout == 10.0

    # Test minimum timeout
    req = SnapshotRequest(wait_timeout=0.1)
    assert req.wait_timeout == 0.1

    # Test maximum timeout
    req = SnapshotRequest(wait_timeout=300.0)
    assert req.wait_timeout == 300.0

    # Test invalid timeouts
    with pytest.raises(ValidationError):
        SnapshotRequest(wait_timeout=-1)  # Too low

    with pytest.raises(ValidationError):
        SnapshotRequest(wait_timeout=0)  # Too low

    with pytest.raises(ValidationError):
        SnapshotRequest(wait_timeout=301)  # Too high


def test_browser_request_validation():
    """Test BrowserRequest field validation."""
    # Test valid request
    req = BrowserRequest(type="test", timeout=30.0, priority=0)
    assert req.timeout == 30.0
    assert req.priority == 0

    # Test timeout validation
    with pytest.raises(ValidationError):
        BrowserRequest(type="test", timeout=-1)  # Negative timeout

    with pytest.raises(ValidationError):
        BrowserRequest(type="test", timeout=0)  # Zero timeout

    with pytest.raises(ValidationError):
        BrowserRequest(type="test", timeout=301)  # Too high timeout

    # Test priority validation
    with pytest.raises(ValidationError):
        BrowserRequest(type="test", priority=-11)  # Too low priority

    with pytest.raises(ValidationError):
        BrowserRequest(type="test", priority=11)  # Too high priority

    # Test valid priority range
    req = BrowserRequest(type="test", priority=-10)
    assert req.priority == -10

    req = BrowserRequest(type="test", priority=10)
    assert req.priority == 10


def test_type_coercion_and_defaults():
    """Test Pydantic type coercion and default value handling."""
    # Test default values
    req = BrowserRequest(type="test")
    assert req.timeout == 30.0
    assert req.priority == 0
    assert isinstance(req.params, dict)
    assert len(req.params) == 0
    assert isinstance(req.id, str)
    assert len(req.id) > 0

    # Test that strings are coerced to numbers (Pydantic default behavior)
    req = BrowserRequest(type="test", timeout="60", priority="5")  # type: ignore
    assert req.timeout == 60.0
    assert req.priority == 5


def test_pydantic_serialization_edge_cases():
    """Test Pydantic serialization with edge cases."""
    # Test with None values in optional fields
    req = SnapshotRequest(wait_for=None)
    assert req.wait_for is None

    # Test serialization
    data = req.model_dump()
    assert "wait_for" in data
    assert data["wait_for"] is None

    # Test JSON serialization
    json_data = req.model_dump_json()
    assert isinstance(json_data, str)

    # Test round-trip serialization
    req2 = SnapshotRequest.model_validate_json(json_data)
    assert req2.wait_timeout == req.wait_timeout


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
