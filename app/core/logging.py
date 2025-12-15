"""Logging configuration with container-aware log handling."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return application logger.
    
    In container environments (detected via /.dockerenv or KUBERNETES_SERVICE_HOST),
    logs go to stdout only for proper log aggregation by orchestrators.
    In local development, logs also go to rotating file.
    """
    log_level = level or settings.log_level

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Always add stdout handler for container log aggregation
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger("kasparro")
    logger.setLevel(log_level.upper())
    logger.addHandler(stdout_handler)

    # Detect container environment
    is_container = (
        os.path.exists("/.dockerenv") or
        os.getenv("KUBERNETES_SERVICE_HOST") is not None or
        os.getenv("CONTAINER") is not None
    )

    # Only add file handler in non-container environments
    if not is_container:
        log_dir = os.getenv("LOG_DIR", "logs")
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = RotatingFileHandler(
                filename=f"{log_dir}/kasparro.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If we can't create log file, continue with stdout only
            logger.warning(f"Could not create file logger: {e}. Using stdout only.")

    logger.propagate = False

    return logger


logger = setup_logging()
