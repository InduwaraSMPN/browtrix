"""
Request and response type definitions for Browtrix communication.
"""

from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4
import time


class BrowserRequest(BaseModel):
    """Standardized request model for browser operations."""

    model_config = ConfigDict(
        extra="allow"
    )  # Allow additional fields for extensibility

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    timeout: float = Field(default=30.0, ge=0.1, le=300.0)  # Between 0.1s and 5min
    priority: int = Field(default=0, ge=-10, le=10)  # Priority range


class SnapshotRequest(BrowserRequest):
    """Request for HTML snapshot."""

    type: Literal["GET_SNAPSHOT"] = "GET_SNAPSHOT"
    wait_for: Optional[str] = None
    full_page: bool = True
    wait_timeout: float = Field(default=10.0, ge=0.1, le=300.0)  # Between 0.1s and 5min


class ConfirmationRequest(BrowserRequest):
    """Request for confirmation alert."""

    type: Literal["SHOW_CONFIRM"] = "SHOW_CONFIRM"
    message: str
    title: str = "Confirmation"
    timeout: float = 60.0


class InputRequest(BrowserRequest):
    """Request for user input popup."""

    type: Literal["SHOW_INPUT"] = "SHOW_INPUT"
    message: str
    title: str = "Input Required"
    input_type: Literal["text", "email", "password", "number"] = "text"
    placeholder: Optional[str] = None
    validation: Literal["any", "email", "number", "url", "regex"] = "any"
    validation_pattern: Optional[str] = None


class ExecuteJSRequest(BrowserRequest):
    """Request for JavaScript execution."""

    type: Literal["EXECUTE_JS"] = "EXECUTE_JS"
    script: str
    wait_for_element: Optional[str] = None
    timeout: float = 15.0


class ScreenshotRequest(BrowserRequest):
    """Request for screenshot."""

    type: Literal["TAKE_SCREENSHOT"] = "TAKE_SCREENSHOT"
    selector: Optional[str] = None
    full_page: bool = True
    quality: int = 90
    format: Literal["png", "jpeg", "webp"] = "png"
