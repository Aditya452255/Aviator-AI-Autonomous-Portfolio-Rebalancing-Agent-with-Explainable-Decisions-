"""Aggregator helper converting portfolio drift metrics to structured DataFrames."""

from typing import List
import pandas as pd
from src.models.drift import PortfolioDriftMetrics


class DriftMetricsAggregator:
    """Aggregates a collection of PortfolioDriftMetrics into tabular DataFrames."""

    @staticmethod
    def to_dataframe(metrics_list: List[PortfolioDriftMetrics]) -> pd.DataFrame:
        """Convert list of PortfolioDriftMetrics objects to pandas DataFrame.

        Args:
            metrics_list: List of PortfolioDriftMetrics instances.

        Returns:
            Flat tabular DataFrame containing summary drift metrics per portfolio.
        """
        rows = []
        for m in metrics_list:
            eq_d = m.asset_drifts.get("Equity")
            fi_d = m.asset_drifts.get("Fixed Income")
            alt_d = m.asset_drifts.get("Alternatives")
            cash_d = m.asset_drifts.get("Cash")

            rows.append({
                "portfolio_id": m.portfolio_id,
                "client_id": m.client_id,
                "risk_category": m.risk_category,
                "total_absolute_drift": m.total_absolute_drift,
                "portfolio_drift_score": m.portfolio_drift_score,
                "cash_drift": m.cash_drift,
                "max_drift_asset_class": m.max_drift_asset_class,
                "max_drift_value": m.max_drift_value,
                "equity_drift": eq_d.absolute_drift if eq_d else 0.0,
                "equity_breached": eq_d.is_breached if eq_d else False,
                "fixed_income_drift": fi_d.absolute_drift if fi_d else 0.0,
                "fixed_income_breached": fi_d.is_breached if fi_d else False,
                "alternatives_drift": alt_d.absolute_drift if alt_d else 0.0,
                "cash_drift_abs": cash_d.absolute_drift if cash_d else 0.0,
                "is_rebalance_candidate": m.is_rebalance_candidate,
            })

        return pd.DataFrame(rows)
