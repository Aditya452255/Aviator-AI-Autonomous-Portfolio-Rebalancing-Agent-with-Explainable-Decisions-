"""Shared Workflow State tracking multi-agent execution context, history, and consensus."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum
from src.memory.agent_context import TaskResult


class WorkflowStatus(StrEnum):
    """Workflow execution state."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SharedWorkflowState(BaseModel):
    """Shared state object accessible to all agents during a decision cycle."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    client_id: str = Field(..., description="Target client ID")
    active_agent: str = Field(default="Orchestrator", description="Currently executing agent")
    workflow_status: WorkflowStatus = Field(default=WorkflowStatus.NOT_STARTED, description="Current workflow state")
    task_results: Dict[str, TaskResult] = Field(default_factory=dict, description="Map of agent_name -> TaskResult")
    execution_history: List[TaskResult] = Field(default_factory=list, description="Ordered history of executed tasks")
    consensus_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall multi-agent consensus rating")
    conflict_flag: bool = Field(default=False, description="True if unresolved conflict exists")
    conflict_notes: List[str] = Field(default_factory=list, description="Log of conflicts and resolution notes")

    def record_task_result(self, result: TaskResult) -> None:
        """Add task result to execution history and agent outputs map.

        Args:
            result: TaskResult object.
        """
        self.task_results[result.agent_name] = result
        self.execution_history.append(result)
        self.active_agent = result.agent_name
