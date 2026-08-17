"""Unit tests for AllocationAnalyzer and DriftMonitor execution modes."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.monitoring.allocation_analyzer import AllocationAnalyzer
from src.monitoring.drift_monitor import DriftMonitor


def test_allocation_analyzer_and_monitor() -> None:
    """Test AllocationAnalyzer single portfolio and universe allocation summaries."""
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

    analyzer = AllocationAnalyzer()
    df_single = analyzer.analyze_portfolio_allocation(portfolios[0])
    assert not df_single.empty
    assert len(df_single) == 4

    universe_sums = analyzer.analyze_universe_allocation(portfolios)
    assert len(universe_sums) > 0

    monitor = DriftMonitor(risk_categories=risk_cats, batch_size=2)
    inc_metrics = monitor.monitor_incremental(portfolios[:2])
    assert len(inc_metrics) == 2

    on_demand_metric = monitor.monitor_on_demand(portfolios[0])
    assert on_demand_metric.portfolio_id == portfolios[0].portfolio_id

    flagged = monitor.filter_flagged_portfolios(inc_metrics)
    assert isinstance(flagged, list)
