"""Risk Manager Agent analyzing VaR, Tracking Error, concentration risk, and stress scenarios."""

from typing import Any, Dict, Optional
import numpy as np

from src.core.logger import get_logger
from src.memory.agent_context import TaskResult
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.task_factory import TaskFactory

logger = get_logger(__name__)


class RiskManagerAgent:
    """Chief Risk Officer Agent assessing quantitative portfolio risk metrics."""

    def __init__(self, agent_config: Optional[Dict] = None) -> None:
        self.name = "Risk Manager"
        self.role = "Chief Risk Officer"
        self.confidence_threshold = 0.75

    def assess_risk(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        input_context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """Evaluate portfolio risk metrics: VaR, Tracking Error, concentration risk, and stress testing.

        Args:
            portfolio: Portfolio instance.
            opt_result: OptimizationResult from Phase 3.
            input_context: Input context dictionary.

        Returns:
            TaskResult with risk evaluation findings.
        """
        task_id = f"TSK_RISK_{portfolio.portfolio_id}"

        # 1. Estimate 95% Parametric VaR (daily 95% VaR = 1.645 * daily_vol)
        est_annual_vol = 0.16
        daily_vol = est_annual_vol / np.sqrt(252.0)
        var_95_pct = 1.645 * daily_vol * 100.0  # % of portfolio value at risk daily

        # 2. Tracking Error
        te_after = opt_result.tracking_error_after

        # 3. Maximum Single Security Weight Concentration
        sec_weights = list(opt_result.security_target_weights.values()) if opt_result.security_target_weights else [h.current_weight for h in portfolio.holdings]
        max_sec_w = max(sec_weights) if sec_weights else 0.0

        # 4. Stress Test Scenario Impact (-10% market crash scenario)
        stress_loss_value = portfolio.total_market_value * 0.10

        # Risk Classification
        if max_sec_w > 0.25 or te_after > 0.08:
            risk_rating = "HIGH"
            recommendation = "MODIFY"
            confidence = 0.70
            comments = f"High risk detected: max position weight ({max_sec_w:.1%}) or tracking error exceeds limits."
        elif max_sec_w > 0.18:
            risk_rating = "MEDIUM"
            recommendation = "APPROVE"
            confidence = 0.85
            comments = "Medium risk profile: position concentration within tolerable bounds."
        else:
            risk_rating = "LOW"
            recommendation = "APPROVE"
            confidence = 0.95
            comments = "Low risk profile: portfolio is well-diversified with low tracking error."

        output_data = {
            "portfolio_id": portfolio.portfolio_id,
            "risk_rating": risk_rating,
            "var_95_daily_pct": round(var_95_pct, 2),
            "tracking_error_after": te_after,
            "max_security_weight": round(max_sec_w, 4),
            "stress_test_market_crash_loss": round(stress_loss_value, 2),
            "concentration_risk": "HIGH" if max_sec_w > 0.20 else "LOW",
        }

        return TaskFactory.create_task_result(
            agent_name=self.name,
            task_id=task_id,
            input_data={"portfolio_id": portfolio.portfolio_id},
            output_data=output_data,
            confidence_score=confidence,
            recommendation=recommendation,
            comments=comments,
        )
