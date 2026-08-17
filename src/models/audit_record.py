"""Audit record domain models for event sourcing and regulatory audit trails."""

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class AuditEventType(StrEnum):
    """Types of auditable decision lifecycle events."""

    CREATED = "CREATED"
    OPTIMIZATION = "OPTIMIZATION"
    AGENT_EXECUTION = "AGENT_EXECUTION"
    EXPLAINABILITY = "EXPLAINABILITY"
    APPROVAL = "APPROVAL"
    OVERRIDE = "OVERRIDE"
    EXECUTION_STATUS = "EXECUTION_STATUS"
    FINAL_OUTCOME = "FINAL_OUTCOME"


class AuditRecord(BaseModel):
    """Immutable audit record entry."""

    audit_id: str = Field(..., description="Unique audit record ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    decision_id: str = Field(..., description="Associated decision package ID")
    event_type: AuditEventType = Field(..., description="Event classification")
    event_summary: str = Field(..., description="Summary string of event")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed event payload")
    actor: str = Field(default="SYSTEM", description="Actor triggering event (e.g. System, Agent, Advisor)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Event timestamp")
