"""Structured task context and result communication models between agents."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class TaskStatus(StrEnum):
    """Task execution status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


class TaskResult(BaseModel):
    """Structured result returned by an agent upon task execution."""

    task_id: str = Field(..., description="Unique task execution ID")
    agent_name: str = Field(..., description="Name of executing agent")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Task input parameters")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Structured agent findings")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Agent confidence rating (0.0 - 1.0)")
    status: TaskStatus = Field(default=TaskStatus.COMPLETED, description="Task status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Execution timestamp")
    recommendation: str = Field(default="APPROVE", description="Agent recommendation: APPROVE, REJECT, or MODIFY")
    comments: str = Field(default="", description="Explanatory notes from agent")


class AgentContext(BaseModel):
    """Context wrapper passed across sequential agent handoffs."""

    portfolio_id: str = Field(..., description="Portfolio ID")
    client_id: str = Field(..., description="Client ID")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Shared context parameters")
