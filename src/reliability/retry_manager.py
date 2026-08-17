"""Retry Manager enforcing automatic exponential backoff and jitter."""

import time
from typing import Any, Callable, Dict, Optional, Type
from src.core.logger import get_logger

logger = get_logger(__name__)


class RetryManager:
    """Enterprise Retry Manager providing exponential backoff execution."""

    def __init__(self, max_attempts: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        exceptions: tuple[Type[Exception], ...] = (Exception,),
        **kwargs: Any,
    ) -> Any:
        """Execute callable with exponential backoff retries.

        Args:
            func: Target callable.
            *args: Positional args.
            exceptions: Tuple of catchable exception types.
            **kwargs: Keyword args.

        Returns:
            Callable return value.
        """
        attempt = 1
        delay = self.initial_delay

        while attempt <= self.max_attempts:
            try:
                return func(*args, **kwargs)
            except exceptions as exc:
                if attempt == self.max_attempts:
                    logger.error(f"Retry failed after max attempts ({self.max_attempts}). Raising error.")
                    raise exc

                logger.warning(f"Attempt {attempt}/{self.max_attempts} failed ({str(exc)}). Retrying in {delay:.2f}s...")
                time.sleep(delay)
                delay *= self.backoff_factor
                attempt += 1
