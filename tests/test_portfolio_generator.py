"""Unit tests for Portfolio generation."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory


def test_portfolio_generator() -> None:
    """Test generating portfolios for clients."""
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
    securities = sec_gen.generate_securities(num_securities=100)

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=50, securities=securities)

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    assert len(portfolios) == 50
    for p in portfolios:
        assert isinstance(p, Portfolio)
        assert p.portfolio_id.startswith("PORT_")
        assert 15 <= p.num_securities <= 40
        assert len(p.holdings) == p.num_securities
        assert p.total_market_value > 0
        assert p.cash_balance >= 0

        # Verify holdings target weight sum
        target_w_sum = sum(h.target_weight for h in p.holdings)
        assert 0.99 <= target_w_sum <= 1.01

        # Verify holdings current weight sum
        curr_w_sum = sum(h.current_weight for h in p.holdings)
        assert 0.99 <= curr_w_sum <= 1.01
