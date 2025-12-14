"""Logging configuration."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
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

    # Add RotatingFileHandler
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/kasparro.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("kasparro")
    logger.setLevel(log_level.upper())
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger


logger = setup_logging()
