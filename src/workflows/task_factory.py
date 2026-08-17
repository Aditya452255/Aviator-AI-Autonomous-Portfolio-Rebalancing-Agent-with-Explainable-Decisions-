"""Task Factory constructing standardized TaskResult objects for agent communication."""

from datetime import datetime
from typing import Any, Dict
from src.memory.agent_context import TaskResult, TaskStatus


class TaskFactory:
    """Factory constructing validated TaskResult communication objects."""

    @staticmethod
    def create_task_result(
        agent_name: str,
        task_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        confidence_score: float,
        recommendation: str = "APPROVE",
        comments: str = "",
        status: TaskStatus = TaskStatus.COMPLETED,
    ) -> TaskResult:
        """Create a TaskResult object.

        Args:
            agent_name: Name of agent creating result.
            task_id: Task identifier.
            input_data: Input context parameters.
            output_data: Agent findings dictionary.
            confidence_score: Confidence rating (0.0 to 1.0).
            recommendation: APPROVE, REJECT, or MODIFY.
            comments: Explanatory notes.
            status: TaskStatus enum value.

        Returns:
            Validated TaskResult instance.
        """
        return TaskResult(
            task_id=task_id,
            agent_name=agent_name,
            input_data=input_data,
            output_data=output_data,
            confidence_score=round(float(confidence_score), 4),
            status=status,
            timestamp=datetime.now().isoformat(),
            recommendation=recommendation,
            comments=comments,
        )
