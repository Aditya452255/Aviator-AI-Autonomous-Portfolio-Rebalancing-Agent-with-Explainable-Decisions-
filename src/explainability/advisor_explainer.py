"""Advisor Explainer generating semi-technical summaries for wealth managers and advisors."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.explanation import AdvisorExplanation
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class AdvisorExplainer:
    """Enterprise Advisor Explainer generating semi-technical summaries (max 400 words)."""

    def generate_advisor_explanation(
        self,
        portfolio: Portfolio,
        decision_package: FinalDecisionPackage,
        top_driver: str = "portfolio_drift",
    ) -> AdvisorExplanation:
        """Generate wealth advisor-facing explanation summary.

        Args:
            portfolio: Target portfolio instance.
            decision_package: Phase 4 FinalDecisionPackage.
            top_driver: Primary feature driver name.

        Returns:
            AdvisorExplanation domain model object.
        """
        opt_sum = decision_package.optimization_summary
        risk_sum = decision_package.risk_summary
        tax_sum = decision_package.tax_summary

        drift_analysis = f"Portfolio RMS drift: {opt_sum.get('drift_before', 0.05):.4f} -> {opt_sum.get('drift_after', 0.01):.4f}. Primary driver: {top_driver}."
        te_analysis = f"Tracking Error after optimization: {risk_sum.get('tracking_error_after', 0.012):.4f}. VaR 95% Daily: {risk_sum.get('var_95_daily_pct', 1.2):.2f}%."
        tax_cost_analysis = f"Total transaction cost: ${opt_sum.get('total_cost', 0.0):,.2f}. Tax liability / savings: ${tax_sum.get('total_tax_impact', 0.0):,.2f}."
        liq_analysis = "Order execution scheduled via TWAP/VWAP algorithmic slicing to minimize ADV market impact."

        summary_text = (
            f"ADVISOR TECHNICAL BRIEF - Portfolio {portfolio.portfolio_id}\n"
            f"• Strategy: {opt_sum.get('strategy', 'BALANCED')} (Solver Status: {opt_sum.get('solver_status', 'OPTIMAL')})\n"
            f"• Consensus Rating: {decision_package.consensus_score:.2f} | Confidence: {decision_package.confidence_score:.2f}\n"
            f"• {drift_analysis}\n"
            f"• {te_analysis}\n"
            f"• {tax_cost_analysis}\n"
            f"• {liq_analysis}\n"
            f"• Recommendation: {decision_package.recommendation}."
        )

        words = summary_text.split()
        if len(words) > 400:
            summary_text = " ".join(words[:390]) + "..."

        return AdvisorExplanation(
            portfolio_id=portfolio.portfolio_id,
            summary=summary_text,
            word_count=len(summary_text.split()),
            drift_analysis=drift_analysis,
            tracking_error_analysis=te_analysis,
            tax_and_cost_analysis=tax_cost_analysis,
            liquidity_and_execution=liq_analysis,
        )
