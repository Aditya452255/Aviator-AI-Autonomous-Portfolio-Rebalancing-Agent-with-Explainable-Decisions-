"""Domain models for trade execution plans and algorithmic order slicing."""

from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class ExecutionStrategy(StrEnum):
    """Algorithmic execution strategy."""

    SINGLE_IMMEDIATE = "Single Immediate"
    TWAP = "TWAP (Time-Weighted Average Price)"
    VWAP = "VWAP (Volume-Weighted Average Price)"
    MULTI_DAY = "Multi-Day Staged"


class ExecutionSlice(BaseModel):
    """Single algorithmic order slice within an execution plan."""

    slice_id: str = Field(..., description="Unique slice identifier")
    slice_index: int = Field(..., ge=1, description="Slice sequence index")
    time_window: str = Field(..., description="Time window for slice execution (e.g. 09:30-10:00)")
    quantity_pct: float = Field(..., ge=0.0, le=1.0, description="Percentage of total trade quantity")
    target_shares: float = Field(..., ge=0.0, description="Shares to execute in this slice")
    estimated_impact_bps: float = Field(default=0.0, description="Estimated market impact in basis points")


class ExecutionPlan(BaseModel):
    """Comprehensive execution plan for executing portfolio rebalancing trades."""

    plan_id: str = Field(..., description="Unique execution plan ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    strategy: ExecutionStrategy = Field(..., description="Selected execution strategy")
    execution_window: str = Field(..., description="Total execution window duration (e.g. '1 Day' or '3 Days')")
    trade_priority: str = Field(..., description="Overall trade priority level")
    estimated_completion_minutes: float = Field(..., ge=0.0, description="Estimated completion time in minutes")
    execution_risk_rating: str = Field(..., description="Risk rating: LOW, MEDIUM, or HIGH")
    total_estimated_cost: float = Field(..., ge=0.0, description="Total estimated execution cost including impact")
    slices: List[ExecutionSlice] = Field(default_factory=list, description="Order slices")
