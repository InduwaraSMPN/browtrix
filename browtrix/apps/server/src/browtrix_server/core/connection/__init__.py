"""
Connection management module for Browtrix MCP Server.
"""

from .manager import ConnectionManager, ConnectionHealthMonitor
from .errors import (
    BrowtrixError,
    BrowserConnectionError,
    BrowserTimeoutError,
    ToolExecutionError,
    ValidationError,
)

__all__ = [
    "ConnectionManager",
    "ConnectionHealthMonitor",
    "BrowtrixError",
    "BrowserConnectionError",
    "BrowserTimeoutError",
    "ToolExecutionError",
    "ValidationError",
]
