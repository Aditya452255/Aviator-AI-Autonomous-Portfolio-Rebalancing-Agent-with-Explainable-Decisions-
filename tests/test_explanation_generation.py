"""Unit tests for Client, Advisor, and Compliance explainers and quality scoring."""

import pytest
from src.core.config import load_config
from src.core.exceptions import ValidationError
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.explainability.decision_explainer import DecisionExplainer
from src.explainability.explanation_quality import ExplanationQualityEngine
from src.explainability.explanation_validator import ExplanationValidator
from src.models.explanation import AdvisorExplanation, ClientExplanation
from src.models.risk_category import RiskCategory
from src.optimization.portfolio_rebalancer import PortfolioRebalancer
from src.workflows.workflow_engine import MultiAgentWorkflowEngine


def test_multi_audience_explanation_generation() -> None:
    """Test multi-audience explanation generation and quality scoring."""
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

    explainer = DecisionExplainer()
    shap_vals = {"portfolio_drift": 0.05, "market_volatility": 0.01}
    explanations = explainer.generate_all_explanations(
        portfolio=portfolios[0],
        decision_package=package,
        shap_values=shap_vals,
    )

    validator = ExplanationValidator()
    assert validator.validate_client_explanation(explanations["client"]) is True
    assert validator.validate_advisor_explanation(explanations["advisor"]) is True

    quality = ExplanationQualityEngine()
    scores = quality.evaluate_quality(explanations["client"], explanations["advisor"], explanations["compliance"])
    assert scores.overall_score > 0.70


def test_explanation_validator_limits() -> None:
    """Test ExplanationValidator word limit and missing section validation."""
    validator = ExplanationValidator()

    # Missing section test
    invalid_cli = ClientExplanation(
        portfolio_id="PORT_1",
        summary="",
        word_count=0,
        benefits="",
        costs_and_taxes="",
        risks="",
    )
    with pytest.raises(ValidationError, match="missing required sections"):
        validator.validate_client_explanation(invalid_cli)

    # Word limit excess test
    long_cli = ClientExplanation(
        portfolio_id="PORT_1",
        summary="word " * 220,
        word_count=220,
        benefits="B",
        costs_and_taxes="C",
        risks="R",
    )
    with pytest.raises(ValidationError, match="exceeds max limit"):
        validator.validate_client_explanation(long_cli)

    invalid_adv = AdvisorExplanation(
        portfolio_id="PORT_1",
        summary="",
        word_count=0,
        drift_analysis="",
        tracking_error_analysis="",
        tax_and_cost_analysis="",
        liquidity_and_execution="",
    )
    with pytest.raises(ValidationError, match="missing required sections"):
        validator.validate_advisor_explanation(invalid_adv)
