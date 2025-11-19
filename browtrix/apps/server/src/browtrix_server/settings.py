from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env"], extra="ignore")

    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to")
    log_level: str = Field(default="info", description="Logging level")


settings = Settings()
