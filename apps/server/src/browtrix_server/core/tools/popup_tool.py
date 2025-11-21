"""
question popup tool.
"""

from typing import Annotated, Literal, Optional, Any
from pydantic import BaseModel, Field
from ..tools.base import BaseBrowtrixTool, ToolResult, ToolValidator
from ..types.requests import InputRequest
from ..connection.errors import BrowserConnectionError, ValidationError


class PopupOptions(BaseModel):
    """Question popup options with validation for collecting user input through modal dialogs."""

    question: Annotated[
        str,
        Field(
            description="The question or prompt to display to the user. Should clearly indicate "
            "what input is expected and in what format. Maximum length: 1000 characters. "
            "Example: 'Enter your email address to receive notifications'"
        ),
    ]
    title: Annotated[
        str,
        Field(
            description="The dialog title/header text. Use this to categorize the input type. "
            "Examples: 'API Configuration', 'Enter Credentials', 'Provide Details'. "
            "Default: 'Input Required'",
            default="Input Required",
        ),
    ] = "Input Required"
    input_type: Annotated[
        Literal["text", "email", "password", "number"],
        Field(
            description="HTML input type affecting keyboard and browser behavior. "
            "Options: 'text' (general input), 'email' (email-specific with @ key), "
            "'password' (masked input), 'number' (numeric with spinners). "
            "Default: 'text'"
        ),
    ] = "text"
    placeholder: Annotated[
        str,
        Field(
            description="Example text shown in the empty input field to demonstrate expected format. "
            "Examples: 'user@example.com', 'https://api.example.com', '42'. "
            "Default: empty string"
        ),
    ] = ""
    validation: Annotated[
        Literal["any", "email", "number", "url", "regex"],
        Field(
            description="Validation rule applied to user input. Options: 'any' (no validation), "
            "'email' (email format), 'number' (numeric only), 'url' (URL format), "
            "'regex' (custom pattern via validation_pattern). Default: 'any'"
        ),
    ] = "any"
    validation_pattern: Annotated[
        str,
        Field(
            description="Custom regex pattern used when validation is 'regex'. Must be a valid "
            "JavaScript-compatible regex pattern. Example: '^[A-Z]{2}\\d{4}$' for 'AB1234' format. "
            "Ignored if validation is not 'regex'. Default: empty string"
        ),
    ] = ""
    required: Annotated[
        bool,
        Field(
            description="Whether the input field must be filled before submission. If true, "
            "empty submissions are rejected and an error is returned. "
            "Set to false for optional fields. Default: true"
        ),
    ] = True
    timeout: Annotated[
        int,
        Field(
            description="Maximum time in seconds to wait for user input. After timeout, "
            "the dialog closes automatically and returns an error. Range: 5-300 seconds. "
            "Complex inputs or custom validation should have longer timeouts. Default: 60 seconds.",
            ge=5,
            le=300,
        ),
    ] = 60

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
            description="""Displays an interactive input modal in the active browser session to collect validated user input.

This tool creates a blocking modal dialog that prompts the user to provide textual or numeric input with optional validation. It supports various input types, validation patterns, and customization options. The dialog ensures data quality through client-side validation before returning the result.

Use Cases:
- Collecting user credentials (email, password) during authentication flows
- Gathering configuration parameters from users (API keys, URLs, numeric settings)
- Requesting data for form auto-filling or test data generation
- Implementing human-in-the-loop data entry for AI workflows
- Validating user-provided information with regex patterns
- Collecting feedback or notes during automation processes

Input Types & Validation:
- text: Free-form text input (default) - useful for names, descriptions, general input
- email: Email-specific input with browser hints - validates against email format
- password: Masked password input - characters are hidden for security
- number: Numeric-only input with browser spinners - restricts to numeric values

Validation Options:
- any: No specific validation (default) - accepts any input
- email: Validates email address format (user@domain.com)
- number: Ensures numeric input only
- url: Validates URL format (http://, https://)
- regex: Custom validation using `validation_pattern` parameter

Interaction Behavior:
1. Displays a modal overlay that blocks interaction with the underlying page
2. Presents a customizable question/prompt and title to the user
3. Provides an input field styled according to `input_type`
4. Validates input client-side based on `validation` rules
5. Shows validation errors inline if input doesn't meet requirements
6. Waits for valid submission or timeout, whichever occurs first
7. Returns the validated input value with timing metrics

Response Handling:
- If user submits valid input: Returns `value` with `validation_passed: true`
- If validation fails: Shows error and prompts user to correct input
- If `required: true` and user submits empty: Returns error
- If timeout is reached: Returns error with no value
- The `input_time_ms` metric tracks how long the user took to respond

Best Practices:
- Use clear, specific questions that tell the user exactly what format is expected
- Choose the appropriate `input_type` to trigger correct browser behaviors (keyboard, autocomplete)
- Set `required: true` for mandatory fields to prevent empty submissions
- Use `validation` to ensure data quality before processing
- For custom formats, use `validation: regex` with a descriptive error message in the question
- Set timeouts appropriate to the expected response time (complex inputs need longer timeouts)
- Use `placeholder` text to show example input formats

Parameters:
- question (required): The question or prompt to display to the user. Should clearly indicate what input is expected and in what format. Maximum length: 1000 characters.
- title: The dialog title/header text (default: "Input Required"). Use this to categorize the type of input being requested (e.g., "API Configuration", "Enter Credentials", "Provide Details").
- input_type: The HTML input type which affects keyboard and browser behavior (options: "text", "email", "password", "number"; default: "text"). This determines the input field styling and mobile keyboard layout.
- placeholder: Example text shown in the empty input field (default: ""). Use this to demonstrate the expected format (e.g., "user@example.com", "https://api.example.com").
- validation: The validation rule to apply to the input (options: "any", "email", "number", "url", "regex"; default: "any"). Client-side validation prevents submission of invalid data.
- validation_pattern: Custom regex pattern when `validation: regex` is used (default: ""). Example: "^[A-Z]{2}\\d{4}$" for format like "AB1234".
- required: Whether the input field must be filled (default: true). If true, empty submissions are rejected.
- timeout: Maximum time in seconds to wait for user input (range: 5-300, default: 60). After timeout, the dialog closes automatically and returns an error.

Returns:
A structured result containing:
- value: The user-provided input value as a string (empty string if timed out or cancelled)
- validation_passed: Boolean indicating whether the input passed validation rules
- input_time_ms: Time in milliseconds from dialog display until user submission (null if timed out)
- popup_options: Echo of the title, input_type, validation, and required settings used

Example Usage:
Collect email address:
  question: "Enter your email address to receive notifications"
  title: "Email Setup"
  input_type: "email"
  validation: "email"
  required: true
  timeout: 60

API key with custom validation:
  question: "Enter your API key (format: sk-xxxx-xxxxxxxxxxxx)"
  title: "API Configuration"
  input_type: "text"
  placeholder: "sk-proj-abc123def456"
  validation: "regex"
  validation_pattern: "^sk-[a-zA-Z0-9]+-[a-zA-Z0-9]+$"
  required: true
  timeout: 120

Optional numeric input:
  question: "How many retries would you like? (leave blank for default: 3)"
  title: "Retry Configuration"
  input_type: "number"
  validation: "number"
  required: false
  timeout: 30""",
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
