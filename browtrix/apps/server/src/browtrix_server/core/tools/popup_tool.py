"""
question popup tool.
"""

from typing import Annotated, Literal, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import InputRequest
from ..connection.errors import BrowserConnectionError, ValidationError


class PopupOptions(BaseModel):
    """popup options with validation."""

    question: Annotated[str, Field(description="Question to display")]
    title: Annotated[
        str, Field(description="Popup title", default="Input Required")
    ] = "Input Required"
    input_type: Annotated[
        Literal["text", "email", "password", "number"],
        Field(description="Type of input field"),
    ] = "text"
    placeholder: Annotated[str, Field(description="Placeholder text")] = ""
    validation: Annotated[
        Literal["any", "email", "number", "url", "regex"],
        Field(description="Validation type"),
    ] = "any"
    validation_pattern: Annotated[str, Field(description="Custom regex pattern")] = ""
    required: Annotated[bool, Field(description="Whether input is required")] = True
    timeout: Annotated[int, Field(description="Timeout in seconds", ge=5, le=300)] = 60

    def validate_options(self):
        """Validate popup options."""
        ToolValidator.validate_required_field(self.question, "question")
        if len(self.question) > 1000:
            raise ValidationError(
                "question", self.question, "Question too long (max 1000 chars)"
            )
        return True


class PopupTool(BaseBrowtrixTool):
    """question popup tool."""

    def __init__(self):
        super().__init__(
            name="question-popup",
            description=" question popup tool with configurable options",
        )
        self._connection_manager: Optional[Any] = None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute  popup with options."""
        try:
            # Get options from kwargs
            options = kwargs.get("options")
            if options:
                options.validate_options()
            else:
                # Default for backward compatibility
                question = kwargs.get("question", "")
                if not question:
                    return ToolResult(success=False, error="Question is required")
                options = PopupOptions(question=question)
                options.validate_options()

            # Create request
            request = InputRequest(
                message=options.question,
                title=options.title,
                input_type=options.input_type,
                placeholder=options.placeholder,
                validation=options.validation,
                validation_pattern=options.validation_pattern
                if options.validation == "regex"
                else None,
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
            value = getattr(response, "value", "")
            validation_passed = getattr(response, "validation_passed", True)
            input_time = getattr(response, "input_time_ms", None)

            # Validate required field
            if options.required and not value:
                return ToolResult(success=False, error="Required field was not filled")

            result_data = {
                "value": value,
                "validation_passed": validation_passed,
                "input_time_ms": input_time,
                "popup_options": {
                    "title": options.title,
                    "input_type": options.input_type,
                    "validation": options.validation,
                    "required": options.required,
                },
            }

            return ToolResult(success=True, data=result_data)

        except ValidationError:
            raise
        except Exception as e:
            return ToolResult(success=False, error=f"Popup failed: {str(e)}")
