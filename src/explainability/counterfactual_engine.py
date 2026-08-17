"""Counterfactual Engine computing minimum-change counterfactual explanations."""

from typing import Dict, List, Optional
import pandas as pd
from src.core.logger import get_logger
from src.models.counterfactual import CounterfactualExplanation, CounterfactualSummary

logger = get_logger(__name__)


class CounterfactualEngine:
    """Enterprise Counterfactual Engine generating minimum-change counterfactual scenarios."""

    def __init__(self, drift_threshold: float = 0.042) -> None:
        self.drift_threshold = drift_threshold

    def generate_counterfactuals(
        self,
        portfolio_id: str,
        features: Dict[str, float],
        current_decision: str = "REBALANCE",
    ) -> CounterfactualSummary:
        """Generate counterfactual explanation scenarios for a portfolio decision.

        Args:
            portfolio_id: Target portfolio ID.
            features: Dictionary of current feature values.
            current_decision: Observed decision string.

        Returns:
            CounterfactualSummary domain model.
        """
        curr_drift = features.get("portfolio_drift", 0.055)
        curr_days = features.get("days_since_last_rebalance", 45.0)

        counterfactuals: List[CounterfactualExplanation] = []

        # Counterfactual Scenario 1: Portfolio Drift Threshold
        if curr_drift >= self.drift_threshold:
            cf_drift = round(self.drift_threshold - 0.005, 4)
            cf_1 = CounterfactualExplanation(
                feature_name="portfolio_drift",
                current_value=round(curr_drift, 4),
                counterfactual_value=cf_drift,
                current_decision=current_decision,
                counterfactual_decision="NO_REBALANCE",
                impact_description=(
                    f"If Portfolio Drift were {cf_drift:.1%} (below the {self.drift_threshold:.1%} rebalance threshold), "
                    f"the autonomous agent would NOT trigger a rebalance."
                ),
            )
            counterfactuals.append(cf_1)
        else:
            cf_drift = round(self.drift_threshold + 0.005, 4)
            cf_1 = CounterfactualExplanation(
                feature_name="portfolio_drift",
                current_value=round(curr_drift, 4),
                counterfactual_value=cf_drift,
                current_decision="NO_REBALANCE",
                counterfactual_decision="REBALANCE",
                impact_description=(
                    f"If Portfolio Drift increased to {cf_drift:.1%} (above {self.drift_threshold:.1%}), "
                    f"a rebalance order would be triggered immediately."
                ),
            )
            counterfactuals.append(cf_1)

        # Counterfactual Scenario 2: Calendar Rebalance Interval
        if curr_days > 90.0:
            cf_2 = CounterfactualExplanation(
                feature_name="days_since_last_rebalance",
                current_value=round(curr_days, 1),
                counterfactual_value=60.0,
                current_decision=current_decision,
                counterfactual_decision="NO_REBALANCE",
                impact_description=(
                    f"If days since last rebalance were 60 days (below quarterly 90-day threshold), "
                    f"the calendar trigger would not have activated."
                ),
            )
            counterfactuals.append(cf_2)

        return CounterfactualSummary(
            portfolio_id=portfolio_id,
            counterfactuals=counterfactuals,
        )
