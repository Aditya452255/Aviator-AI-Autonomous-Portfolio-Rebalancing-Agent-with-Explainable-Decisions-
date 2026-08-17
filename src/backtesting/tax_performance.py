"""Tax Performance Evaluator assessing after-tax return alpha and loss harvesting efficiency."""

from typing import Dict, List
from src.core.logger import get_logger

logger = get_logger(__name__)


class TaxPerformanceEvaluator:
    """Enterprise Tax Performance Evaluator."""

    def evaluate_tax_alpha(
        self,
        gross_return: float,
        stcg_tax_paid: float,
        ltcg_tax_paid: float,
        harvested_losses: float,
        portfolio_value: float,
    ) -> Dict[str, float]:
        """Compute tax-adjusted return metrics and harvested loss alpha.

        Args:
            gross_return: Gross return fraction.
            stcg_tax_paid: Total STCG tax paid.
            ltcg_tax_paid: Total LTCG tax paid.
            harvested_losses: Total tax losses harvested.
            portfolio_value: Portfolio market value.

        Returns:
            Dictionary of tax performance findings.
        """
        tax_saved = harvested_losses * 0.20
        net_tax_impact = (stcg_tax_paid + ltcg_tax_paid) - tax_saved
        tax_drag_pct = net_tax_impact / max(1.0, portfolio_value)

        after_tax_return = gross_return - tax_drag_pct
        tax_alpha_bps = (tax_saved / max(1.0, portfolio_value)) * 10000.0

        return {
            "gross_return": round(gross_return, 4),
            "total_tax_paid": round(stcg_tax_paid + ltcg_tax_paid, 2),
            "total_tax_saved": round(tax_saved, 2),
            "net_tax_impact": round(net_tax_impact, 2),
            "after_tax_return": round(after_tax_return, 4),
            "tax_alpha_bps": round(tax_alpha_bps, 2),
        }
