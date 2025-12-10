"""Logging configuration."""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure and return application logger."""
    log_level = level or settings.log_level

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("kasparro")
    logger.setLevel(log_level.upper())
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()
