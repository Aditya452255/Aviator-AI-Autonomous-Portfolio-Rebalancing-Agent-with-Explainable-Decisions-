"""Override domain models defining advisor override actions and records."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class OverrideAction(StrEnum):
    """Advisor manual override action."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"
    DEFER = "DEFER"
    CANCEL = "CANCEL"


class OverrideRecord(BaseModel):
    """Complete record of an advisor manual override."""

    override_id: str = Field(..., description="Unique override record ID")
    decision_id: str = Field(..., description="Target decision package ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    advisor_id: str = Field(..., description="Advisor ID executing override")
    action: OverrideAction = Field(..., description="Override action taken")
    original_recommendation: str = Field(..., description="Original AI recommendation")
    modified_recommendation: str = Field(..., description="Final modified recommendation")
    reason_category: str = Field(..., description="Category of override (e.g., CLIENT_REQUEST)")
    comments: str = Field(..., description="Mandatory detailed comments")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Override timestamp")
    modifications: Dict[str, Any] = Field(default_factory=dict, description="Specific trade or weight modifications")
