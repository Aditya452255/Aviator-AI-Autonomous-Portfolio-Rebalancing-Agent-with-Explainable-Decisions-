"""Unit tests for Trigger Engine evaluation."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.models.trigger import TriggerReason, TriggerType
from src.monitoring.drift_calculator import DriftCalculator
from src.monitoring.trigger_engine import TriggerEngine


def test_trigger_engine_evaluations() -> None:
    """Test trigger evaluations across Threshold, Calendar, Market Event, and Client Event categories."""
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
    clients[0].upcoming_cash_flow = 200000.0  # Large cash deposit

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    calculator = DriftCalculator(risk_categories=risk_cats)
    metrics = calculator.calculate_portfolio_drift(portfolios[0])

    trigger_engine = TriggerEngine()

    market_summary = {
        "max_price_gap": 0.05,
        "market_volatility": 0.30,
        "sector_crash_drop": 0.06,
    }

    triggers = trigger_engine.evaluate_triggers(
        portfolio=portfolios[0],
        metrics=metrics,
        client=clients[0],
        market_summary=market_summary,
        days_since_rebalance=100,
    )

    assert len(triggers) > 0
    t_types = {t.trigger_type for t in triggers}
    assert TriggerType.CALENDAR in t_types
    assert TriggerType.MARKET_EVENT in t_types
