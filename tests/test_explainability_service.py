"""Unit tests for ExplainabilityService orchestration and data exports."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.services.agent_service import AgentService
from src.services.explainability_service import ExplainabilityService
from src.services.monitoring_service import MonitoringService
from src.services.optimization_service import OptimizationService


def test_explainability_service_full_cycle(tmp_path: Path) -> None:
    """Test full Phase 5 explainability service workflow and dataset exports."""
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

    xai_service = ExplainabilityService(config=config)
    xai_results, metrics = xai_service.run_explainability_cycle(
        portfolios=portfolios,
        decision_packages=packages,
        save_exports=True,
        generate_plots=True,
    )

    assert len(xai_results) == len(packages)
    assert (tmp_path / "client_explanations.parquet").exists()
    assert (tmp_path / "advisor_explanations.parquet").exists()
    assert (tmp_path / "compliance_explanations.parquet").exists()
    assert (tmp_path / "feature_importance.csv").exists()
    assert (tmp_path / "counterfactuals.csv").exists()
    assert (tmp_path / "explainability_metrics.json").exists()
