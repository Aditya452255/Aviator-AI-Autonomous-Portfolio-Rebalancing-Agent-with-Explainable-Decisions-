"""Unit tests for utilities, exceptions, and allocation models."""

import pytest
import numpy as np
from src.core.exceptions import AviatorAIError, ValidationError, ConfigurationError
from src.core.utils import Timer, normalize_weights, ensure_positive_definite
from src.models.allocation import TargetAllocation, CurrentAllocation


def test_custom_exceptions() -> None:
    """Test string representation of custom exceptions."""
    err = AviatorAIError("Test error", details={"key": "val"})
    assert "Test error" in str(err)
    assert "key" in str(err)

    cfg_err = ConfigurationError("Config issue")
    assert "Config issue" in str(cfg_err)


def test_timer_context() -> None:
    """Test Timer context manager execution metrics."""
    with Timer("Test Op") as metrics:
        a = 1 + 1
    assert "elapsed_seconds" in metrics
    assert metrics["operation"] == "Test Op"


def test_normalize_weights() -> None:
    """Test weight dictionary normalization."""
    raw = {"a": 2.0, "b": 3.0, "c": 5.0}
    norm = normalize_weights(raw)
    assert norm["a"] == 0.2
    assert norm["b"] == 0.3
    assert norm["c"] == 0.5

    with pytest.raises(ValueError):
        normalize_weights({"a": 0.0, "b": 0.0})


def test_ensure_positive_definite() -> None:
    """Test converting non-positive definite matrix to positive definite."""
    mat = np.array([[1.0, 2.0], [2.0, 1.0]])
    pos_def = ensure_positive_definite(mat)
    eigvals = np.linalg.eigvals(pos_def)
    assert (eigvals > 0).all()


def test_allocation_models_validation() -> None:
    """Test TargetAllocation and CurrentAllocation sum validation."""
    ta = TargetAllocation(equity=0.5, fixed_income=0.3, alternatives=0.1, cash=0.1)
    assert ta.equity == 0.5

    with pytest.raises(ValueError):
        TargetAllocation(equity=0.5, fixed_income=0.5, alternatives=0.5, cash=0.5)

    ca = CurrentAllocation(equity=0.4, fixed_income=0.4, alternatives=0.1, cash=0.1)
    assert ca.equity == 0.4

    with pytest.raises(ValueError):
        CurrentAllocation(equity=0.1, fixed_income=0.1, alternatives=0.1, cash=0.1)
