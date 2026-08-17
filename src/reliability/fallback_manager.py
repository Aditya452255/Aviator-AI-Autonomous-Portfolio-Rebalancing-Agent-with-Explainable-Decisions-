"""Fallback Manager providing graceful degradation and fallback responses."""

from typing import Any, Callable, Dict, Optional
from src.core.logger import get_logger

logger = get_logger(__name__)


class FallbackManager:
    """Enterprise Fallback Manager executing fallbacks on failure."""

    def execute_with_fallback(
        self,
        primary_func: Callable[..., Any],
        fallback_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute primary function, falling back to secondary function if primary fails.

        Args:
            primary_func: Primary function.
            fallback_func: Fallback function.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            Output from primary or fallback function.
        """
        try:
            return primary_func(*args, **kwargs)
        except Exception as exc:
            logger.warning(f"Primary operation failed ({str(exc)}). Invoking fallback execution.")
            return fallback_func(*args, **kwargs)
