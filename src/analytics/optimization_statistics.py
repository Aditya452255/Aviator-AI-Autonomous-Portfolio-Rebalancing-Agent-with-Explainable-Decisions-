"""Optimization Statistics analytics computing drift reduction, tracking error reduction, and turnover summaries."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from src.core.logger import get_logger
from src.models.optimization_result import OptimizationResult

logger = get_logger(__name__)


class OptimizationStatistics:
    """Enterprise analytics engine computing portfolio optimization metrics."""

    def compute_summary_statistics(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Compute aggregate statistical summary across optimization runs.

        Args:
            results: List of OptimizationResult instances.

        Returns:
            Dictionary containing drift reduction %, turnover, costs, and solver success rate.
        """
        if not results:
            return {"total_optimized_portfolios": 0}

        total_runs = len(results)
        optimal_count = sum(1 for r in results if "OPTIMAL" in r.solver_status or "FEASIBLE" in r.solver_status)

        drift_befores = np.array([r.drift_score_before for r in results])
        drift_afters = np.array([r.drift_score_after for r in results])
        drift_reduction_pct = float(np.mean((drift_befores - drift_afters) / np.maximum(1e-5, drift_befores) * 100.0))

        te_befores = np.array([r.tracking_error_before for r in results])
        te_afters = np.array([r.tracking_error_after for r in results])
        te_reduction_pct = float(np.mean((te_befores - te_afters) / np.maximum(1e-5, te_befores) * 100.0))

        turnovers = [r.turnover for r in results]
        total_trades = sum(len(r.trades) for r in results)
        total_costs = sum(r.total_estimated_cost for r in results)
        total_taxes = sum(r.total_tax_impact for r in results)

        return {
            "total_optimized_portfolios": total_runs,
            "solver_success_rate_pct": round(optimal_count / total_runs * 100.0, 2),
            "average_drift_before": round(float(np.mean(drift_befores)), 4),
            "average_drift_after": round(float(np.mean(drift_afters)), 4),
            "average_drift_reduction_pct": round(drift_reduction_pct, 2),
            "average_tracking_error_before": round(float(np.mean(te_befores)), 4),
            "average_tracking_error_after": round(float(np.mean(te_afters)), 4),
            "average_tracking_error_reduction_pct": round(te_reduction_pct, 2),
            "average_portfolio_turnover_pct": round(float(np.mean(turnovers)) * 100.0, 2),
            "total_trades_generated": total_trades,
            "total_estimated_transaction_costs": round(total_costs, 2),
            "total_estimated_tax_impact": round(total_taxes, 2),
        }
