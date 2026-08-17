"""Unit tests for Trade Generator and Trade Validator."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.models.trade import Trade, TradeAction
from src.optimization.trade_generator import TradeGenerator
from src.optimization.trade_validator import TradeValidator


def test_trade_generator_and_validator() -> None:
    """Test generating executable trades and validating zero negative quantities or duplicates."""
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

    # Shift target weights to force trade generation
    p = portfolios[0]
    opt_weights = {h.ticker: h.current_weight * (1.10 if i % 2 == 0 else 0.90) for i, h in enumerate(p.holdings)}
    total_w = sum(opt_weights.values())
    opt_weights = {k: v / total_w for k, v in opt_weights.items()}

    generator = TradeGenerator()
    trades = generator.generate_trades(portfolio=p, optimized_sec_weights=opt_weights, min_trade_value=10.0)

    assert len(trades) > 0
    validator = TradeValidator()
    assert validator.validate_trades(trades=trades, portfolio=p) is True

    for t in trades:
        assert isinstance(t, Trade)
        assert t.shares > 0
        assert t.market_value > 0
        assert t.action in (TradeAction.BUY, TradeAction.SELL)
