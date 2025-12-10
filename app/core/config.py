"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kasparro"
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


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
