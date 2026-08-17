"""Unit tests for Portfolio Optimizer convergence and optimization strategies."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.optimization_result import OptimizationStrategy
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_optimizer import PortfolioOptimizer


def test_portfolio_optimizer_strategies() -> None:
    """Test convex portfolio optimization across MIN_DRIFT, MIN_COST, BALANCED, and TAX_OPTIMIZED strategies."""
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

    optimizer = PortfolioOptimizer()

    for strat in [OptimizationStrategy.MIN_DRIFT, OptimizationStrategy.MIN_COST, OptimizationStrategy.BALANCED, OptimizationStrategy.TAX_OPTIMIZED]:
        cat_w, sec_w, status = optimizer.optimize_portfolio(
            portfolio=portfolios[0],
            risk_category=risk_cats["balanced"],
            strategy=strat,
        )
        assert status in ("OPTIMAL", "OPTIMAL_INACCURATE", "FEASIBLE_FALLBACK")
        assert len(cat_w) == 4
        assert len(sec_w) == portfolios[0].num_securities
        assert 0.99 <= sum(sec_w.values()) + cat_w["Cash"] <= 1.01
