"""Approval Rules evaluator determining required approval levels for portfolio decisions."""

from typing import Dict, Optional, Tuple
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.approval import ApprovalLevel
from src.models.portfolio import Portfolio

logger = get_logger(__name__)

Tuple_Level = Tuple[ApprovalLevel, str]


class ApprovalRulesEvaluator:
    """Enterprise Approval Rules Evaluator assessing risk, trade value, and confidence thresholds."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        cfg = config or {}
        rules = cfg.get("approval_rules", {}).get("thresholds", {})
        self.high_val_threshold = rules.get("high_value_portfolio_threshold", 500000.0)
        self.ultra_val_threshold = rules.get("ultra_high_value_portfolio_threshold", 2000000.0)
        self.large_trade_threshold = rules.get("large_trade_threshold", 100000.0)
        self.low_conf_threshold = rules.get("low_confidence_threshold", 0.75)
        self.low_consensus_threshold = rules.get("low_consensus_threshold", 0.80)

    def determine_approval_level(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
    ) -> Tuple_Level:
        """Determine required approval level and rationale string.

        Args:
            portfolio: Target portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.

        Returns:
            Tuple of (ApprovalLevel, reason_string).
        """
        port_val = portfolio.total_market_value
        opt_sum = decision_package.optimization_summary
        total_trade_cost = opt_sum.get("total_cost", 0.0)

        # Rule 1: Ultra high value portfolio or REJECT recommendation -> ESCALATION_REQUIRED
        if port_val >= self.ultra_val_threshold or decision_package.recommendation == "REJECT":
            return (
                ApprovalLevel.ESCALATION_REQUIRED,
                f"Portfolio value (${port_val:,.2f}) exceeds ${self.ultra_val_threshold:,.2f} or AI recommendation is REJECT.",
            )

        # Rule 2: High value portfolio, large trade value, low confidence, or low consensus -> APPROVAL_REQUIRED
        if (
            port_val >= self.high_val_threshold
            or total_trade_cost >= self.large_trade_threshold
            or decision_package.confidence_score < self.low_conf_threshold
            or decision_package.consensus_score < self.low_consensus_threshold
            or decision_package.recommendation == "MODIFIED_EXECUTE"
        ):
            return (
                ApprovalLevel.APPROVAL_REQUIRED,
                f"Requires advisor approval (Portfolio value: ${port_val:,.2f}, Confidence: {decision_package.confidence_score:.2f}).",
            )

        # Rule 3: Moderate confidence or advisory criteria -> ADVISORY
        if decision_package.confidence_score < 0.85:
            return (
                ApprovalLevel.ADVISORY,
                f"Advisory notification sent to assigned advisor (Confidence: {decision_package.confidence_score:.2f}).",
            )

        # Rule 4: Fully autonomous execution -> INFORMATIONAL
        return (
            ApprovalLevel.INFORMATIONAL,
            "Low risk autonomous execution with full agent consensus.",
        )
