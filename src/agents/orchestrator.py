"""Orchestrator Agent directing workflow execution, resolving deadlocks, and building FinalDecisionPackage."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult, TaskStatus
from src.memory.decision_memory import ExecutionReadiness, FinalDecisionPackage
from src.memory.shared_state import SharedWorkflowState, WorkflowStatus
from src.models.client import ClientProfile
from src.models.optimization_result import OptimizationResult
from src.models.portfolio import Portfolio
from src.workflows.task_factory import TaskFactory

logger = get_logger(__name__)


class OrchestratorAgent:
    """Chief Investment Operations Orchestrator Agent directing multi-agent workflows."""

    def __init__(self, agent_config: Optional[Dict] = None) -> None:
        self.name = "Orchestrator"
        self.role = "Chief Investment Operations Orchestrator"
        self.confidence_threshold = 0.70

    def aggregate_decision_package(
        self,
        portfolio: Portfolio,
        opt_result: OptimizationResult,
        state: SharedWorkflowState,
        client: Optional[ClientProfile] = None,
    ) -> FinalDecisionPackage:
        """Aggregate all agent outputs into a unified FinalDecisionPackage.

        Args:
            portfolio: Portfolio instance.
            opt_result: OptimizationResult from Phase 3.
            state: SharedWorkflowState containing task results and consensus.
            client: Optional ClientProfile.

        Returns:
            Validated FinalDecisionPackage object.
        """
        decision_id = f"DEC_{portfolio.portfolio_id}"

        # Collect individual agent outputs
        analyst_res = state.task_results.get("Portfolio Analyst")
        risk_res = state.task_results.get("Risk Manager")
        tax_res = state.task_results.get("Tax Specialist")
        comp_res = state.task_results.get("Compliance Officer")
        expl_res = state.task_results.get("Explanation Writer")

        # Determine overall recommendation
        recs = [r.recommendation for r in state.task_results.values()]
        if "REJECT" in recs:
            overall_rec = "REJECT"
            readiness = ExecutionReadiness.BLOCKED_COMPLIANCE
        elif "MODIFY" in recs:
            overall_rec = "MODIFIED_EXECUTE"
            readiness = ExecutionReadiness.NEEDS_REVIEW
        else:
            overall_rec = "EXECUTE"
            readiness = ExecutionReadiness.READY

        # Calculate average confidence score
        conf_scores = [r.confidence_score for r in state.task_results.values()]
        avg_confidence = float(sum(conf_scores) / len(conf_scores)) if conf_scores else 0.85

        explanations = expl_res.output_data if expl_res else {
            "client_explanation": "Rebalancing decision package prepared.",
            "advisor_explanation": "Rebalancing decision package prepared.",
            "compliance_explanation": "Rebalancing decision package prepared.",
        }

        package = FinalDecisionPackage(
            decision_id=decision_id,
            portfolio_id=portfolio.portfolio_id,
            client_id=portfolio.client_id,
            timestamp=datetime.now().isoformat(),
            recommendation=overall_rec,
            consensus_score=state.consensus_score,
            confidence_score=round(avg_confidence, 4),
            execution_readiness=readiness,
            portfolio_summary={
                "portfolio_id": portfolio.portfolio_id,
                "client_id": portfolio.client_id,
                "risk_category": portfolio.risk_category.value if hasattr(portfolio.risk_category, "value") else str(portfolio.risk_category),
                "total_market_value": portfolio.total_market_value,
                "cash_balance": portfolio.cash_balance,
            },
            optimization_summary={
                "strategy": opt_result.strategy.value if hasattr(opt_result.strategy, "value") else str(opt_result.strategy),
                "solver_status": opt_result.solver_status,
                "drift_before": opt_result.drift_score_before,
                "drift_after": opt_result.drift_score_after,
                "turnover": opt_result.turnover,
                "trades_count": len(opt_result.trades),
                "total_cost": opt_result.total_estimated_cost,
                "total_tax": opt_result.total_tax_impact,
            },
            risk_summary=risk_res.output_data if risk_res else {},
            tax_summary=tax_res.output_data if tax_res else {},
            compliance_summary=comp_res.output_data if comp_res else {},
            explanations={
                "client_explanation": explanations.get("client_explanation", ""),
                "advisor_explanation": explanations.get("advisor_explanation", ""),
                "compliance_explanation": explanations.get("compliance_explanation", ""),
            },
            agent_outputs=state.task_results,
        )

        return package
