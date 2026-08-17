"""Escalation Manager routing decisions requiring senior review or compliance intervention."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.governance_event import GovernanceEvent, GovernanceEventType

logger = get_logger(__name__)


class EscalationManager:
    """Enterprise Escalation Manager routing high-risk or conflicting decisions."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.escalations: List[GovernanceEvent] = []

    def evaluate_and_escalate(
        self,
        decision_package: FinalDecisionPackage,
        kill_switch_active: bool = False,
    ) -> Optional[GovernanceEvent]:
        """Evaluate decision package and trigger escalation if necessary.

        Args:
            decision_package: Phase 4 FinalDecisionPackage.
            kill_switch_active: True if system kill switch is active.

        Returns:
            GovernanceEvent if escalated, None otherwise.
        """
        esc_reason = None
        severity = "HIGH"

        if kill_switch_active:
            esc_reason = "System Kill Switch is active. All autonomous executions halted."
            severity = "CRITICAL"
        elif decision_package.recommendation == "REJECT":
            esc_reason = "Compliance or risk agent issued REJECT recommendation."
            severity = "HIGH"
        elif decision_package.confidence_score < 0.70:
            esc_reason = f"Decision confidence score ({decision_package.confidence_score:.2f}) is below minimum threshold 0.70."
            severity = "MEDIUM"
        elif decision_package.consensus_score < 0.75:
            esc_reason = f"Agent consensus rating ({decision_package.consensus_score:.2f}) indicates agent disagreement."
            severity = "MEDIUM"

        if esc_reason:
            evt_id = f"ESC_{decision_package.portfolio_id}"
            event = GovernanceEvent(
                event_id=evt_id,
                event_type=GovernanceEventType.ESCALATION_TRIGGERED,
                severity=severity,
                description=esc_reason,
                metadata={
                    "portfolio_id": decision_package.portfolio_id,
                    "decision_id": decision_package.decision_id,
                    "recommendation": decision_package.recommendation,
                },
            )
            self.escalations.append(event)
            logger.warning(f"ESCALATION TRIGGERED [{evt_id}] | Severity: {severity} | Reason: {esc_reason}")
            return event

        return None
