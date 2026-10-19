
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized, validated application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DATAPILOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DataPilot"
    environment: str = "development"
    log_level: str = "INFO"

    # Credentials stay masked when represented as a SecretStr.
    groq_api_key: SecretStr | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    # PostgreSQL connection URL; keep it secret.
    postgres_url: SecretStr | None = None

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once and reuse them across the application."""
    return Settings()

