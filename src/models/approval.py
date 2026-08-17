"""Approval domain models defining approval levels and decisions."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class ApprovalLevel(StrEnum):
    """Approval level requirements."""

    INFORMATIONAL = "INFORMATIONAL"
    ADVISORY = "ADVISORY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"


class ApprovalRequest(BaseModel):
    """Structured request for advisor or manager approval."""

    request_id: str = Field(..., description="Unique approval request ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    decision_id: str = Field(..., description="Associated decision package ID")
    approval_level: ApprovalLevel = Field(..., description="Required approval level")
    reason: str = Field(..., description="Reason for required approval level")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Request creation timestamp")
    is_approved: bool = Field(default=False, description="True if approved")
    approved_by: Optional[str] = Field(default=None, description="Advisor or manager ID who approved")


class ApprovalDecision(BaseModel):
    """Recorded approval decision."""

    request_id: str = Field(..., description="Request ID")
    portfolio_id: str = Field(..., description="Portfolio ID")
    level: ApprovalLevel = Field(..., description="Approval level")
    status: str = Field(..., description="Status: APPROVED, REJECTED, ESCALATED")
    approver_id: str = Field(..., description="Approver ID")
    comments: str = Field(default="", description="Approver notes")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Decision timestamp")
