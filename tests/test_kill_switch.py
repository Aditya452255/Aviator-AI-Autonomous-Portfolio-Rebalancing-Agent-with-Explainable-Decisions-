"""Unit tests for KillSwitch safety controls."""

import pytest
from src.governance.kill_switch import KillSwitch


def test_kill_switch_manual_and_auto_activation() -> None:
    """Test manual and automatic activation of Kill Switch safety stops."""
    ks = KillSwitch()

    assert ks.is_active is False

    # Auto-trigger test: High market volatility
    triggered = ks.evaluate_auto_triggers(market_volatility=0.40)
    assert triggered is True
    assert ks.is_active is True
    assert len(ks.events) == 1

    # Deactivate
    ks.deactivate(operator_id="ADMIN_01", reason="Volatility returned to normal level.")
    assert ks.is_active is False

    # Manual trigger test
    ks.activate_manually(operator_id="ADMIN_01", reason="Emergency market halt.")
    assert ks.is_active is True
