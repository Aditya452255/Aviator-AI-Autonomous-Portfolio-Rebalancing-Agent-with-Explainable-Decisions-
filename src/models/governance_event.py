"""Governance event domain models for safety stops and policy events."""

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class GovernanceEventType(StrEnum):
    """Types of governance safety events."""

    KILL_SWITCH_ACTIVATED = "KILL_SWITCH_ACTIVATED"
    KILL_SWITCH_DEACTIVATED = "KILL_SWITCH_DEACTIVATED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    COMPLIANCE_BREACH = "COMPLIANCE_BREACH"
    POLICY_VIOLATION = "POLICY_VIOLATION"


class GovernanceEvent(BaseModel):
    """Governance safety or policy event entry."""

    event_id: str = Field(..., description="Unique event ID")
    event_type: GovernanceEventType = Field(..., description="Type of governance event")
    severity: str = Field(default="HIGH", description="Severity level: INFO, WARNING, HIGH, CRITICAL")
    description: str = Field(..., description="Detailed description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual parameters")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Event timestamp")
