"""
snapshot tool with  features.
"""

from typing import Annotated, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import SnapshotRequest
from ..connection.errors import BrowserConnectionError, ValidationError


class SnapshotOptions(BaseModel):
    """snapshot options with validation."""

    wait_for: Annotated[
        Optional[str],
        Field(description="CSS selector to wait for before taking snapshot"),
    ] = None
    full_page: Annotated[
        bool, Field(description="Capture full page or visible area")
    ] = True
    wait_timeout: Annotated[
        int, Field(description="Timeout to wait for element", ge=1, le=60)
    ] = 10
    quality: Annotated[
        int, Field(description="Snapshot quality (1-100)", ge=1, le=100)
    ] = 100

    def validate_options(self):
        """Validate snapshot options."""
        if self.wait_for and not self.wait_for.strip():
            raise ValidationError(
                "wait_for", self.wait_for, "CSS selector cannot be empty"
            )
        return True


class SnapshotTool(BaseBrowtrixTool):
    """HTML snapshot tool with configurable options."""

    def __init__(self):
        super().__init__(
            name="html-snapshot",
            description="""HTML snapshot with configurable options.

Captures HTML content or screenshot of the current browser page.

Parameters:
- wait_for: CSS selector to wait for (optional)
- full_page: Capture full page (default: true)
- wait_timeout: Wait timeout in seconds (1-60, default: 10)
- quality: Image quality (1-100, default: 100)

Returns: HTML content, page URL, title, content size, and snapshot metadata.""",
        )
        self._connection_manager: Optional[Any] = None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute  snapshot with options."""
        try:
            # Get options from kwargs
            options = kwargs.get("options")
            if options:
                options.validate_options()
            else:
                options = SnapshotOptions()
                options.validate_options()

            # Create request
            request = SnapshotRequest(
                wait_for=options.wait_for,
                full_page=options.full_page,
                wait_timeout=float(options.wait_timeout),
            )

            # Get connection manager (would be injected)
            connection_manager = getattr(self, "_connection_manager", None)
            if not connection_manager:
                raise BrowserConnectionError("Connection manager not available")

            # Send request and get response
            response = await connection_manager.send_request(request)

            if not response.success:
                return ToolResult(success=False, error=response.error)

            # Extract HTML content
            html_content = ""
            if hasattr(response, "html_content") and response.html_content:
                html_content = response.html_content
            elif response.data:
                html_content = str(response.data)

            # Validate content
            if not html_content:
                return ToolResult(success=False, error="No HTML content received")

            # Validate string length
            html_content = ToolValidator.validate_string_length(
                html_content, max_length=1000000
            )

            result_data = {
                "html_content": html_content,
                "page_url": getattr(response, "page_url", None),
                "page_title": getattr(response, "page_title", None),
                "content_size": len(html_content),
                "snapshot_options": {
                    "full_page": request.full_page,
                    "wait_for": request.wait_for,
                    "wait_timeout": request.wait_timeout,
                },
            }

            return ToolResult(success=True, data=result_data)

        except ValidationError:
            raise
        except Exception as e:
            return ToolResult(success=False, error=f"Snapshot failed: {str(e)}")
