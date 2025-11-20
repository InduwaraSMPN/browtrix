"""
confirmation alert tool.
"""

from typing import Annotated, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import ConfirmationRequest
from ..connection.errors import BrowserConnectionError, ValidationError


class AlertOptions(BaseModel):
    """alert options with validation."""

    message: Annotated[str, Field(description="Alert message to display")]
    title: Annotated[str, Field(description="Alert title", default="Confirmation")] = (
        "Confirmation"
    )
    timeout: Annotated[int, Field(description="Timeout in seconds", ge=5, le=300)] = 60
    confirm_text: Annotated[
        str, Field(description="Text for confirm button", default="Yes")
    ] = "Yes"
    cancel_text: Annotated[
        str, Field(description="Text for cancel button", default="No")
    ] = "No"

    def validate_options(self):
        """Validate alert options."""
        ToolValidator.validate_required_field(self.message, "message")
        if len(self.message) > 1000:
            raise ValidationError(
                "message", self.message, "Message too long (max 1000 chars)"
            )
        return True


class AlertTool(BaseBrowtrixTool):
    """confirmation alert tool."""

    def __init__(self):
        super().__init__(
            name="confirmation-alert",
            description=" confirmation alert tool with configurable options",
        )
        self._connection_manager: Optional[Any] = None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute  alert with options."""
        try:
            # Get options from kwargs
            options = kwargs.get("options")
            if options:
                options.validate_options()
            else:
                # Default for backward compatibility
                message = kwargs.get("message", "")
                if not message:
                    return ToolResult(success=False, error="Message is required")
                options = AlertOptions(message=message)
                options.validate_options()

            # Create request
            request = ConfirmationRequest(
                message=options.message, title=options.title, timeout=options.timeout
            )

            # Get connection manager
            connection_manager = getattr(self, "_connection_manager", None)
            if not connection_manager:
                raise BrowserConnectionError("Connection manager not available")

            # Send request and get response
            response = await connection_manager.send_request(request)

            if not response.success:
                return ToolResult(success=False, error=response.error)

            # Extract result
            approved = getattr(response, "approved", False)
            selection_time = getattr(response, "selection_time_ms", None)

            result_data = {
                "approved": approved,
                "selection_time_ms": selection_time,
                "alert_options": {"title": options.title, "timeout": options.timeout},
            }

            return ToolResult(success=True, data=result_data)

        except ValidationError:
            raise
        except Exception as e:
            return ToolResult(success=False, error=f"Alert failed: {str(e)}")
