"""Domain models for portfolio optimization results and constraint violation reports."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum
from src.models.execution_plan import ExecutionPlan
from src.models.trade import Trade


class OptimizationStrategy(StrEnum):
    """Portfolio optimization strategy types."""

    MIN_DRIFT = "Minimum Drift"
    MIN_COST = "Minimum Cost"
    BALANCED = "Balanced"
    TAX_OPTIMIZED = "Tax Optimized"


class ConstraintViolation(BaseModel):
    """Record of a portfolio constraint boundary violation."""

    constraint_name: str = Field(..., description="Name of violated constraint")
    description: str = Field(..., description="Detailed description of violation")
    severity: str = Field(..., description="Violation severity: WARNING or ERROR")
    current_value: float = Field(..., description="Observed portfolio metric value")
    allowed_limit: float = Field(..., description="Maximum or minimum allowed threshold")


class OptimizationResult(BaseModel):
    """Complete output result from portfolio optimization engine."""

    optimization_id: str = Field(..., description="Unique optimization run ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    strategy: OptimizationStrategy = Field(..., description="Optimization strategy used")
    solver_status: str = Field(..., description="Solver convergence status (e.g. OPTIMAL, FEASIBLE)")
    optimization_time_seconds: float = Field(..., ge=0.0, description="Solve execution duration in seconds")
    tracking_error_before: float = Field(..., ge=0.0, description="Pre-optimization tracking error")
    tracking_error_after: float = Field(..., ge=0.0, description="Post-optimization tracking error")
    drift_score_before: float = Field(..., ge=0.0, description="Pre-optimization RMS drift score")
    drift_score_after: float = Field(..., ge=0.0, description="Post-optimization RMS drift score")
    turnover: float = Field(..., ge=0.0, le=1.0, description="Total portfolio turnover percentage")
    total_estimated_cost: float = Field(..., ge=0.0, description="Total estimated transaction fees")
    total_tax_impact: float = Field(..., description="Total estimated tax liability/savings")
    optimized_weights: Dict[str, float] = Field(..., description="Optimized target weights by asset category")
    security_target_weights: Dict[str, float] = Field(default_factory=dict, description="Optimized security-level weights")
    trades: List[Trade] = Field(default_factory=list, description="Generated executable trade list")
    execution_plan: Optional[ExecutionPlan] = Field(default=None, description="Trade execution plan")
    constraint_violations: List[ConstraintViolation] = Field(default_factory=list, description="List of constraint violations")
