"""Unit tests for AuditTrail event recording and DecisionLifecycleManager."""

import pytest
from src.governance.audit_trail import AuditTrail
from src.governance.decision_lifecycle import DecisionLifecycleManager
from src.models.audit_record import AuditEventType
from src.models.decision_state import DecisionLifecycleState


def test_audit_trail_and_lifecycle() -> None:
    """Test recording immutable audit events and lifecycle state transitions."""
    audit = AuditTrail()
    rec = audit.record_event(
        portfolio_id="PORT_001",
        decision_id="DEC_001",
        event_type=AuditEventType.CREATED,
        event_summary="Decision created",
        actor="SYSTEM",
    )
    assert rec.portfolio_id == "PORT_001"
    assert len(audit.get_audit_trail_for_portfolio("PORT_001")) == 1

    lifecycle = DecisionLifecycleManager()
    hist = lifecycle.transition_state(
        portfolio_id="PORT_001",
        decision_id="DEC_001",
        target_state=DecisionLifecycleState.APPROVED,
        reason="Advisor signoff",
    )
    assert hist.current_state == DecisionLifecycleState.APPROVED
