import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

from sqlmodel import Field


class Settings(BaseSettings):
    # App Settings
    app_name: str = "FastAPI Agentic Backend"
    version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    # Database - PostgreSQL
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # JWT
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production", alias="JWT_SECRET"
    )
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Google OAuth
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(
        default=None, alias="GOOGLE_CLIENT_SECRET"
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8080/api/v1/oauth/google/callback",
        alias="GOOGLE_REDIRECT_URI",
    )

    # AI AGENT CONFIGURATION
    api_key: str = Field(default="", alias="API_KEY")
    api_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        alias="API_BASE_URL",
    )
    model: str = Field(default="gemini-2.5-flash", alias="MODEL")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080", alias="ALLOWED_ORIGINS"
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
