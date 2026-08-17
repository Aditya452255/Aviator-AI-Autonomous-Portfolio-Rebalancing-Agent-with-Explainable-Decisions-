"""Unit tests for Drift Calculator engine."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.drift import PortfolioDriftMetrics
from src.models.risk_category import RiskCategory
from src.monitoring.drift_calculator import DriftCalculator


def test_drift_calculator_single_portfolio() -> None:
    """Test calculation of absolute, relative, and RMS drift metrics for a portfolio."""
    config = load_config("config")
    risk_cats = {}
    for k, item in config.risk_categories.items():
        risk_cats[k] = RiskCategory(
            id=item.id,
            name=item.name,
            target_equity=item.target_equity,
            target_fixed_income=item.target_fixed_income,
            target_alternatives=item.target_alternatives,
            target_cash=item.target_cash,
            drift_threshold=item.drift_threshold,
        )

    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=50)

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=10, securities=securities)

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    calculator = DriftCalculator(risk_categories=risk_cats)
    metrics = calculator.calculate_portfolio_drift(portfolios[0])

    assert isinstance(metrics, PortfolioDriftMetrics)
    assert metrics.portfolio_id == portfolios[0].portfolio_id
    assert metrics.total_absolute_drift >= 0.0
    assert metrics.portfolio_drift_score >= 0.0
    assert "Equity" in metrics.asset_drifts
    assert "Fixed Income" in metrics.asset_drifts
    assert len(metrics.security_drifts) == portfolios[0].num_securities
