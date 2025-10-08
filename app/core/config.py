import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

from sqlmodel import Field


class Settings(BaseSettings):
    # App Settings
    app_name: str = "FastAPI Auth Backend"
    version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    # Database - PostgreSQL
    database_url: Optional[str] = None

    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:3000/auth/google/callback"

    # OpenAI/Gemini
    gemini_api_key: Optional[str] = None
    base_url: str = "https://gemini.googleapis.com/v1/"
    model: str = "gemini-2.5-flash"

    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]


    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False


settings = Settings()
