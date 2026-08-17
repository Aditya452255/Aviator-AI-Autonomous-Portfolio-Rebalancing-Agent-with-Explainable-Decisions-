"""Decision Validator verifying completeness, agent execution, confidence thresholds, and output integrity."""

from typing import Dict, List, Optional
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.memory.shared_state import SharedWorkflowState

logger = get_logger(__name__)


class DecisionValidator:
    """Enterprise decision validator verifying multi-agent execution integrity."""

    REQUIRED_AGENTS = [
        "Portfolio Analyst",
        "Risk Manager",
        "Tax Specialist",
        "Compliance Officer",
        "Explanation Writer",
    ]

    def validate_workflow_state(self, state: SharedWorkflowState) -> bool:
        """Validate workflow state before aggregating final decision package.

        Args:
            state: SharedWorkflowState instance.

        Returns:
            True if all required agents executed cleanly.

        Raises:
            ValidationError: If required agent output is missing or confidence is too low.
        """
        for agent in self.REQUIRED_AGENTS:
            if agent not in state.task_results:
                raise ValidationError(f"Missing required agent output for: '{agent}'")

            res = state.task_results[agent]
            if res.confidence_score < 0.60:
                raise ValidationError(f"Agent '{agent}' confidence score ({res.confidence_score}) is below minimum threshold 0.60")

        return True

    def validate_decision_package(self, package: FinalDecisionPackage) -> bool:
        """Validate integrity of generated FinalDecisionPackage.

        Args:
            package: FinalDecisionPackage instance.

        Returns:
            True if package is valid.

        Raises:
            ValidationError: If package invariants fail.
        """
        if not package.decision_id or not package.portfolio_id:
            raise ValidationError("DecisionPackage missing decision_id or portfolio_id.")

        if package.confidence_score < 0.0 or package.confidence_score > 1.0:
            raise ValidationError(f"Invalid decision package confidence score: {package.confidence_score}")

        if not package.explanations.get("client_explanation"):
            raise ValidationError("DecisionPackage missing client explanation.")

        return True
