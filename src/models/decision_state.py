"""Decision lifecycle state domain models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class DecisionLifecycleState(StrEnum):
    """Decision lifecycle states."""

    CREATED = "CREATED"
    UNDER_REVIEW = "UNDER_REVIEW"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"


class DecisionStateHistory(BaseModel):
    """State transition history entry."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    decision_id: str = Field(..., description="Target decision package ID")
    current_state: DecisionLifecycleState = Field(..., description="Current state")
    previous_state: Optional[DecisionLifecycleState] = Field(default=None, description="Previous state")
    reason: str = Field(default="", description="State change transition reason")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Transition timestamp")
