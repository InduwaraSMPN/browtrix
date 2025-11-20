from browtrix_server.core.connection.errors import (
    BrowserConnectionError,
    BrowserTimeoutError,
    ValidationError,
)


def test_browser_connection_error():
    err = BrowserConnectionError("test", connection_state="failed")
    assert "test" in str(err)
    assert err.connection_state == "failed"


def test_browser_timeout_error():
    err = BrowserTimeoutError("timeout", operation="click", timeout_duration=5)
    assert "timeout" in str(err)
    assert err.operation == "click"


def test_validation_error():
    err = ValidationError("field", "value", "msg")
    assert err.message == "msg"
    assert err.field_name == "field"
    assert err.field_value == "value"
