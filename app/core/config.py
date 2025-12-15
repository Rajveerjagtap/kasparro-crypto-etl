"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database - supports both DATABASE_URL and DB_URL
    database_url: Optional[str] = None
    db_url: Optional[str] = Field(default=None, validate_default=False)
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # API Keys
    coinpaprika_key: Optional[str] = None
    coingecko_key: Optional[str] = None

    # Application
    app_name: str = "Kasparro"
    debug: bool = False
    log_level: str = "INFO"

    # ETL
    batch_size: int = 100
    csv_data_path: str = "data/crypto_data.csv"

    @model_validator(mode="after")
    def set_db_url(self):
        """Prefer DATABASE_URL over DB_URL if set."""
        import os

        if self.database_url:
            self.db_url = self.database_url
        elif not self.db_url:
            # Fallback to env var directly if pydantic missed it
            self.db_url = os.getenv("DATABASE_URL")

        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
