"""Conflict Resolver resolving agent disagreements, compliance rejections, and deadlocks."""

from typing import Dict, List, Tuple
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult
from src.memory.shared_state import SharedWorkflowState

logger = get_logger(__name__)


class ConflictResolver:
    """Enterprise conflict resolver resolving agent disagreements automatically or marking escalation."""

    def resolve_conflicts(self, state: SharedWorkflowState) -> Tuple[SharedWorkflowState, List[str]]:
        """Identify and resolve recommendation conflicts across agent results.

        Args:
            state: SharedWorkflowState instance.

        Returns:
            Tuple of (updated SharedWorkflowState, list of resolution notes).
        """
        resolution_notes: List[str] = []

        comp_res = state.task_results.get("Compliance Officer")
        risk_res = state.task_results.get("Risk Manager")
        tax_res = state.task_results.get("Tax Specialist")

        # Conflict 1: Compliance Rejection (Strict Override Rule)
        if comp_res and comp_res.recommendation == "REJECT":
            note = "Compliance Officer rejected rebalancing trades. Overriding workflow recommendation to REJECT."
            resolution_notes.append(note)
            state.conflict_flag = True
            state.conflict_notes.append(note)
            return state, resolution_notes

        # Conflict 2: Risk vs Tax Disagreement (Risk recommends MODIFY, Tax recommends APPROVE)
        if risk_res and tax_res:
            if risk_res.recommendation == "MODIFY" and tax_res.recommendation == "APPROVE":
                note = "Risk Manager recommended MODIFY while Tax Specialist recommended APPROVE. Resolving by enforcing Risk position cap while retaining tax loss harvesting."
                resolution_notes.append(note)
                state.conflict_notes.append(note)
                # Adjust Tax Specialist result comments
                tax_res.comments += " (Adjusted for Risk Manager position cap)"

        # Conflict 3: Low Confidence Agent Warning
        low_conf_agents = [r.agent_name for r in state.task_results.values() if r.confidence_score < 0.75]
        if low_conf_agents:
            note = f"Agents with confidence < 0.75 detected: {low_conf_agents}. Flagging for internal advisor review."
            resolution_notes.append(note)
            state.conflict_notes.append(note)

        logger.debug(f"Conflict resolution evaluated. Total resolution notes: {len(resolution_notes)}")
        return state, resolution_notes
