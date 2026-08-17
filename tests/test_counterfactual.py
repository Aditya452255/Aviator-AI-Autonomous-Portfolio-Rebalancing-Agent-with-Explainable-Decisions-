"""Unit tests for CounterfactualEngine."""

import pytest
from src.explainability.counterfactual_engine import CounterfactualEngine
from src.models.counterfactual import CounterfactualSummary


def test_counterfactual_engine_scenarios() -> None:
    """Test minimum-change counterfactual explanation scenarios."""
    engine = CounterfactualEngine(drift_threshold=0.042)

    features_high_drift = {"portfolio_drift": 0.065, "days_since_last_rebalance": 100.0}
    cf_summary = engine.generate_counterfactuals("PORT_TEST", features_high_drift, "REBALANCE")

    assert isinstance(cf_summary, CounterfactualSummary)
    assert len(cf_summary.counterfactuals) >= 1
    assert cf_summary.counterfactuals[0].counterfactual_decision == "NO_REBALANCE"
