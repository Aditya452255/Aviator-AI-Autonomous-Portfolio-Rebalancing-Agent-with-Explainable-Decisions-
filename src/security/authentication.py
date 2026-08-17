"""Authentication Manager verifying user credentials and issuing sessions."""

from typing import Optional
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.security.rbac import Role, UserSession

logger = get_logger(__name__)


class AuthenticationManager:
    """Enterprise Authentication Manager."""

    def authenticate_user(self, username: str, password: str) -> UserSession:
        """Authenticate user credentials and issue active session.

        Args:
            username: Username string.
            password: Password string.

        Returns:
            UserSession object.

        Raises:
            ValidationError: If authentication fails.
        """
        if username in ("admin", "advisor1", "compliance1") and password == "AviatorAI2026!":
            role = Role.ADMIN if username == "admin" else (Role.ADVISOR if username == "advisor1" else Role.COMPLIANCE_OFFICER)
            session = UserSession(user_id=username, role=role, token=f"TOKEN_{username}_SECURE")
            logger.info(f"User [{username}] authenticated successfully as {role.value}.")
            return session

        raise ValidationError("Authentication failed: Invalid credentials.")
