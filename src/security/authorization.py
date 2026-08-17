"""Authorization Manager checking role permissions for platform actions."""

from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.security.rbac import Role, UserSession

logger = get_logger(__name__)


class AuthorizationManager:
    """Enterprise Authorization Manager checking role permissions."""

    def authorize_action(self, session: UserSession, required_role: Role) -> bool:
        """Verify user session has required role for action.

        Args:
            session: Active UserSession.
            required_role: Minimum required Role.

        Returns:
            True if authorized.

        Raises:
            ValidationError: If unauthorized.
        """
        if session.role == Role.ADMIN:
            return True

        if session.role == required_role:
            return True

        logger.warning(f"Unauthorized action attempt by user [{session.user_id}] with role {session.role.value}.")
        raise ValidationError(f"Unauthorized: Role {session.role.value} cannot execute action requiring {required_role.value}.")
