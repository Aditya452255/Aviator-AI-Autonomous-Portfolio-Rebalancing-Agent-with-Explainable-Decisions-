"""Secrets Manager handling secure environment variables and API keys."""

import os
from typing import Optional


class SecretsManager:
    """Enterprise Secrets Manager."""

    def get_secret(self, name: str, default: str = "DEFAULT_SECRET") -> str:
        """Fetch secret string from environment variable or default fallback.

        Args:
            name: Environment variable name.
            default: Default string fallback.

        Returns:
            Secret string value.
        """
        return os.getenv(name, default)
