"""Unit tests for CircuitBreaker state transitions."""

import pytest
from src.core.exceptions import AviatorAIError
from src.reliability.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_tripping() -> None:
    """Test CircuitBreaker tripping to OPEN state after failure threshold reached."""
    cb = CircuitBreaker(name="TestBreaker", failure_threshold=2, recovery_timeout_seconds=0.1)

    assert cb.state == CircuitState.CLOSED

    def failing_func() -> None:
        raise ValueError("Simulated service failure")

    # Attempt 1 -> Failure
    with pytest.raises(ValueError):
        cb.execute(failing_func)
    assert cb.state == CircuitState.CLOSED

    # Attempt 2 -> Failure -> Trip to OPEN
    with pytest.raises(ValueError):
        cb.execute(failing_func)
    assert cb.state == CircuitState.OPEN

    # Attempt 3 -> Circuit OPEN -> AviatorAIError
    with pytest.raises(AviatorAIError, match="is OPEN"):
        cb.execute(failing_func)
