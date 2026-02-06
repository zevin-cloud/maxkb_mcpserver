"""Configuration management for MaxKB MCP Server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MaxKB API Configuration
    maxkb_base_url: str = "http://localhost:8080"
    maxkb_api_key: str = ""

    # MCP Server Configuration
    mcp_server_name: str = "maxkb-knowledge-base"
    mcp_server_version: str = "0.1.0"

    # Transport Configuration
    mcp_transport: str = "stdio"  # Options: stdio, sse
    mcp_port: int = 3000  # Port for SSE transport
    mcp_host: str = "127.0.0.1"  # Host for SSE transport

    # Workspace configuration
    maxkb_workspace_id: str = "default"

    @property
    def maxkb_api_base(self) -> str:
        """Get MaxKB API base URL."""
        base = self.maxkb_base_url.rstrip("/")
        return f"{base}/admin/api"


# Global settings instance
settings = Settings()
