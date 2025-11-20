"""
Browtrix MCP Server with  features.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Annotated, Optional
from pydantic import Field
import structlog
import asyncio
import uvicorn
from datetime import datetime, timezone

# Imports
from .core import (
    ConnectionManager,
    ToolExecutionError,
)
from .core.tools import (
    SnapshotTool,
    AlertTool,
    PopupTool,
    SnapshotOptions,
    AlertOptions,
    PopupOptions,
)
from .settings import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default=settings.host, description="Server host")
    port: int = Field(default=settings.port, description="Server port")
    max_connections: int = Field(default=10, description="Max browser connections")
    request_timeout: float = Field(default=30.0, description="Default request timeout")
    enable_health_checks: bool = Field(
        default=True, description="Enable health check endpoints"
    )


class BrowtrixServer:
    """Browtrix MCP Server with  features."""

    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or ServerConfig()

        # Initialize  connection manager
        self.connection_manager = ConnectionManager(
            max_connections=self.config.max_connections,
            request_timeout=self.config.request_timeout,
        )

        # Initialize FastMCP
        self.mcp = FastMCP("browtrix-server")

        # Initialize FastAPI
        self.app = FastAPI(
            title="Browtrix MCP Server",
            description="Model Context Protocol server for browser automation",
            version="1.0.0",
            lifespan=self.lifespan,
        )

        # Setup tools
        self._setup_tools()

        # Setup routes
        self._setup_routes()

        # Setup WebSocket
        self._setup_websocket()

        # Background tasks
        self._shutdown_event = None

        logger.info(
            "Browtrix Server initialized",
            host=self.config.host,
            port=self.config.port,
            max_connections=self.config.max_connections,
        )

    def _setup_tools(self):
        """Setup MCP tools."""

        # HTML Snapshot Tool
        @self.mcp.tool
        async def browtrix_html_snapshot(
            wait_for: Annotated[
                Optional[str], Field(description="CSS selector to wait for")
            ] = None,
            full_page: Annotated[bool, Field(description="Capture full page")] = True,
            wait_timeout: Annotated[
                int, Field(description="Wait timeout", ge=1, le=60)
            ] = 10,
            quality: Annotated[
                int, Field(description="Quality (1-100)", ge=1, le=100)
            ] = 100,
        ) -> Annotated[str, "HTML content of the page"]:
            """HTML snapshot with configurable options."""
            try:
                snapshot_tool = SnapshotTool()
                snapshot_tool._connection_manager = self.connection_manager
                options = SnapshotOptions(
                    wait_for=wait_for,
                    full_page=full_page,
                    wait_timeout=wait_timeout,
                    quality=quality,
                )
                result = await snapshot_tool.safe_execute(options=options)

                if result.success:
                    return result.data["html_content"]
                else:
                    raise ToolExecutionError(
                        "browtrix_html_snapshot", result.error or "Unknown error"
                    )

            except Exception as e:
                logger.error("Snapshot tool failed", error=str(e), exc_info=True)
                raise ToolExecutionError("browtrix_html_snapshot", str(e))

        # Confirmation Alert Tool

        @self.mcp.tool
        async def browtrix_confirmation_alert(
            message: Annotated[str, Field(description="Alert message")],
            title: Annotated[str, Field(description="Alert title")] = "Confirmation",
            timeout: Annotated[
                int, Field(description="Timeout in seconds", ge=5, le=300)
            ] = 60,
        ) -> Annotated[bool, "True if user confirmed, False if cancelled"]:
            """Confirmation alert with configurable options."""
            try:
                alert_tool = AlertTool()
                alert_tool._connection_manager = self.connection_manager
                options = AlertOptions(message=message, title=title, timeout=timeout)
                result = await alert_tool.safe_execute(options=options)

                if result.success:
                    return result.data["approved"]
                else:
                    raise ToolExecutionError(
                        "browtrix_confirmation_alert", result.error or "Unknown error"
                    )

            except Exception as e:
                logger.error("Alert tool failed", error=str(e), exc_info=True)
                raise ToolExecutionError("browtrix_confirmation_alert", str(e))

        # Question Popup Tool
        popup_tool = PopupTool()

        @self.mcp.tool
        async def browtrix_question_popup(
            question: Annotated[str, Field(description="Question to ask")],
            title: Annotated[str, Field(description="Popup title")] = "Input Required",
            input_type: Annotated[str, Field(description="Input type")] = "text",
            validation: Annotated[str, Field(description="Validation type")] = "any",
        ) -> Annotated[str, "User input value"]:
            """Question popup with configurable options."""
            try:
                popup_tool._connection_manager = self.connection_manager
                # Validate and cast input types
                valid_input_types = ["text", "email", "password", "number"]
                valid_validation_types = ["any", "email", "number", "url", "regex"]

                input_type_valid = (
                    input_type if input_type in valid_input_types else "text"
                )
                validation_valid = (
                    validation if validation in valid_validation_types else "any"
                )

                options = PopupOptions(
                    question=question,
                    title=title,
                    input_type=input_type_valid,  # type: ignore
                    validation=validation_valid,  # type: ignore
                )
                result = await popup_tool.safe_execute(options=options)

                if result.success:
                    return result.data["value"]
                else:
                    raise ToolExecutionError(
                        "browtrix_question_popup",
                        str(result.error) if result.error else "Unknown error",
                    )

            except Exception as e:
                logger.error("Popup tool failed", error=str(e), exc_info=True)
                raise ToolExecutionError("browtrix_question_popup", str(e))

    def _setup_routes(self):
        """Setup HTTP routes."""

        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                health_status = self.connection_manager.get_health_status()
                return JSONResponse(
                    status_code=200 if health_status.status == "healthy" else 503,
                    content=health_status.model_dump(mode="json"),
                )
            except Exception as e:
                logger.error("Health check failed", error=str(e))
                raise HTTPException(status_code=503, detail="Service unhealthy")

        # Statistics endpoint
        @self.app.get("/stats")
        async def get_statistics():
            """Get server statistics."""
            try:
                stats = self.connection_manager.get_statistics()
                return JSONResponse(content=stats)
            except Exception as e:
                logger.error("Statistics endpoint failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))

        # Server info endpoint
        @self.app.get("/info")
        async def server_info():
            """Get server information."""
            return {
                "name": "Browtrix MCP Server",
                "version": "1.0.0",
                "description": "Model Context Protocol server for browser automation",
                "features": [
                    "HTML snapshots with configurable options",
                    "Configurable alerts and popups",
                    "Health monitoring",
                    "Connection pooling",
                    "Structured logging",
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _setup_websocket(self):
        """Setup WebSocket endpoint."""

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            connection_id = None
            try:
                # Accept connection
                connection_id = await self.connection_manager.connect(websocket)
                logger.info("WebSocket connected", connection_id=connection_id)

                # Start health monitoring for this connection
                await self.connection_manager.start_health_monitoring()

                # Handle messages
                while True:
                    data = await websocket.receive_text()
                    await self.connection_manager.handle_message(data, connection_id)

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected", connection_id=connection_id)
            except Exception as e:
                logger.error(
                    "WebSocket error",
                    connection_id=connection_id,
                    error=str(e),
                    exc_info=True,
                )
            finally:
                if connection_id:
                    self.connection_manager.disconnect(connection_id)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan."""
        logger.info("Starting Browtrix Server...")
        await self.connection_manager.start_health_monitoring()
        self._shutdown_event = asyncio.Event()

        yield

        logger.info("Shutting down Browtrix Server...")
        await self.connection_manager.stop_health_monitoring()
        if self._shutdown_event:
            self._shutdown_event.set()

    async def run(self):
        """Run the server."""

        # Mount MCP app
        try:
            mcp_app = self.mcp.http_app(transport="sse")
            self.app.mount("/mcp", mcp_app)
        except Exception as e:
            logger.error("Failed to mount MCP app", error=str(e))
            raise

        # Run server
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
            access_log=True,
        )

        server = uvicorn.Server(config)
        await server.serve()


# Global server instance
_server_instance: Optional[BrowtrixServer] = None


def get_global_server() -> BrowtrixServer:
    """Get or create global server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = BrowtrixServer()
    return _server_instance


# Global exports for FastMCP integration
app = get_global_server().app
mcp = get_global_server().mcp


async def main():
    """Main entry point."""
    server = get_global_server()
    await server.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
