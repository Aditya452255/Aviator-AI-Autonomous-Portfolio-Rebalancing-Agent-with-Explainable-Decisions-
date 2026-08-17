"""Priority Engine scoring rebalancing opportunities across multiple risk factors."""

from typing import Dict, List, Optional
import numpy as np

from src.core.logger import get_logger
from src.models.client import ClientProfile
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.rebalancing_request import PriorityLevel
from src.models.trigger import TriggerEvaluation

logger = get_logger(__name__)


class PriorityEngine:
    """Enterprise priority engine calculating multi-factor priority scores and assigning priority levels."""

    def __init__(self, weights_config: Optional[Dict] = None) -> None:
        cfg = weights_config or {}
        p_weights = cfg.get("priority_weights", {})
        self.w_size = p_weights.get("portfolio_size_weight", 0.20)
        self.w_drift = p_weights.get("drift_severity_weight", 0.35)
        self.w_risk = p_weights.get("risk_category_weight", 0.15)
        self.w_vol = p_weights.get("market_volatility_weight", 0.10)
        self.w_time = p_weights.get("time_since_last_rebalance_weight", 0.10)
        self.w_client = p_weights.get("client_importance_weight", 0.05)
        self.w_tax = p_weights.get("tax_impact_weight", 0.05)

        p_thresh = cfg.get("priority_thresholds", {})
        self.th_critical = p_thresh.get("critical", 0.75)
        self.th_high = p_thresh.get("high", 0.55)
        self.th_medium = p_thresh.get("medium", 0.35)

    def calculate_priority(
        self,
        portfolio: Portfolio,
        metrics: PortfolioDriftMetrics,
        client: Optional[ClientProfile] = None,
        triggers: Optional[List[TriggerEvaluation]] = None,
        market_volatility: float = 0.18,
        days_since_rebalance: int = 45,
    ) -> tuple[float, PriorityLevel]:
        """Calculate composite multi-factor priority score and assign PriorityLevel.

        Args:
            portfolio: Portfolio instance.
            metrics: Calculated PortfolioDriftMetrics.
            client: Optional ClientProfile instance.
            triggers: Fired triggers list.
            market_volatility: Annualized market volatility fraction.
            days_since_rebalance: Days since last rebalancing execution.

        Returns:
            Tuple of (normalized priority_score 0.0-1.0, PriorityLevel).
        """
        # Factor 1: Portfolio Size Score (log-scaled up to 100M base currency)
        size_score = float(np.clip(np.log10(max(10000.0, portfolio.total_market_value)) / 8.0, 0.0, 1.0))

        # Factor 2: Drift Severity Score
        drift_score = float(np.clip(metrics.portfolio_drift_score / 0.12, 0.0, 1.0))

        # Factor 3: Trigger Severity Max
        trigger_sev = max([t.severity_score for t in triggers], default=0.0) if triggers else 0.0
        combined_drift_sev = max(drift_score, trigger_sev)

        # Factor 4: Risk Category Factor (higher sensitivity for ultra conservative or ultra aggressive)
        risk_map = {
            "ultra_conservative": 0.9,
            "conservative": 0.7,
            "balanced": 0.5,
            "aggressive": 0.7,
            "ultra_aggressive": 0.9,
        }
        risk_score = risk_map.get(metrics.risk_category.lower(), 0.5)

        # Factor 5: Market Volatility Factor
        vol_score = float(np.clip(market_volatility / 0.35, 0.0, 1.0))

        # Factor 6: Time Since Last Rebalance Factor (capped at 180 days)
        time_score = float(np.clip(days_since_rebalance / 180.0, 0.0, 1.0))

        # Factor 7: Client Importance (annual income tier)
        client_score = 0.5
        if client:
            client_score = float(np.clip(np.log10(max(100000.0, client.annual_income)) / 7.5, 0.0, 1.0))

        # Factor 8: Tax Impact Estimate (tax bracket level)
        tax_score = 0.5
        if client:
            tax_map = {"0%": 0.2, "10%": 0.4, "20%": 0.6, "30%": 0.8, "35%+": 1.0}
            tax_score = tax_map.get(str(client.tax_bracket), 0.5)

        # Weighted Sum
        composite_score = (
            self.w_size * size_score
            + self.w_drift * combined_drift_sev
            + self.w_risk * risk_score
            + self.w_vol * vol_score
            + self.w_time * time_score
            + self.w_client * client_score
            + self.w_tax * tax_score
        )

        final_score = round(float(np.clip(composite_score, 0.0, 1.0)), 4)

        if final_score >= self.th_critical:
            level = PriorityLevel.CRITICAL
        elif final_score >= self.th_high:
            level = PriorityLevel.HIGH
        elif final_score >= self.th_medium:
            level = PriorityLevel.MEDIUM
        else:
            level = PriorityLevel.LOW

        return final_score, level
