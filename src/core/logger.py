"""Enterprise logging setup utilizing Loguru for Aviator AI."""

import os
import sys
from typing import Any, Dict
from loguru import logger


def setup_logger(
    log_level: str = "INFO",
    log_file: str = "logs/application.log",
    rotation: str = "10 MB",
    retention: str = "10 days",
    console_enabled: bool = True,
) -> None:
    """Configure enterprise loggers for console and file destinations.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Target relative or absolute file path for file log sink.
        rotation: Log rotation rule (e.g. '10 MB' or '1 day').
        retention: Log retention policy (e.g. '10 days').
        console_enabled: Whether stdout logging is active.
    """
    logger.remove()  # Clear standard default handlers

    # Console Handler
    if console_enabled:
        logger.add(
            sys.stdout,
            level=log_level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

    # File Handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logger.add(
            log_file,
            level="DEBUG",  # Capture DEBUG and above in file
            rotation=rotation,
            retention=retention,
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,  # Thread safe async logging
        )


def get_logger(module_name: str) -> Any:
    """Return logger bound with module context.

    Args:
        module_name: Module or class identifier.

    Returns:
        Loguru logger bound with context.
    """
    return logger.bind(module=module_name)
