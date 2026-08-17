"""Handoff Manager managing typed context handoffs between sequential agents."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.core.logger import get_logger
from src.memory.agent_context import AgentContext, TaskResult

logger = get_logger(__name__)


class HandoffPacket(BaseModel):
    """Structured handoff packet passed from sender agent to receiver agent."""

    sender_agent: str = Field(..., description="Agent transferring context")
    receiver_agent: str = Field(..., description="Target receiving agent")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    payload: Dict[str, Any] = Field(..., description="Structured payload dictionary")
    previous_task_result: Optional[TaskResult] = Field(default=None, description="Previous task result object")


class HandoffManager:
    """Enterprise handoff manager transferring structured context packets across agents."""

    def create_handoff(
        self,
        sender: str,
        receiver: str,
        portfolio_id: str,
        payload: Dict[str, Any],
        previous_result: Optional[TaskResult] = None,
    ) -> HandoffPacket:
        """Create a validated HandoffPacket.

        Args:
            sender: Sending agent name.
            receiver: Receiving agent name.
            portfolio_id: Target portfolio ID.
            payload: Payload context.
            previous_result: Optional TaskResult from previous step.

        Returns:
            HandoffPacket instance.
        """
        logger.debug(f"Handoff created: [{sender}] ---> [{receiver}] for portfolio {portfolio_id}")
        return HandoffPacket(
            sender_agent=sender,
            receiver_agent=receiver,
            portfolio_id=portfolio_id,
            payload=payload,
            previous_task_result=previous_result,
        )
