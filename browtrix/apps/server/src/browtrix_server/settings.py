from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to")
    log_level: str = Field(default="info", description="Logging level")

    # Connection Management
    max_connections: int = Field(default=10, description="Maximum browser connections")
    request_timeout: float = Field(
        default=30.0, description="Default request timeout in seconds"
    )
    enable_health_checks: bool = Field(
        default=True, description="Enable health check endpoints"
    )

    # Health Monitoring
    max_idle_time: float = Field(
        default=1800.0,
        description="Maximum idle time before connection is considered stale (seconds)",
    )
    health_check_interval: float = Field(
        default=60.0, description="Health check interval in seconds"
    )

    # Tool Configuration
    snapshot_default_timeout: int = Field(
        default=10, description="Default snapshot wait timeout in seconds"
    )
    snapshot_max_timeout: int = Field(
        default=60, description="Maximum snapshot wait timeout in seconds"
    )
    alert_default_timeout: int = Field(
        default=60, description="Default alert timeout in seconds"
    )
    alert_max_timeout: int = Field(
        default=300, description="Maximum alert timeout in seconds"
    )

    # MCP Configuration
    mcp_server_name: str = Field(
        default="browtrix-server", description="MCP server name"
    )
    mcp_server_version: str = Field(default="1.0.0", description="MCP server version")
    mcp_transport: str = Field(
        default="sse", description="MCP transport type (http, streamable-http, sse)"
    )

    # Feature Flags
    enable_metrics: bool = Field(default=False, description="Enable metrics collection")
    enable_cors: bool = Field(default=True, description="Enable CORS headers")
    debug_mode: bool = Field(default=False, description="Enable debug mode")


settings = Settings()
