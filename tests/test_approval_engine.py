"""Unit tests for ApprovalEngine, ApprovalRulesEvaluator, EscalationManager, and GovernancePolicyEngine."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.governance.approval_engine import ApprovalEngine
from src.governance.escalation_manager import EscalationManager
from src.governance.governance_policy import GovernancePolicyEngine
from src.models.approval import ApprovalLevel, ApprovalRequest
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_rebalancer import PortfolioRebalancer
from src.workflows.workflow_engine import MultiAgentWorkflowEngine


def test_approval_engine_level_determination() -> None:
    """Test automatic approval level determination."""
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

    app_engine = ApprovalEngine()
    req = app_engine.create_approval_request(portfolio=portfolios[0], decision_package=package)

    assert isinstance(req, ApprovalRequest)
    assert req.portfolio_id == portfolios[0].portfolio_id
    assert req.approval_level in (ApprovalLevel.INFORMATIONAL, ApprovalLevel.ADVISORY, ApprovalLevel.APPROVAL_REQUIRED, ApprovalLevel.ESCALATION_REQUIRED)

    dec = app_engine.record_decision(req.request_id, approver_id="ADV_001", status="APPROVED")
    assert dec.status == "APPROVED"


def test_escalation_manager_and_policy() -> None:
    """Test EscalationManager triggering and GovernancePolicyEngine drift check."""
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

    # Escalation Test
    esc_mgr = EscalationManager()
    evt = esc_mgr.evaluate_and_escalate(package, kill_switch_active=True)
    assert evt is not None
    assert evt.severity == "CRITICAL"

    # Policy Check Test
    pol_engine = GovernancePolicyEngine()
    is_compliant, viols = pol_engine.check_policy_compliance(portfolios[0], drift_score=0.10)
    assert is_compliant is False
    assert len(viols) == 1
