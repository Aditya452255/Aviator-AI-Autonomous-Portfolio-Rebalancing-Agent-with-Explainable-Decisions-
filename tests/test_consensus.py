"""Unit tests for ConsensusValidator and DecisionValidator error handling."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.core.exceptions import ValidationError
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.memory.agent_context import TaskResult, TaskStatus
from src.memory.shared_state import SharedWorkflowState
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_rebalancer import PortfolioRebalancer
from src.services.agent_service import AgentService
from src.services.monitoring_service import MonitoringService
from src.services.optimization_service import OptimizationService
from src.validators.consensus_validator import ConsensusValidator
from src.validators.decision_validator import DecisionValidator
from src.workflows.task_factory import TaskFactory


def test_consensus_validator_scoring() -> None:
    """Test consensus score calculation across agent recommendations."""
    validator = ConsensusValidator()

    t1 = TaskFactory.create_task_result("Portfolio Analyst", "1", {}, {}, 0.90, recommendation="APPROVE")
    t2 = TaskFactory.create_task_result("Risk Manager", "2", {}, {}, 0.85, recommendation="APPROVE")
    t3 = TaskFactory.create_task_result("Tax Specialist", "3", {}, {}, 0.88, recommendation="APPROVE")

    score = validator.compute_consensus_score({"Portfolio Analyst": t1, "Risk Manager": t2, "Tax Specialist": t3})
    assert score == 1.0


def test_decision_validator_failures() -> None:
    """Test DecisionValidator error handling for missing agents or low confidence."""
    validator = DecisionValidator()
    state = SharedWorkflowState(portfolio_id="PORT_TEST", client_id="CLT_TEST")

    t1 = TaskFactory.create_task_result("Portfolio Analyst", "1", {}, {}, 0.90)
    state.record_task_result(t1)

    with pytest.raises(ValidationError, match="Missing required agent output"):
        validator.validate_workflow_state(state)


def test_agent_service_full_cycle(tmp_path: Path) -> None:
    """Test AgentService full decision intelligence cycle execution."""
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
    packages, analytics = agent_service.run_decision_intelligence_cycle(portfolios=portfolios, optimization_results=opt_results, clients=clients, save_exports=True)

    assert len(packages) == len(opt_results)
    assert (tmp_path / "decision_packages.parquet").exists()
    assert (tmp_path / "agent_task_history.parquet").exists()
    assert (tmp_path / "decision_summary.json").exists()
