"""Return Metrics Calculator computing Gross, Net, and After-Tax returns."""

from typing import Dict
from src.core.logger import get_logger
from src.models.performance_metrics import ReturnAnalysisModel

logger = get_logger(__name__)


class ReturnMetricsCalculator:
    """Enterprise Return Metrics Calculator computing net and tax-adjusted returns."""

    def compute_return_breakdown(
        self,
        gross_cagr: float,
        total_costs: float,
        total_taxes: float,
        portfolio_value: float,
    ) -> ReturnAnalysisModel:
        """Compute return breakdown metrics.

        Args:
            gross_cagr: Gross CAGR before fees and taxes.
            total_costs: Cumulative transaction costs.
            total_taxes: Cumulative tax liabilities.
            portfolio_value: Total portfolio market value.

        Returns:
            ReturnAnalysisModel instance.
        """
        cost_impact_pct = total_costs / max(1.0, portfolio_value)
        tax_impact_pct = max(0.0, total_taxes) / max(1.0, portfolio_value)
        tax_saved = abs(min(0.0, total_taxes))

        net_cagr = gross_cagr - cost_impact_pct
        after_tax_cagr = net_cagr - tax_impact_pct

        return ReturnAnalysisModel(
            gross_return_cagr=round(gross_cagr, 4),
            net_return_cagr=round(net_cagr, 4),
            after_tax_cagr=round(after_tax_cagr, 4),
            total_transaction_costs=round(total_costs, 2),
            total_tax_savings=round(tax_saved, 2),
        )
