"""
Response type definitions for Browtrix communication.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BrowserResponse(BaseModel):
    """Standardized response model for browser operations."""

    model_config = ConfigDict(
        extra="allow"
    )  # Allow additional fields for extensibility

    id: str
    success: bool = False
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SnapshotResponse(BrowserResponse):
    """Response for HTML snapshot."""

    html_content: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    wait_time_ms: Optional[float] = None
    snapshot_info: Dict[str, Any] = Field(default_factory=dict)


class ConfirmationResponse(BrowserResponse):
    """Response for confirmation alert."""

    approved: bool = False
    selection_time_ms: Optional[float] = None
    button_clicked: Optional[str] = None
    timeout_occurred: bool = False


class InputResponse(BrowserResponse):
    """Response for user input popup."""

    user_input: Optional[str] = None
    input_type: Optional[str] = None
    validation_passed: bool = True
    validation_message: Optional[str] = None
    submission_time_ms: Optional[float] = None


class ExecuteJSResponse(BrowserResponse):
    """Response for JavaScript execution."""

    result: Optional[Any] = None
    error_details: Optional[str] = None
    execution_context: Optional[str] = None


class ScreenshotResponse(BrowserResponse):
    """Response for screenshot."""

    image_data: Optional[str] = None  # Base64 encoded image
    file_path: Optional[str] = None
    image_format: Optional[str] = None
    dimensions: Dict[str, int] = Field(default_factory=dict)


class HealthCheckResponse(BrowserResponse):
    """Response for health check endpoint."""

    status: str = "healthy"
    uptime_seconds: Optional[float] = None
    active_connections: int = 0
    memory_usage_mb: Optional[float] = None
    version: str = "0.1.0"
    connections: Optional[int] = None
    last_activity: Optional[datetime] = None
    components: Optional[Dict[str, str]] = None


class ConnectionInfo(BaseModel):
    """Connection information for monitoring."""

    connection_id: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    request_count: int = 0
    error_count: int = 0
    avg_response_time_ms: Optional[float] = None
    is_active: bool = True
    browser_id: Optional[str] = None
    user_agent: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.now)
