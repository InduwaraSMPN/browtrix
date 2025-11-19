"""
Base classes for Browtrix tools with  error handling and type safety.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
import asyncio
import structlog
from ..connection.errors import BrowserConnectionError


logger = structlog.get_logger(__name__)


class ToolResult(BaseModel):
    """Standardized tool result with status and metadata."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseBrowtrixTool(ABC):
    """Base class for all Browtrix tools with common functionality."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logger.bind(tool=name)

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with provided parameters."""
        pass

    async def safe_execute(self, **kwargs) -> ToolResult:
        """Execute tool with comprehensive error handling."""
        try:
            self.logger.info("Tool execution started", params=kwargs)
            result = await self.execute(**kwargs)
            self.logger.info("Tool execution completed", success=result.success)
            return result
        except asyncio.TimeoutError as e:
            error_msg = f"Tool execution timed out: {str(e)}"
            self.logger.error("Tool execution timeout", error=error_msg)
            return ToolResult(success=False, error=error_msg)
        except BrowserConnectionError as e:
            error_msg = f"Browser connection error: {str(e)}"
            self.logger.error("Browser connection error", error=error_msg)
            return ToolResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in tool execution: {str(e)}"
            self.logger.error("Unexpected tool error", error=error_msg, exc_info=True)
            return ToolResult(success=False, error=error_msg)


class ToolValidator:
    """Validation utilities for tool parameters."""

    @staticmethod
    def validate_required_field(value: Any, field_name: str) -> None:
        """Validate that a required field is present and not None."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Required field '{field_name}' is missing or empty")

    @staticmethod
    def validate_timeout(timeout: float) -> float:
        """Validate and normalize timeout value."""
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        return min(timeout, 300.0)  # Cap at 5 minutes

    @staticmethod
    def validate_string_length(value: str, max_length: int = 10000) -> str:
        """Validate string length and truncate if necessary."""
        if len(value) > max_length:
            truncated = value[:max_length] + "..."
            logger.warning(
                "String truncated",
                original_length=len(value),
                truncated_length=max_length,
            )
            return truncated
        return value
