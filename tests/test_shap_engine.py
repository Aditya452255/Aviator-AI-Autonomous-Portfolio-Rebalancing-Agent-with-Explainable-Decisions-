"""Unit tests for SurrogateModel and SHAPEngine."""

import pytest
from src.explainability.shap_engine import SHAPEngine
from src.explainability.surrogate_model import SurrogateModel


def test_surrogate_model_and_shap_engine() -> None:
    """Test surrogate model training and local SHAP feature attribution calculation."""
    surrogate = SurrogateModel()
    surrogate.fit_synthetic_baseline(num_samples=100)

    X_sample = surrogate.extract_features(
        portfolio_id="PORT_TEST",
        drift_score=0.065,
        risk_category_str="Balanced",
        tax_impact=-150.0,
    )

    probs = surrogate.predict_proba(X_sample)
    assert probs.shape == (1, 2)

    shap_engine = SHAPEngine(surrogate_model=surrogate)
    shap_vals = shap_engine.compute_shap_values(X_sample)

    assert isinstance(shap_vals, dict)
    assert "portfolio_drift" in shap_vals
    assert len(shap_vals) == len(surrogate.FEATURE_NAMES)
