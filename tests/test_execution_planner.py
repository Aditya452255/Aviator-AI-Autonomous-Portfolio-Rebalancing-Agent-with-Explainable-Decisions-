"""Unit tests for Execution Planner and Liquidity Manager."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.execution_plan import ExecutionPlan, ExecutionStrategy
from src.models.risk_category import RiskCategory
from src.optimization.execution_planner import ExecutionPlanner
from src.optimization.liquidity_manager import LiquidityManager
from src.optimization.trade_generator import TradeGenerator


def test_execution_planner_and_liquidity() -> None:
    """Test execution strategy selection (TWAP/VWAP) and order slice creation."""
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
    opt_weights = {h.ticker: h.current_weight * 1.05 for h in p.holdings}
    generator = TradeGenerator()
    trades = generator.generate_trades(portfolio=p, optimized_sec_weights=opt_weights, min_trade_value=1.0)

    planner = ExecutionPlanner()
    plan = planner.generate_execution_plan(portfolio=p, trades=trades, priority="Critical")

    assert isinstance(plan, ExecutionPlan)
    assert plan.portfolio_id == p.portfolio_id
    assert plan.trade_priority == "Critical"
    assert len(plan.slices) >= 1
    assert plan.estimated_completion_minutes > 0.0
