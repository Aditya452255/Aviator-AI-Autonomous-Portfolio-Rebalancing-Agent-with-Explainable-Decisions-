"""Unit tests for OverrideManager advisor override operations."""

import pytest
from src.core.config import load_config
from src.core.exceptions import ValidationError
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.governance.override_manager import OverrideManager
from src.models.override import OverrideAction, OverrideRecord
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_rebalancer import PortfolioRebalancer
from src.workflows.workflow_engine import MultiAgentWorkflowEngine


def test_override_manager_execution() -> None:
    """Test executing advisor manual overrides and validating required comments."""
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

    ovr_mgr = OverrideManager()

    # Valid override
    rec = ovr_mgr.execute_override(
        decision_package=package,
        advisor_id="ADV_101",
        action=OverrideAction.REJECT,
        reason_category="CLIENT_REQUEST",
        comments="Client requested to postpone rebalance until next quarter.",
    )
    assert isinstance(rec, OverrideRecord)
    assert rec.action == OverrideAction.REJECT
    assert rec.modified_recommendation == "CANCELLED"

    # Validation failure: Missing comments
    with pytest.raises(ValidationError, match="requires detailed comments"):
        ovr_mgr.execute_override(
            decision_package=package,
            advisor_id="ADV_101",
            action=OverrideAction.APPROVE,
            reason_category="TAX_TACTICAL",
            comments="",
        )
