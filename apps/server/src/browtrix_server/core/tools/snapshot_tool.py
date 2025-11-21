"""
snapshot tool with  features.
"""

from typing import Annotated, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import SnapshotRequest
from ..connection.errors import BrowserConnectionError, ValidationError
from ...settings import settings


class SnapshotOptions(BaseModel):
    """Snapshot options with validation for capturing browser page HTML content."""

    wait_for: Annotated[
        Optional[str],
        Field(
            description="CSS selector to wait for before capturing the snapshot. "
            "The tool will wait for this element to appear in the DOM before proceeding. "
            "Examples: '#content', '.data-loaded', '[data-ready=\"true\"]'. "
            "If None, capture proceeds immediately."
        ),
    ] = None
    full_page: Annotated[
        bool,
        Field(
            description="Whether to capture the full page including content below the fold (true) "
            "or only the visible viewport area (false). Full page capture is recommended for "
            "complete content analysis, while viewport capture is faster."
        ),
    ] = True
    wait_timeout: Annotated[
        int,
        Field(
            description="Maximum time in seconds to wait for the wait_for element to appear. "
            "Range: 1-60 seconds. If the element doesn't appear within this time, "
            "the capture proceeds anyway. Increase for slow-loading pages.",
            ge=1,
            le=settings.snapshot_max_timeout,
        ),
    ] = settings.snapshot_default_timeout
    quality: Annotated[
        int,
        Field(
            description="Reserved for future screenshot functionality. Quality level from 1 (lowest) "
            "to 100 (highest). Currently has no effect on HTML snapshots.",
            ge=1,
            le=100,
        ),
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
            description="""Captures a complete HTML snapshot of the current browser page with advanced rendering options.

This tool provides high-fidelity capture of web page content, allowing you to wait for dynamic content to load before capturing. It returns the full HTML DOM structure along with metadata about the captured page.

Use Cases:
- Capturing dynamically-loaded content after AJAX/fetch requests complete
- Extracting full page HTML for analysis or archival
- Taking snapshots after specific elements render (e.g., loading spinners disappear)
- Monitoring page state changes over time

Capture Behavior:
1. Optionally waits for a specified CSS selector to appear before capturing
2. Captures either the full page (including content below the fold) or just the visible viewport
3. Returns the complete HTML DOM as a string with associated metadata
4. Includes timing and size information for performance monitoring

Best Practices:
- Use `wait_for` parameter when targeting pages with dynamic content (React, Vue, Angular apps)
- Set `full_page=false` for faster captures when only viewport content is needed
- Increase `wait_timeout` for slow-loading pages or complex SPAs
- Monitor `content_size` to track page complexity and potential performance issues

Parameters:
- wait_for: CSS selector to wait for before capturing (e.g., '#content', '.data-loaded'). The tool will wait up to `wait_timeout` seconds for this element to appear in the DOM.
- full_page: Capture the entire page including content below the fold (default: true). Set to false to capture only the visible viewport area.
- wait_timeout: Maximum time in seconds to wait for the `wait_for` element (range: 1-60, default: 10). If the element doesn't appear within this time, the capture will proceed anyway.
- quality: Reserved for future screenshot functionality (range: 1-100, default: 100).

Returns:
A structured result containing:
- html_content: Complete HTML DOM as a string
- page_url: Current URL of the captured page
- page_title: Page title from the <title> tag
- content_size: Size of the HTML content in bytes
- snapshot_options: Echo of the options used for this capture

Example Usage:
Wait for a data table to load before capturing:
  wait_for: 'table.data-loaded'
  full_page: true
  wait_timeout: 15

Capture just the visible area immediately:
  wait_for: null
  full_page: false
  wait_timeout: 10""",
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
