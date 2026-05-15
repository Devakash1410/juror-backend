"""
Configuration and environment settings for JUROR backend.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # FastAPI
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Verification APIs
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    wolfram_app_id: str = os.getenv("WOLFRAM_APP_ID", "")
    wikipedia_timeout: int = int(os.getenv("WIKIPEDIA_TIMEOUT", "10"))

    # Agent Configuration
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT", "30"))
    generator_temperature: float = float(os.getenv("GENERATOR_TEMPERATURE", "0.7"))
    jury_temperature: float = float(os.getenv("JURY_TEMPERATURE", "0.5"))
    corrector_temperature: float = float(os.getenv("CORRECTOR_TEMPERATURE", "0.6"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "2"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
