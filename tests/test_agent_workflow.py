"""Unit tests for 6-agent Crew workflow execution, agent outputs, and decision package aggregation."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.memory.decision_memory import DecisionMemory, FinalDecisionPackage
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_rebalancer import PortfolioRebalancer
from src.validators.decision_validator import DecisionValidator
from src.workflows.workflow_engine import MultiAgentWorkflowEngine


def test_agent_workflow_execution() -> None:
    """Test full multi-agent workflow execution for a portfolio."""
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

    rebalancer = PortfolioRebalancer()
    opt_res = rebalancer.rebalance_portfolio(portfolio=portfolios[0], risk_category=risk_cats["balanced"])

    engine = MultiAgentWorkflowEngine()
    package = engine.run_workflow(portfolio=portfolios[0], opt_result=opt_res, client=clients[0])

    assert isinstance(package, FinalDecisionPackage)
    assert package.portfolio_id == portfolios[0].portfolio_id
    assert package.consensus_score > 0.0
    assert package.confidence_score > 0.0
    assert "client_explanation" in package.explanations
    assert len(package.agent_outputs) == 5

    # Test DecisionMemory
    memory = engine.decision_memory
    retrieved = memory.get_decision(package.decision_id)
    assert retrieved is not None
    assert len(memory.list_decisions_for_portfolio(portfolios[0].portfolio_id)) >= 1

    # Test DecisionValidator
    validator = DecisionValidator()
    assert validator.validate_decision_package(package) is True


def test_agent_specialized_evaluations() -> None:
    """Test individual agent evaluations: Risk, Tax, Compliance."""
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

    rebalancer = PortfolioRebalancer()
    opt_res = rebalancer.rebalance_portfolio(portfolio=portfolios[0], risk_category=risk_cats["balanced"])

    engine = MultiAgentWorkflowEngine()
    tax_res = engine.crew_builder.tax_specialist.evaluate_tax(portfolio=portfolios[0], opt_result=opt_res)
    assert tax_res.confidence_score > 0.0

    comp_res = engine.crew_builder.compliance_officer.verify_compliance(portfolio=portfolios[0], opt_result=opt_res, client=clients[0])
    assert comp_res.confidence_score > 0.0
