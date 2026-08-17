"""Unit tests for MonitoringService orchestration and data validation."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.services.monitoring_service import MonitoringService


def test_monitoring_service_cycle(tmp_path: Path) -> None:
    """Test full Phase 2 monitoring service cycle."""
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
    clients = client_gen.generate_clients(num_clients=20, securities=securities)

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    service = MonitoringService(config=config)
    metrics_list, queue, alerts, analytics = service.run_monitoring_cycle(
        portfolios=portfolios,
        clients=clients,
        save_exports=True,
    )

    assert len(metrics_list) == 20
    assert "cycle_metrics" in analytics
    assert "drift_statistics" in analytics

    # Check exported files
    assert (tmp_path / "drift_report.parquet").exists()
    assert (tmp_path / "rebalancing_queue.parquet").exists()
    assert (tmp_path / "alerts.parquet").exists()
    assert (tmp_path / "analytics_summary.json").exists()
