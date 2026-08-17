"""Decision Memory module storing unified decision packages and consensus records."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum
from src.memory.agent_context import TaskResult

logger = get_logger = None  # Lazy init if needed


class ExecutionReadiness(StrEnum):
    """Execution readiness status."""

    READY = "READY"
    BLOCKED_COMPLIANCE = "BLOCKED_COMPLIANCE"
    BLOCKED_RISK = "BLOCKED_RISK"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class FinalDecisionPackage(BaseModel):
    """Unified multi-agent decision package containing complete analysis and explainability outputs."""

    decision_id: str = Field(..., description="Unique decision package ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    client_id: str = Field(..., description="Target client ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Package generation timestamp")
    recommendation: str = Field(..., description="Overall decision: EXECUTE, REJECT, or MODIFIED_EXECUTE")
    consensus_score: float = Field(..., ge=0.0, le=1.0, description="Multi-agent consensus rating (0.0 - 1.0)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall decision confidence rating")
    execution_readiness: ExecutionReadiness = Field(..., description="Execution readiness state")

    portfolio_summary: Dict[str, Any] = Field(..., description="Portfolio & drift summary")
    optimization_summary: Dict[str, Any] = Field(..., description="CVXPY optimization & trade summary")
    risk_summary: Dict[str, Any] = Field(..., description="VaR, tracking error, and stress risk summary")
    tax_summary: Dict[str, Any] = Field(..., description="STCG/LTCG & tax loss harvesting summary")
    compliance_summary: Dict[str, Any] = Field(..., description="Constraint and ESG compliance check summary")
    explanations: Dict[str, str] = Field(..., description="Structured Client, Advisor, and Compliance text explanations")
    agent_outputs: Dict[str, TaskResult] = Field(default_factory=dict, description="Raw agent task results")


class DecisionMemory:
    """In-memory persistent store for historical decision packages."""

    def __init__(self) -> None:
        self.history: Dict[str, FinalDecisionPackage] = {}

    def store_decision(self, package: FinalDecisionPackage) -> None:
        """Store decision package in memory.

        Args:
            package: FinalDecisionPackage instance.
        """
        self.history[package.decision_id] = package

    def get_decision(self, decision_id: str) -> Optional[FinalDecisionPackage]:
        """Retrieve decision package by ID.

        Args:
            decision_id: Package ID.

        Returns:
            FinalDecisionPackage if found.
        """
        return self.history.get(decision_id)

    def list_decisions_for_portfolio(self, portfolio_id: str) -> List[FinalDecisionPackage]:
        """Get all historical decision packages for a portfolio.

        Args:
            portfolio_id: Portfolio ID.

        Returns:
            List of matching FinalDecisionPackage objects.
        """
        return [p for p in self.history.values() if p.portfolio_id == portfolio_id]
