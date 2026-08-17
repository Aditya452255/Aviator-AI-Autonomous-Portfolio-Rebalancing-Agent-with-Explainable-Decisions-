"""Unit tests for HistoricalReplayEngine and StrategyRunner."""

import pytest
from src.backtesting.historical_replay import HistoricalReplayEngine
from src.backtesting.strategy_runner import StrategyRunner
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.backtest_result import StrategyPerformance
from src.models.risk_category import RiskCategory


def test_historical_replay_schedules() -> None:
    """Test stepping index calculation for daily, monthly, and quarterly schedules."""
    replay = HistoricalReplayEngine()

    daily_steps = replay.get_replay_schedules(252, "DAILY")
    assert len(daily_steps) == 252

    monthly_steps = replay.get_replay_schedules(252, "MONTHLY")
    assert len(monthly_steps) == 12

    quarterly_steps = replay.get_replay_schedules(252, "QUARTERLY")
    assert len(quarterly_steps) == 4


def test_strategy_runner() -> None:
    """Test strategy execution for Buy & Hold and AI Optimized strategies."""
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

    runner = StrategyRunner()
    perf_bh = runner.run_strategy(portfolios[0], "BUY_AND_HOLD")
    perf_ai = runner.run_strategy(portfolios[0], "AI_OPTIMIZED")

    assert isinstance(perf_bh, StrategyPerformance)
    assert isinstance(perf_ai, StrategyPerformance)
    assert perf_ai.cagr > 0.0
    assert perf_ai.sharpe_ratio != 0.0
