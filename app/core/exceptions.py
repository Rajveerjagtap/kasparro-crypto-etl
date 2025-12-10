"""Custom exceptions for the application."""

from typing import Any, Optional


class KasparroException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(KasparroException):
    """Database operation failures."""

    pass


class ExtractionException(KasparroException):
    """Data extraction failures from external sources."""

    pass


class TransformationException(KasparroException):
    """Data transformation/normalization failures."""

    pass


class ValidationException(KasparroException):
    """Data validation failures."""

    pass


class ConfigurationException(KasparroException):
    """Configuration/environment setup failures."""

    pass


class APIException(KasparroException):
    """External API call failures."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.status_code = status_code
        super().__init__(message, details)
