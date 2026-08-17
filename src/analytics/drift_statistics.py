"""Drift Statistics generator computing summary metrics, distribution quantiles, and top drifted portfolios."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from src.core.logger import get_logger
from src.models.drift import PortfolioDriftMetrics

logger = get_logger(__name__)


class DriftStatistics:
    """Enterprise analytics engine for drift statistics and distribution analysis."""

    def compute_summary_statistics(self, metrics_list: List[PortfolioDriftMetrics]) -> Dict[str, Any]:
        """Calculate statistical distribution metrics for portfolio drift scores.

        Args:
            metrics_list: List of PortfolioDriftMetrics instances.

        Returns:
            Dictionary containing average drift, max drift, distribution quantiles, and count totals.
        """
        if not metrics_list:
            return {"total_portfolios": 0}

        drift_scores = np.array([m.portfolio_drift_score for m in metrics_list])
        total_abs_drifts = np.array([m.total_absolute_drift for m in metrics_list])

        quantiles = np.quantile(drift_scores, [0.25, 0.50, 0.75, 0.90, 0.95, 0.99])

        return {
            "total_portfolios_scanned": len(metrics_list),
            "rebalance_candidates_count": sum(1 for m in metrics_list if m.is_rebalance_candidate),
            "rebalance_candidates_pct": round(sum(1 for m in metrics_list if m.is_rebalance_candidate) / len(metrics_list) * 100.0, 2),
            "average_portfolio_drift_score": round(float(np.mean(drift_scores)), 4),
            "median_portfolio_drift_score": round(float(np.median(drift_scores)), 4),
            "maximum_portfolio_drift_score": round(float(np.max(drift_scores)), 4),
            "minimum_portfolio_drift_score": round(float(np.min(drift_scores)), 4),
            "std_dev_drift_score": round(float(np.std(drift_scores)), 4),
            "average_total_absolute_drift": round(float(np.mean(total_abs_drifts)), 4),
            "drift_score_quantiles": {
                "p25": round(float(quantiles[0]), 4),
                "p50_median": round(float(quantiles[1]), 4),
                "p75": round(float(quantiles[2]), 4),
                "p90": round(float(quantiles[3]), 4),
                "p95": round(float(quantiles[4]), 4),
                "p99": round(float(quantiles[5]), 4),
            },
        }

    def get_top_drifted_portfolios(self, metrics_list: List[PortfolioDriftMetrics], top_n: int = 100) -> pd.DataFrame:
        """Return the Top N most drifted portfolios sorted by drift score descending.

        Args:
            metrics_list: List of PortfolioDriftMetrics instances.
            top_n: Count of top drifted portfolios to return (default: 100).

        Returns:
            DataFrame containing Top N drifted portfolios.
        """
        sorted_metrics = sorted(metrics_list, key=lambda m: m.portfolio_drift_score, reverse=True)[:top_n]
        rows = []
        for rank, m in enumerate(sorted_metrics, start=1):
            rows.append({
                "rank": rank,
                "portfolio_id": m.portfolio_id,
                "client_id": m.client_id,
                "risk_category": m.risk_category,
                "portfolio_drift_score": m.portfolio_drift_score,
                "total_absolute_drift": m.total_absolute_drift,
                "cash_drift": m.cash_drift,
                "max_drift_asset_class": m.max_drift_asset_class,
                "max_drift_value": m.max_drift_value,
            })
        return pd.DataFrame(rows)
