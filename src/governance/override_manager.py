"""Override Manager handling advisor manual overrides and trade modifications."""

from typing import Any, Dict, List, Optional
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.memory.decision_memory import FinalDecisionPackage
from src.models.override import OverrideAction, OverrideRecord

logger = get_logger(__name__)


class OverrideManager:
    """Enterprise Override Manager capturing and enforcing advisor manual overrides."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self.override_history: Dict[str, OverrideRecord] = {}

    def execute_override(
        self,
        decision_package: FinalDecisionPackage,
        advisor_id: str,
        action: OverrideAction,
        reason_category: str,
        comments: str,
        modifications: Optional[Dict[str, Any]] = None,
    ) -> OverrideRecord:
        """Execute and log an advisor manual override action.

        Args:
            decision_package: Phase 4 FinalDecisionPackage.
            advisor_id: Advisor ID string.
            action: OverrideAction enum value (APPROVE, REJECT, MODIFY, DEFER, CANCEL).
            reason_category: Category string (e.g., CLIENT_REQUEST).
            comments: Explanatory notes.
            modifications: Optional dictionary of specific trade modifications.

        Returns:
            OverrideRecord instance.

        Raises:
            ValidationError: If mandatory comments or reason are missing.
        """
        if not comments or len(comments.strip()) < 5:
            raise ValidationError("Manual advisor override requires detailed comments (minimum 5 characters).")

        if not reason_category:
            raise ValidationError("Manual advisor override requires a valid reason_category.")

        override_id = f"OVR_{decision_package.portfolio_id}"

        # Determine modified recommendation string
        if action == OverrideAction.APPROVE:
            mod_rec = "EXECUTE"
        elif action == OverrideAction.REJECT or action == OverrideAction.CANCEL:
            mod_rec = "CANCELLED"
        elif action == OverrideAction.MODIFY:
            mod_rec = "MODIFIED_EXECUTE"
        elif action == OverrideAction.DEFER:
            mod_rec = "DEFERRED"
        else:
            mod_rec = action.value

        record = OverrideRecord(
            override_id=override_id,
            decision_id=decision_package.decision_id,
            portfolio_id=decision_package.portfolio_id,
            advisor_id=advisor_id,
            action=action,
            original_recommendation=decision_package.recommendation,
            modified_recommendation=mod_rec,
            reason_category=reason_category,
            comments=comments,
            modifications=modifications or {},
        )

        self.override_history[override_id] = record
        logger.info(
            f"Advisor Override Executed [{override_id}] by {advisor_id} | Action: {action.value} | "
            f"Original: {decision_package.recommendation} -> Modified: {mod_rec} | Reason: {reason_category}"
        )
        return record
