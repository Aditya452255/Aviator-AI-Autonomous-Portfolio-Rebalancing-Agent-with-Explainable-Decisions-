"""Unit tests for Priority Engine scoring and classification."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.rebalancing_request import PriorityLevel
from src.models.risk_category import RiskCategory
from src.monitoring.drift_calculator import DriftCalculator
from src.monitoring.priority_engine import PriorityEngine


def test_priority_engine_scoring() -> None:
    """Test priority scoring and priority level classification."""
    config = load_config("config")
    risk_cats = {
        k: RiskCategory(
            id=v.id,
            name=v.name,
            target_equity=v.target_equity,
            target_fixed_income=v.target_fixed_income,
            target_alternatives=v.target_alternatives,
            target_cash=v.target_cash,
            drift_threshold=v.drift_threshold,
        )
        for k, v in config.risk_categories.items()
    }

    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=50)

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=5, securities=securities)

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    calculator = DriftCalculator(risk_categories=risk_cats)
    metrics = calculator.calculate_portfolio_drift(portfolios[0])

    priority_engine = PriorityEngine()
    score, level = priority_engine.calculate_priority(
        portfolio=portfolios[0],
        metrics=metrics,
        client=clients[0],
        market_volatility=0.25,
        days_since_rebalance=60,
    )

    assert 0.0 <= score <= 1.0
    assert isinstance(level, PriorityLevel)
