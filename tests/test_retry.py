"""Unit tests for RetryManager and FallbackManager."""

import pytest
from src.reliability.fallback_manager import FallbackManager
from src.reliability.retry_manager import RetryManager


def test_retry_manager_success_and_failure() -> None:
    """Test retry manager retrying failed calls up to max attempts."""
    retry = RetryManager(max_attempts=2, initial_delay=0.01)

    attempts = 0

    def faulty_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("Transient error")
        return "SUCCESS"

    res = retry.execute_with_retry(faulty_func)
    assert res == "SUCCESS"
    assert attempts == 2


def test_fallback_manager() -> None:
    """Test fallback manager falling back to backup function on primary error."""
    fallback = FallbackManager()

    def primary() -> str:
        raise ValueError("Primary solver crashed")

    def backup() -> str:
        return "FALLBACK_SUCCESS"

    res = fallback.execute_with_fallback(primary, backup)
    assert res == "FALLBACK_SUCCESS"
