"""Unit tests for ConflictResolver agent disagreement handling."""

import pytest
from src.memory.agent_context import TaskResult, TaskStatus
from src.memory.shared_state import SharedWorkflowState
from src.validators.conflict_resolver import ConflictResolver
from src.workflows.task_factory import TaskFactory


def test_conflict_resolver_compliance_rejection() -> None:
    """Test strict compliance rejection override rule."""
    state = SharedWorkflowState(portfolio_id="PORT_TEST", client_id="CLT_TEST")

    res_comp = TaskFactory.create_task_result(
        agent_name="Compliance Officer",
        task_id="TSK_1",
        input_data={},
        output_data={},
        confidence_score=0.95,
        recommendation="REJECT",
        comments="Restricted security breach",
    )
    state.record_task_result(res_comp)

    resolver = ConflictResolver()
    state, notes = resolver.resolve_conflicts(state)

    assert state.conflict_flag is True
    assert any("Compliance Officer rejected" in n for n in notes)


def test_conflict_resolver_risk_tax_disagreement() -> None:
    """Test Risk vs Tax disagreement resolution."""
    state = SharedWorkflowState(portfolio_id="PORT_TEST", client_id="CLT_TEST")

    res_risk = TaskFactory.create_task_result(
        agent_name="Risk Manager",
        task_id="TSK_1",
        input_data={},
        output_data={},
        confidence_score=0.85,
        recommendation="MODIFY",
        comments="Overweight position",
    )
    res_tax = TaskFactory.create_task_result(
        agent_name="Tax Specialist",
        task_id="TSK_2",
        input_data={},
        output_data={},
        confidence_score=0.90,
        recommendation="APPROVE",
        comments="Tax loss harvesting opportunity",
    )

    state.record_task_result(res_risk)
    state.record_task_result(res_tax)

    resolver = ConflictResolver()
    state, notes = resolver.resolve_conflicts(state)

    assert any("Risk Manager recommended MODIFY" in n for n in notes)
