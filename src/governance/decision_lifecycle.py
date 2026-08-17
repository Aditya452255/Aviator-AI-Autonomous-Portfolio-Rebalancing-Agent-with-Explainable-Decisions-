"""Decision Lifecycle Manager tracking decision state machine transitions."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.models.decision_state import DecisionLifecycleState, DecisionStateHistory

logger = get_logger(__name__)


class DecisionLifecycleManager:
    """Enterprise state transition manager tracking decision lifecycle states."""

    def __init__(self) -> None:
        self.state_history: List[DecisionStateHistory] = []
        self.current_states: Dict[str, DecisionLifecycleState] = {}

    def transition_state(
        self,
        portfolio_id: str,
        decision_id: str,
        target_state: DecisionLifecycleState,
        reason: str = "",
    ) -> DecisionStateHistory:
        """Transition decision to new lifecycle state and record history.

        Args:
            portfolio_id: Target portfolio ID.
            decision_id: Decision package ID.
            target_state: DecisionLifecycleState enum target.
            reason: Transition rationale string.

        Returns:
            DecisionStateHistory instance.
        """
        prev_state = self.current_states.get(decision_id, None)
        self.current_states[decision_id] = target_state

        history_entry = DecisionStateHistory(
            portfolio_id=portfolio_id,
            decision_id=decision_id,
            current_state=target_state,
            previous_state=prev_state,
            reason=reason,
        )
        self.state_history.append(history_entry)

        logger.info(
            f"Decision State Transition [{decision_id}] | "
            f"{prev_state.value if prev_state else 'NONE'} ---> {target_state.value} | Reason: {reason}"
        )
        return history_entry
