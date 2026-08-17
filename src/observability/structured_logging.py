"""Structured JSON Logging module with correlation ID tracking."""

import json
from typing import Any, Dict
from src.core.logger import get_logger

logger = get_logger(__name__)


class StructuredLogger:
    """Enterprise Structured Logger formatting logs as JSON payloads."""

    def log_json(self, level: str, message: str, correlation_id: str, payload: Dict[str, Any]) -> None:
        """Log structured JSON record.

        Args:
            level: INFO, WARNING, ERROR, CRITICAL.
            message: Message string.
            correlation_id: Request correlation ID.
            payload: Payload dictionary.
        """
        record = {
            "message": message,
            "correlation_id": correlation_id,
            "payload": payload,
        }
        json_str = json.dumps(record)

        if level.upper() == "ERROR":
            logger.error(json_str)
        elif level.upper() == "WARNING":
            logger.warning(json_str)
        else:
            logger.info(json_str)
