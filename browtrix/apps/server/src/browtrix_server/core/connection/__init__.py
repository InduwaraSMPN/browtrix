"""
Connection management module for Browtrix server.
"""

from .manager import ConnectionManager, ConnectionHealthMonitor
from .errors import (
    BrowtrixError,
    BrowserConnectionError,
    BrowserTimeoutError,
    ToolExecutionError,
    ValidationError,
    ConfigurationError,
    HealthCheckError,
)

__all__ = [
    "ConnectionManager",
    "ConnectionHealthMonitor",
    "BrowtrixError",
    "BrowserConnectionError",
    "BrowserTimeoutError",
    "ToolExecutionError",
    "ValidationError",
    "ConfigurationError",
    "HealthCheckError",
]
