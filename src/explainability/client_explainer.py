"""Client Explainer generating plain-English, non-technical summaries for retail investors."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.explanation import ClientExplanation
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class ClientExplainer:
    """Enterprise Client Explainer generating plain-English summaries (max 200 words)."""

    def generate_client_explanation(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
        top_driver: str = "portfolio_drift",
    ) -> ClientExplanation:
        """Generate client-facing explanation summary.

        Args:
            portfolio: Target portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.
            top_driver: Primary feature driver name.

        Returns:
            ClientExplanation domain model object.
        """
        opt_sum = decision_package.optimization_summary
        drift_bef = opt_sum.get("drift_before", 0.05)
        drift_aft = opt_sum.get("drift_after", 0.01)
        cost_val = opt_sum.get("total_cost", 0.0)
        tax_val = opt_sum.get("total_tax", 0.0)
        trades_cnt = opt_sum.get("trades_count", 0)

        summary_text = (
            f"Aviator AI conducted a health check on your portfolio. "
            f"Market price movements caused your investments to drift away from your target asset allocation. "
            f"To keep your portfolio aligned with your long-term financial goals and risk tolerance, "
            f"our automated agent recommended executing {trades_cnt} rebalancing transactions."
        )

        benefits_text = f"Reduces portfolio drift from {drift_bef:.1%} to {drift_aft:.1%}, maintaining risk discipline."
        costs_text = f"Estimated transaction cost is ${cost_val:,.2f} with estimated tax impact of ${tax_val:,.2f}."
        risks_text = "Maintains diversification while protecting against unmanaged market exposure."

        full_text = f"{summary_text} {benefits_text} {costs_text} {risks_text}"
        words = full_text.split()
        if len(words) > 200:
            summary_text = " ".join(words[:190]) + "..."

        return ClientExplanation(
            portfolio_id=portfolio.portfolio_id,
            summary=summary_text,
            word_count=len(summary_text.split()),
            benefits=benefits_text,
            costs_and_taxes=costs_text,
            risks=risks_text,
        )
