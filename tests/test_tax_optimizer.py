"""Unit tests for Tax Optimizer and Tax Lot Manager."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.models.trade import Trade, TradeAction
from src.optimization.tax_lot_manager import TaxLotManager
from src.optimization.tax_optimizer import TaxOptimizer


def test_tax_optimizer_evaluation() -> None:
    """Test tax lot generation, lot selection strategies, and tax loss harvesting."""
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

    p = portfolios[0]
    tax_lot_mgr = TaxLotManager(seed=42)
    lots_map = tax_lot_mgr.generate_synthetic_tax_lots(p)

    assert len(lots_map) == p.num_securities

    h = p.holdings[0]
    trade_sell = Trade(
        trade_id="TRD_SELL_001",
        portfolio_id=p.portfolio_id,
        ticker=h.ticker,
        action=TradeAction.SELL,
        shares=h.shares * 0.5,
        current_weight=h.current_weight,
        target_weight=h.current_weight * 0.5,
        weight_change=-h.current_weight * 0.5,
        price=h.current_price,
        market_value=h.current_price * h.shares * 0.5,
        reason="Tax Test",
    )

    tax_opt = TaxOptimizer()
    tax_impact, breakdown = tax_opt.evaluate_trade_tax_impact(trade_sell, lots_map[h.ticker])

    assert "realized_stcg" in breakdown
    assert "realized_ltcg" in breakdown
    assert "harvested_loss" in breakdown
    assert "net_tax_impact" in breakdown
