"""Unit tests for BacktestingService orchestration and dataset exports."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.services.agent_service import AgentService
from src.services.backtesting_service import BacktestingService
from src.services.monitoring_service import MonitoringService
from src.services.optimization_service import OptimizationService


def test_backtesting_service_full_cycle(tmp_path: Path) -> None:
    """Test full Phase 7 BacktestingService workflow and file exports."""
    config = load_config("config")
    config.storage.output_dir = str(tmp_path)

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

    mon_service = MonitoringService(config=config)
    _, queue, _, _ = mon_service.run_monitoring_cycle(portfolios=portfolios, clients=clients, save_exports=False)

    opt_service = OptimizationService(config=config)
    opt_results, _ = opt_service.run_optimization_cycle(portfolios=portfolios, rebalancing_queue=queue, clients=clients, securities=securities, save_exports=False)

    agent_service = AgentService(config=config)
    packages, _ = agent_service.run_decision_intelligence_cycle(portfolios=portfolios, optimization_results=opt_results, clients=clients, save_exports=False)

    bt_service = BacktestingService(config=config)
    results, analytics = bt_service.run_backtesting_cycle(
        portfolios=portfolios,
        optimization_results=opt_results,
        decision_packages=packages,
        trading_days=252,
        save_exports=True,
    )

    assert len(results) == len(portfolios)
    assert (tmp_path / "backtest_results.parquet").exists()
    assert (tmp_path / "strategy_comparison.csv").exists()
    assert (tmp_path / "benchmark_comparison.csv").exists()
    assert (tmp_path / "scenario_results.parquet").exists()
    assert (tmp_path / "performance_metrics.json").exists()
    assert (tmp_path / "agent_evaluation.csv").exists()
