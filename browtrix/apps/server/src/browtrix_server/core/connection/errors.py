"""
Custom exceptions for Browtrix connection management and tool execution.
"""

from typing import Any, Dict, Optional


class BrowtrixError(Exception):
    """Base exception for all Browtrix-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause


class BrowserConnectionError(BrowtrixError):
    """Raised when browser connection fails or is unavailable."""

    def __init__(
        self,
        message: str = "Browser connection failed",
        browser_id: Optional[str] = None,
        connection_state: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, kwargs)
        self.browser_id = browser_id
        self.connection_state = connection_state


class BrowserTimeoutError(BrowtrixError):
    """Raised when browser operation times out."""

    def __init__(
        self,
        message: str = "Browser operation timed out",
        operation: Optional[str] = None,
        timeout_duration: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, kwargs)
        self.operation = operation
        self.timeout_duration = timeout_duration


class ToolExecutionError(BrowtrixError):
    """Raised when a tool execution fails."""

    def __init__(
        self,
        tool_name: str,
        message: str = "Tool execution failed",
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(message, kwargs)
        self.tool_name = tool_name
        self.parameters = parameters or {}


class ValidationError(BrowtrixError):
    """Raised when parameter validation fails."""

    def __init__(
        self,
        field_name: str,
        field_value: Any,
        message: str = "Validation failed",
        validation_rule: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, kwargs)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class ConfigurationError(BrowtrixError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, message: str = "Configuration error", **kwargs):
        super().__init__(message, kwargs)
        self.config_key = config_key


class HealthCheckError(BrowtrixError):
    """Raised when health check fails."""

    def __init__(self, component: str, message: str = "Health check failed", **kwargs):
        super().__init__(message, kwargs)
        self.component = component
