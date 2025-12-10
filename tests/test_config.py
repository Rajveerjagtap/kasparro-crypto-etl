"""Tests for configuration settings."""

import pytest
from app.core.config import Settings, get_settings


class TestSettings:
    """Test configuration settings."""

    def test_default_values(self):
        settings = Settings()
        assert settings.app_name == "Kasparro"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.batch_size == 100

    def test_db_pool_defaults(self):
        settings = Settings()
        assert settings.db_pool_size == 10
        assert settings.db_max_overflow == 20

    def test_cached_settings(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
