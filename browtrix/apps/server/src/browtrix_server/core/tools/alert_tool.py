"""
confirmation alert tool.
"""

from typing import Annotated, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import ConfirmationRequest
from ..connection.errors import BrowserConnectionError, ValidationError


class AlertOptions(BaseModel):
    """Confirmation alert options with validation for displaying modal dialogs."""

    message: Annotated[
        str,
        Field(
            description="The confirmation message to display to the user. Should clearly explain "
            "what action is being confirmed. Maximum length: 1000 characters. "
            "Example: 'Are you sure you want to delete these 42 files?'"
        ),
    ]
    title: Annotated[
        str,
        Field(
            description="The dialog title/header text. Use this to categorize the confirmation type. "
            "Examples: 'Delete Confirmation', 'Proceed with Action', 'Warning'. "
            "Default: 'Confirmation'",
            default="Confirmation",
        ),
    ] = "Confirmation"
    timeout: Annotated[
        int,
        Field(
            description="Maximum time in seconds to wait for user response. After timeout, "
            "the dialog closes automatically and returns approved: false. "
            "Range: 5-300 seconds. Longer messages should have longer timeouts. "
            "Default: 60 seconds.",
            ge=5,
            le=300,
        ),
    ] = 60
    confirm_text: Annotated[
        str,
        Field(
            description="Text displayed on the confirm/yes button. Customize for clarity. "
            "Examples: 'Yes', 'Confirm', 'Proceed', 'Delete'. Default: 'Yes'",
            default="Yes",
        ),
    ] = "Yes"
    cancel_text: Annotated[
        str,
        Field(
            description="Text displayed on the cancel/no button. Customize for clarity. "
            "Examples: 'No', 'Cancel', 'Abort', 'Keep'. Default: 'No'",
            default="No",
        ),
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
            description="""Displays a modal confirmation dialog in the active browser session requiring user interaction.

This tool creates a blocking modal dialog that prompts the user to confirm or cancel an action. It returns the user's choice along with timing metrics. The dialog will remain visible until the user responds or the timeout is reached.

Use Cases:
- Confirming destructive actions before execution (e.g., "Delete all items?")
- Requesting user approval before proceeding with a workflow step
- Implementing human-in-the-loop validation for AI-driven automation
- Gathering explicit consent for data operations
- Checkpoint verification in multi-step processes

Interaction Behavior:
1. Displays a modal overlay that blocks interaction with the underlying page
2. Presents a customizable message and title to the user
3. Provides two action buttons: confirm (default: "Yes") and cancel (default: "No")
4. Waits for user interaction or timeout, whichever occurs first
5. Returns the user's selection with timing information

Response Handling:
- If user clicks confirm button: Returns `approved: true` with interaction timing
- If user clicks cancel button: Returns `approved: false` with interaction timing
- If timeout is reached: Returns `approved: false` with error indication
- The `selection_time_ms` metric helps track user decision-making patterns

Best Practices:
- Use clear, concise messages that explain what the user is confirming
- Set appropriate timeouts based on message complexity (longer messages need more time)
- For critical actions, include the action consequence in the message
- Consider the user's context - don't interrupt time-sensitive workflows
- Use descriptive titles that categorize the type of confirmation needed

Parameters:
- message (required): The confirmation message to display to the user. Should be clear and specific about what action requires confirmation. Maximum length: 1000 characters.
- title: The dialog title/header text (default: "Confirmation"). Use this to categorize the type of confirmation (e.g., "Delete Confirmation", "Proceed with Action", "Warning").
- timeout: Maximum time in seconds to wait for user response (range: 5-300, default: 60). After timeout, the dialog closes automatically and returns `approved: false`.

Returns:
A structured result containing:
- approved: Boolean indicating whether the user confirmed (true) or cancelled/timed out (false)
- selection_time_ms: Time in milliseconds from dialog display until user interaction (null if timed out)
- alert_options: Echo of the title and timeout used for this confirmation

Example Usage:
Simple confirmation:
  message: "Are you sure you want to delete these 42 files?"
  title: "Delete Confirmation"
  timeout: 30

Critical action with extended timeout:
  message: "This will permanently remove all user data and cannot be undone. Continue?"
  title: "⚠️ Destructive Action"
  timeout: 120

Quick verification:
  message: "Proceed to next step?"
  title: "Continue"
  timeout: 15""",
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
