"""Tax Specialist Agent evaluating tax lot selection, STCG/LTCG liabilities, and tax-loss harvesting."""

from typing import Any, Dict, Optional
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.task_factory import TaskFactory

logger = get_logger(__name__)


class TaxSpecialistAgent:
    """Enterprise Tax Optimization Specialist Agent analyzing tax efficiency."""

    def __init__(self, agent_config: Optional[Dict] = None) -> None:
        self.name = "Tax Specialist"
        self.role = "Enterprise Tax Optimization Specialist"
        self.confidence_threshold = 0.75

    def evaluate_tax(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        input_context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """Evaluate tax efficiency, STCG/LTCG impact, and tax loss harvesting.

        Args:
            portfolio: Portfolio instance.
            opt_result: OptimizationResult from Phase 3.
            input_context: Input context parameters.

        Returns:
            TaskResult containing tax analysis findings.
        """
        task_id = f"TSK_TAX_{portfolio.portfolio_id}"

        tax_impact = opt_result.total_tax_impact
        trade_count = len(opt_result.trades)

        # Evaluate tax efficiency
        if tax_impact <= 0:
            efficiency_score = 0.95
            tax_rating = "HIGHLY_EFFICIENT"
            recommendation = "APPROVE"
            comments = f"Tax loss harvesting or zero tax liability achieved (Net tax impact: {tax_impact:,.2f})."
        elif tax_impact < (portfolio.total_market_value * 0.01):
            efficiency_score = 0.85
            tax_rating = "MODERATE"
            recommendation = "APPROVE"
            comments = f"Modest tax liability ({tax_impact:,.2f}) within acceptable 1% threshold."
        else:
            efficiency_score = 0.65
            tax_rating = "SUB_OPTIMAL"
            recommendation = "MODIFY"
            comments = f"Higher tax liability ({tax_impact:,.2f}) detected. Recommend tax-efficient lot selection."

        output_data = {
            "portfolio_id": portfolio.portfolio_id,
            "total_tax_impact": tax_impact,
            "tax_rating": tax_rating,
            "tax_efficiency_score": efficiency_score,
            "harvested_loss_opportunity": abs(min(0.0, tax_impact)),
            "stcg_avoidance_status": "SUCCESS" if tax_impact <= 0 else "PARTIAL",
        }

        return TaskFactory.create_task_result(
            agent_name=self.name,
            task_id=task_id,
            input_data={"portfolio_id": portfolio.portfolio_id},
            output_data=output_data,
            confidence_score=efficiency_score,
            recommendation=recommendation,
            comments=comments,
        )
