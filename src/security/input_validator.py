"""Input Validator sanitizing and validating request payloads."""

from typing import Any, Dict
from src.core.exceptions import ValidationError


class InputValidator:
    """Enterprise Input Validator sanitizing payload parameters."""

    def sanitize_portfolio_id(self, portfolio_id: str) -> str:
        """Sanitize portfolio ID input string.

        Args:
            portfolio_id: Raw string input.

        Returns:
            Sanitized string.

        Raises:
            ValidationError: If malformed.
        """
        clean = portfolio_id.strip()
        if not clean or len(clean) > 50 or ";" in clean or "--" in clean:
            raise ValidationError(f"Invalid portfolio ID payload string: {portfolio_id}")
        return clean
