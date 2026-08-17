"""Kill Switch safety control halting autonomous trade execution under critical system or market risk."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.models.governance_event import GovernanceEvent, GovernanceEventType

logger = get_logger(__name__)


class KillSwitch:
    """Enterprise Kill Switch emergency safety control."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        cfg = config or {}
        rules = cfg.get("kill_switch", {}).get("auto_trigger_rules", {})
        self.max_volatility = rules.get("max_market_volatility", 0.35)
        self.max_failure_rate = rules.get("max_failure_rate_pct", 10.0)
        self.max_compliance_breach_rate = rules.get("max_compliance_breach_rate_pct", 5.0)

        self.is_active = False
        self.activation_reason: Optional[str] = None
        self.events: List[GovernanceEvent] = []

    def activate_manually(self, operator_id: str, reason: str) -> GovernanceEvent:
        """Manually activate Kill Switch.

        Args:
            operator_id: Operator or Admin ID activating kill switch.
            reason: Reason description string.

        Returns:
            GovernanceEvent instance.
        """
        self.is_active = True
        self.activation_reason = f"Manual activation by {operator_id}: {reason}"

        evt = GovernanceEvent(
            event_id=f"KS_MANUAL_{len(self.events)+1}",
            event_type=GovernanceEventType.KILL_SWITCH_ACTIVATED,
            severity="CRITICAL",
            description=self.activation_reason,
            metadata={"operator_id": operator_id, "trigger_mode": "MANUAL"},
        )
        self.events.append(evt)
        logger.critical(f"KILL SWITCH MANUALLY ACTIVATED by {operator_id}! Reason: {reason}")
        return evt

    def evaluate_auto_triggers(
        self,
        market_volatility: float = 0.15,
        failure_rate_pct: float = 0.0,
        compliance_breach_pct: float = 0.0,
    ) -> bool:
        """Evaluate automatic kill switch rules based on system metrics.

        Args:
            market_volatility: Current market volatility score.
            failure_rate_pct: System execution failure rate %.
            compliance_breach_pct: Compliance breach rate %.

        Returns:
            True if kill switch was automatically activated.
        """
        if self.is_active:
            return True

        trigger_reason = None
        if market_volatility >= self.max_volatility:
            trigger_reason = f"Excessive market volatility ({market_volatility:.1%} >= {self.max_volatility:.1%})"
        elif failure_rate_pct >= self.max_failure_rate:
            trigger_reason = f"High system failure rate ({failure_rate_pct:.1f}% >= {self.max_failure_rate:.1f}%)"
        elif compliance_breach_pct >= self.max_compliance_breach_rate:
            trigger_reason = f"Compliance breach rate exceeded limit ({compliance_breach_pct:.1f}% >= {self.max_compliance_breach_rate:.1f}%)"

        if trigger_reason:
            self.is_active = True
            self.activation_reason = f"Automatic activation: {trigger_reason}"
            evt = GovernanceEvent(
                event_id=f"KS_AUTO_{len(self.events)+1}",
                event_type=GovernanceEventType.KILL_SWITCH_ACTIVATED,
                severity="CRITICAL",
                description=self.activation_reason,
                metadata={"trigger_mode": "AUTOMATIC"},
            )
            self.events.append(evt)
            logger.critical(f"KILL SWITCH AUTOMATICALLY ACTIVATED! Reason: {trigger_reason}")
            return True

        return False

    def deactivate(self, operator_id: str, reason: str) -> GovernanceEvent:
        """Deactivate Kill Switch and restore normal execution.

        Args:
            operator_id: Operator or Admin ID.
            reason: Reason string.

        Returns:
            GovernanceEvent instance.
        """
        self.is_active = False
        self.activation_reason = None

        evt = GovernanceEvent(
            event_id=f"KS_DEACT_{len(self.events)+1}",
            event_type=GovernanceEventType.KILL_SWITCH_DEACTIVATED,
            severity="INFO",
            description=f"Kill Switch deactivated by {operator_id}: {reason}",
            metadata={"operator_id": operator_id},
        )
        self.events.append(evt)
        logger.info(f"KILL SWITCH DEACTIVATED by {operator_id}. Normal execution restored.")
        return evt
