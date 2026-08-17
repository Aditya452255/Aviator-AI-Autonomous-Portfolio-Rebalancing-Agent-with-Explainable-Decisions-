"""Security Audit Logger recording security events and authentication attempts."""

from datetime import datetime
from typing import Any, Dict, List
from src.core.logger import get_logger

logger = get_logger(__name__)


class SecurityAuditLogger:
    """Enterprise Security Audit Logger."""

    def __init__(self) -> None:
        self.security_logs: List[Dict[str, Any]] = []

    def log_security_event(self, event_type: str, user_id: str, status: str, details: str = "") -> None:
        """Record a security audit log event.

        Args:
            event_type: AUTHENTICATION, AUTHORIZATION, ACCESS, ENCRYPTION.
            user_id: User or actor ID.
            status: SUCCESS or FAILURE.
            details: Contextual details.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "status": status,
            "details": details,
        }
        self.security_logs.append(entry)
        logger.info(f"[SECURITY AUDIT] {event_type} | User: {user_id} | Status: {status} | {details}")
