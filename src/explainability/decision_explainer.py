"""Master Decision Explainer orchestrating multi-audience explanation generation."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.explainability.advisor_explainer import AdvisorExplainer
from src.explainability.client_explainer import ClientExplainer
from src.explainability.compliance_explainer import ComplianceExplainer
from src.memory.decision_memory import FinalDecisionPackage
from src.models.explanation import AdvisorExplanation, ClientExplanation, ComplianceExplanation
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class DecisionExplainer:
    """Enterprise Master Decision Explainer generating complete multi-audience explanation sets."""

    def __init__(self) -> None:
        self.client_explainer = ClientExplainer()
        self.advisor_explainer = AdvisorExplainer()
        self.compliance_explainer = ComplianceExplainer()

    def generate_all_explanations(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
        shap_values: Dict[str, float],
        counterfactual_str: str = "",
        top_driver: str = "portfolio_drift",
    ) -> Dict[str, ClientExplanation | AdvisorExplanation | ComplianceExplanation]:
        """Generate Client, Advisor, and Compliance explanation objects.

        Args:
            portfolio: Target portfolio.
            decision_package: FinalDecisionPackage from Phase 4.
            shap_values: Map of SHAP values.
            counterfactual_str: Counterfactual summary text.
            top_driver: Primary feature driver name.

        Returns:
            Dictionary containing 'client', 'advisor', and 'compliance' explanation objects.
        """
        cli_exp = self.client_explainer.generate_client_explanation(
            portfolio=portfolio,
            decision_package=decision_package,
            top_driver=top_driver,
        )

        adv_exp = self.advisor_explainer.generate_advisor_explanation(
            portfolio=portfolio,
            decision_package=decision_package,
            top_driver=top_driver,
        )

        comp_exp = self.compliance_explainer.generate_compliance_explanation(
            portfolio=portfolio,
            decision_package=decision_package,
            shap_values=shap_values,
            counterfactual_summary=counterfactual_str,
        )

        return {
            "client": cli_exp,
            "advisor": adv_exp,
            "compliance": comp_exp,
        }
