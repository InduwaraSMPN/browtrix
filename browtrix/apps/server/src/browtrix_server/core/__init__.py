"""
Core module for Browtrix MCP Server with  architecture.
"""

from .tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from .connection.errors import (
    BrowtrixError,
    BrowserConnectionError,
    BrowserTimeoutError,
    ToolExecutionError,
    ValidationError,
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
    # Request/Response Types
    "BrowserRequest",
    "SnapshotRequest",
    "ConfirmationRequest",
    "InputRequest",
    "BrowserResponse",
    "HealthCheckResponse",
    "ConnectionInfo",
]
