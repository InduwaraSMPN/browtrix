"""
Core module for Browtrix server with  architecture.
"""

from .tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from .connection.errors import (
    BrowtrixError,
    BrowserConnectionError,
    BrowserTimeoutError,
    ToolExecutionError,
    ValidationError,
    ConfigurationError,
    HealthCheckError,
)
from .connection.manager import ConnectionManager, ConnectionHealthMonitor
from .types.requests import (
    BrowserRequest,
    SnapshotRequest,
    ConfirmationRequest,
    InputRequest,
)
from .types.responses import BrowserResponse, HealthCheckResponse, ConnectionInfo

__all__ = [
    # Tools
    "BaseBrowtrixTool",
    "ToolResult",
    "ToolValidator",
    # Connection Management
    "ConnectionManager",
    "ConnectionHealthMonitor",
    # Error Handling
    "BrowtrixError",
    "BrowserConnectionError",
    "BrowserTimeoutError",
    "ToolExecutionError",
    "ValidationError",
    "ConfigurationError",
    "HealthCheckError",
    # Request/Response Types
    "BrowserRequest",
    "SnapshotRequest",
    "ConfirmationRequest",
    "InputRequest",
    "BrowserResponse",
    "HealthCheckResponse",
    "ConnectionInfo",
]
