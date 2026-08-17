"""Allocation Analyzer comparing current vs target allocations across portfolios."""

from typing import Dict, List
import pandas as pd

from src.core.constants import AssetCategory
from src.core.logger import get_logger
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class AllocationAnalyzer:
    """Enterprise analyzer comparing target and current asset allocations."""

    def analyze_portfolio_allocation(self, portfolio: Portfolio) -> pd.DataFrame:
        """Compare current vs target allocation for a single portfolio.

        Args:
            portfolio: Portfolio domain model object.

        Returns:
            DataFrame showing Category, Target Weight, Current Weight, Difference, % Drift.
        """
        rows = []
        for cat in AssetCategory:
            cat_name = cat.value
            target_w = portfolio.target_weights.get(cat_name, 0.0)
            current_w = portfolio.current_weights.get(cat_name, 0.0)
            diff = current_w - target_w
            pct_drift = (diff / target_w * 100.0) if target_w > 0 else 0.0

            rows.append({
                "portfolio_id": portfolio.portfolio_id,
                "asset_category": cat_name,
                "target_weight": round(target_w, 4),
                "current_weight": round(current_w, 4),
                "weight_difference": round(diff, 4),
                "pct_drift": round(pct_drift, 2),
            })

        return pd.DataFrame(rows)

    def analyze_universe_allocation(self, portfolios: List[Portfolio]) -> Dict[str, pd.DataFrame]:
        """Generate universe-level target vs current allocation summaries by risk category.

        Args:
            portfolios: List of Portfolio objects.

        Returns:
            Dict mapping risk category key to summary comparison DataFrame.
        """
        port_by_risk: Dict[str, List[Portfolio]] = {}
        for p in portfolios:
            risk_key = p.risk_category.value if hasattr(p.risk_category, "value") else str(p.risk_category)
            if risk_key not in port_by_risk:
                port_by_risk[risk_key] = []
            port_by_risk[risk_key].append(p)

        summaries: Dict[str, pd.DataFrame] = {}
        for risk_key, p_list in port_by_risk.items():
            records = []
            for cat in AssetCategory:
                cat_name = cat.value
                avg_tgt = float(pd.Series([p.target_weights.get(cat_name, 0.0) for p in p_list]).mean())
                avg_curr = float(pd.Series([p.current_weights.get(cat_name, 0.0) for p in p_list]).mean())
                avg_diff = avg_curr - avg_tgt

                records.append({
                    "risk_category": risk_key,
                    "asset_category": cat_name,
                    "avg_target_weight": round(avg_tgt, 4),
                    "avg_current_weight": round(avg_curr, 4),
                    "avg_difference": round(avg_diff, 4),
                })

            summaries[risk_key] = pd.DataFrame(records)

        return summaries
