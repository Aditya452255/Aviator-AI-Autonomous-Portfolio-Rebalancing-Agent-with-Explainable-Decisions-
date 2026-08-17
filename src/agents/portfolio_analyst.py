"""Portfolio Analyst Agent evaluating optimization quality, drift reduction, and asset allocation."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult, TaskStatus
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.task_factory import TaskFactory

logger = get_logger(__name__)


class PortfolioAnalystAgent:
    """Senior Portfolio Analyst Agent analyzing optimization results and drift reduction."""

    def __init__(self, agent_config: Optional[Dict] = None) -> None:
        self.name = "Portfolio Analyst"
        self.role = "Senior Portfolio Analyst"
        self.confidence_threshold = 0.75

    def analyze_portfolio(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        input_context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """Analyze portfolio optimization results and generate analyst recommendations.

        Args:
            portfolio: Target portfolio instance.
            opt_result: OptimizationResult from Phase 3.
            input_context: Context dictionary.

        Returns:
            TaskResult object with analyst findings.
        """
        task_id = f"TSK_ANALYST_{portfolio.portfolio_id}"

        drift_before = opt_result.drift_score_before
        drift_after = opt_result.drift_score_after
        drift_reduction = ((drift_before - drift_after) / max(1e-5, drift_before)) * 100.0

        te_before = opt_result.tracking_error_before
        te_after = opt_result.tracking_error_after

        trade_count = len(opt_result.trades)
        turnover_pct = opt_result.turnover * 100.0

        # Quality scoring
        if opt_result.solver_status in ("OPTIMAL", "FEASIBLE") and drift_after <= drift_before:
            confidence = 0.92
            recommendation = "APPROVE"
            comments = f"Optimization successfully reduced drift by {drift_reduction:.1f}% with {trade_count} trade orders."
        else:
            confidence = 0.65
            recommendation = "MODIFY"
            comments = f"Optimization achieved status '{opt_result.solver_status}' with turnover of {turnover_pct:.1f}%."

        output_data = {
            "portfolio_id": portfolio.portfolio_id,
            "strategy": opt_result.strategy.value if hasattr(opt_result.strategy, "value") else str(opt_result.strategy),
            "solver_status": opt_result.solver_status,
            "drift_score_before": drift_before,
            "drift_score_after": drift_after,
            "drift_reduction_pct": round(drift_reduction, 2),
            "tracking_error_before": te_before,
            "tracking_error_after": te_after,
            "trade_count": trade_count,
            "turnover_pct": round(turnover_pct, 2),
            "quality_rating": "EXCELLENT" if confidence >= 0.85 else "SATISFACTORY",
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
