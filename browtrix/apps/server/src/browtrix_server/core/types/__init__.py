"""
Request and response type definitions for Browtrix server.
"""

from .requests import (
    BrowserRequest,
    SnapshotRequest,
    ConfirmationRequest,
    InputRequest,
    ExecuteJSRequest,
    ScreenshotRequest,
)
from .responses import (
    BrowserResponse,
    SnapshotResponse,
    ConfirmationResponse,
    InputResponse,
    ExecuteJSResponse,
    ScreenshotResponse,
    HealthCheckResponse,
    ConnectionInfo,
)

__all__ = [
    # Request Types
    "BrowserRequest",
    "SnapshotRequest",
    "ConfirmationRequest",
    "InputRequest",
    "ExecuteJSRequest",
    "ScreenshotRequest",
    # Response Types
    "BrowserResponse",
    "SnapshotResponse",
    "ConfirmationResponse",
    "InputResponse",
    "ExecuteJSResponse",
    "ScreenshotResponse",
    "HealthCheckResponse",
    "ConnectionInfo",
]
