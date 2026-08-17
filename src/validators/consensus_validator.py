"""Consensus Validator evaluating agent recommendation agreement and alignment score."""

from typing import Dict, List
from src.core.logger import get_logger
from src.memory.agent_context import TaskResult

logger = get_logger(__name__)


class ConsensusValidator:
    """Enterprise consensus validator scoring agent recommendation agreement."""

    def compute_consensus_score(self, task_results: Dict[str, TaskResult]) -> float:
        """Calculate normalized multi-agent consensus score (0.0 to 1.0).

        Args:
            task_results: Dictionary of agent_name -> TaskResult.

        Returns:
            Consensus score float (0.0 = total conflict, 1.0 = full consensus).
        """
        if not task_results:
            return 1.0

        recs = [r.recommendation for r in task_results.values()]
        if not recs:
            return 1.0

        # Most common recommendation count
        rec_counts: Dict[str, int] = {}
        for r in recs:
            rec_counts[r] = rec_counts.get(r, 0) + 1

        majority_count = max(rec_counts.values())
        consensus = float(majority_count / len(recs))

        # Penalty if Compliance Officer rejected
        comp_res = task_results.get("Compliance Officer")
        if comp_res and comp_res.recommendation == "REJECT":
            consensus *= 0.5

        return round(consensus, 4)
