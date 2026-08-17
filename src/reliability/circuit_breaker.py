"""Circuit Breaker state machine preventing cascading system failures."""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional
from src.core.constants import StrEnum
from src.core.exceptions import AviatorAIError
from src.core.logger import get_logger

logger = get_logger(__name__)


class CircuitState(StrEnum):
    """Circuit Breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Enterprise Circuit Breaker state machine."""

    def __init__(
        self,
        name: str = "DefaultCircuitBreaker",
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a target callable within Circuit Breaker protection.

        Args:
            func: Target callable function.
            *args: Position arguments.
            **kwargs: Keyword arguments.

        Returns:
            Callable return value.

        Raises:
            AviatorAIError: If circuit is OPEN.
        """
        now = datetime.now()

        if self.state == CircuitState.OPEN:
            if self.last_failure_time and (now - self.last_failure_time) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"CircuitBreaker [{self.name}] transitioning to HALF_OPEN")
            else:
                logger.warning(f"CircuitBreaker [{self.name}] is OPEN. Fast failing request.")
                raise AviatorAIError(f"Circuit Breaker [{self.name}] is OPEN. Execution blocked.")

        try:
            res = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.reset()
            return res
        except Exception as exc:
            self._record_failure(now)
            raise exc

    def _record_failure(self, now: datetime) -> None:
        self.failure_count += 1
        self.last_failure_time = now

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.critical(
                f"CircuitBreaker [{self.name}] TRIP TO OPEN! "
                f"Failure count ({self.failure_count}) reached threshold ({self.failure_threshold})."
            )

    def reset(self) -> None:
        """Reset Circuit Breaker to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        logger.info(f"CircuitBreaker [{self.name}] reset to CLOSED state.")
