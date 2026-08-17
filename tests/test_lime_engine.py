"""Unit tests for LIMEEngine."""

import pytest
from src.explainability.lime_engine import LIMEEngine
from src.explainability.surrogate_model import SurrogateModel


def test_lime_engine_explanations() -> None:
    """Test LIME tabular explanation generation for portfolio features."""
    surrogate = SurrogateModel()
    surrogate.fit_synthetic_baseline(num_samples=100)

    lime_engine = LIMEEngine(surrogate_model=surrogate)
    X_sample = surrogate.extract_features(portfolio_id="PORT_TEST", drift_score=0.070)

    lime_contribs = lime_engine.compute_lime_explanation(X_sample)

    assert isinstance(lime_contribs, dict)
    assert len(lime_contribs) > 0
