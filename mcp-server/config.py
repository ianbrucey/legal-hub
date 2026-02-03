"""
Configuration module for Legal Intelligence MCP Hub.

Loads environment variables and provides typed configuration objects.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from mcp-server directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class ServerConfig(BaseModel):
    """MCP Server configuration."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")


class S3Config(BaseModel):
    """AWS S3 configuration for report uploads."""
    access_key_id: str | None = Field(default=None)
    secret_access_key: str | None = Field(default=None)
    region: str = Field(default="us-east-1")
    default_bucket: str = Field(default="legal-research-reports")


class CourtListenerConfig(BaseModel):
    """Court Listener API configuration."""
    api_key: str | None = Field(default=None)
    base_url: str = Field(default="https://www.courtlistener.com/api/rest/v4")
    timeout: float = Field(default=30.0)


class GeminiConfig(BaseModel):
    """Gemini configuration for CLI and File Search."""
    api_key: str | None = Field(default=None)
    cli_path: str = Field(default="gemini")


class Config(BaseModel):
    """Main configuration container."""
    server: ServerConfig
    s3: S3Config
    court_listener: CourtListenerConfig
    gemini: GeminiConfig


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        server=ServerConfig(
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        ),
        s3=S3Config(
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            default_bucket=os.getenv("S3_DEFAULT_BUCKET", "legal-research-reports"),
        ),
        court_listener=CourtListenerConfig(
            api_key=os.getenv("COURTLISTENER_API_KEY"),
            base_url=os.getenv("COURTLISTENER_BASE_URL", "https://www.courtlistener.com/api/rest/v4"),
            timeout=float(os.getenv("COURTLISTENER_TIMEOUT", "30.0")),
        ),
        gemini=GeminiConfig(
            api_key=os.getenv("GOOGLE_API_KEY"),
            cli_path=os.getenv("GEMINI_CLI_PATH", "gemini"),
        ),
    )


# Singleton config instance
config = load_config()

