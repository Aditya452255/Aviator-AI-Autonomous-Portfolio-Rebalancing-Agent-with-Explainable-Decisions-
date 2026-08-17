"""Domain models for rebalancing queue requests and system alerts."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum
from src.models.trigger import TriggerReason, TriggerType


class PriorityLevel(StrEnum):
    """Rebalancing request priority levels."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class QueueStatus(StrEnum):
    """State of request in rebalancing workflow queue."""

    PENDING = "Pending"
    VALIDATED = "Validated"
    REJECTED = "Rejected"
    IN_OPTIMIZATION = "In Optimization"
    COMPLETED = "Completed"


class AlertSeverity(StrEnum):
    """Alert severity level."""

    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"


class AlertCategory(StrEnum):
    """Category of generated system alert."""

    CRITICAL_DRIFT = "Critical Drift"
    LARGE_CASH_ALLOCATION = "Large Cash Allocation"
    SECTOR_CONCENTRATION = "Sector Concentration"
    MARKET_EVENT = "Market Event"
    MISSED_REBALANCE = "Missed Rebalance"


class RebalancingRequest(BaseModel):
    """Validated rebalancing queue entry for downstream optimization."""

    request_id: str = Field(..., description="Unique request identifier (e.g. REQ_00001)")
    portfolio_id: str = Field(..., description="Target portfolio identifier")
    client_id: str = Field(..., description="Target client identifier")
    priority: PriorityLevel = Field(..., description="Assigned priority level")
    priority_score: float = Field(..., ge=0.0, le=1.0, description="Normalized multi-factor priority score (0.0 - 1.0)")
    trigger_type: TriggerType = Field(..., description="Primary trigger type")
    trigger_reason: TriggerReason = Field(..., description="Primary trigger reason")
    all_triggers: List[str] = Field(default_factory=list, description="List of all fired trigger reasons")
    drift_summary: Dict[str, Any] = Field(..., description="Summary of key drift metrics")
    timestamp: str = Field(..., description="Creation timestamp in ISO format")
    validation_status: bool = Field(default=True, description="Validation check status")
    queue_status: QueueStatus = Field(default=QueueStatus.VALIDATED, description="Workflow state")


class AlertObject(BaseModel):
    """Structured alert record generated during monitoring cycle."""

    alert_id: str = Field(..., description="Unique alert identifier")
    portfolio_id: str = Field(..., description="Associated portfolio ID")
    client_id: str = Field(..., description="Associated client ID")
    category: AlertCategory = Field(..., description="Alert category")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    title: str = Field(..., description="Alert headline summary")
    description: str = Field(..., description="Detailed alert explanation")
    timestamp: str = Field(..., description="Generation timestamp in ISO format")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual metrics")
