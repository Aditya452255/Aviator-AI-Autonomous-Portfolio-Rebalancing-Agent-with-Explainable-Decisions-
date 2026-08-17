"""Rebalancing Queue Manager generating and validating downstream optimization requests."""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.models.drift import PortfolioDriftMetrics
from src.models.portfolio import Portfolio
from src.models.rebalancing_request import PriorityLevel, QueueStatus, RebalancingRequest
from src.models.trigger import TriggerEvaluation, TriggerReason, TriggerType

logger = get_logger(__name__)


class RebalancingQueueManager:
    """Enterprise manager constructing, validating, and prioritizing the rebalancing queue."""

    def __init__(self) -> None:
        self.queue: List[RebalancingRequest] = []

    def create_request(
        self,
        portfolio: Portfolio,
        metrics: PortfolioDriftMetrics,
        priority: PriorityLevel,
        priority_score: float,
        triggers: List[TriggerEvaluation],
    ) -> RebalancingRequest:
        """Construct a validated RebalancingRequest object for a portfolio.

        Args:
            portfolio: Portfolio instance.
            metrics: Calculated PortfolioDriftMetrics.
            priority: PriorityLevel enum.
            priority_score: Priority score fraction.
            triggers: List of fired TriggerEvaluation objects.

        Returns:
            RebalancingRequest instance.
        """
        primary_trigger = triggers[0] if triggers else None
        t_type = primary_trigger.trigger_type if primary_trigger else TriggerType.THRESHOLD
        t_reason = primary_trigger.trigger_reason if primary_trigger else TriggerReason.EQUITY_DRIFT_BREACH
        all_reasons = [t.trigger_reason.value for t in triggers] if triggers else [t_reason.value]

        req_id = f"REQ_{len(self.queue) + 1:05d}"
        now_str = datetime.now().isoformat()

        drift_summary = {
            "total_absolute_drift": metrics.total_absolute_drift,
            "portfolio_drift_score": metrics.portfolio_drift_score,
            "max_drift_asset_class": metrics.max_drift_asset_class,
            "max_drift_value": metrics.max_drift_value,
            "cash_drift": metrics.cash_drift,
        }

        req = RebalancingRequest(
            request_id=req_id,
            portfolio_id=portfolio.portfolio_id,
            client_id=portfolio.client_id,
            priority=priority,
            priority_score=priority_score,
            trigger_type=t_type,
            trigger_reason=t_reason,
            all_triggers=all_reasons,
            drift_summary=drift_summary,
            timestamp=now_str,
            validation_status=True,
            queue_status=QueueStatus.VALIDATED,
        )

        return req

    def enqueue_request(self, request: RebalancingRequest) -> None:
        """Add request to queue if not a duplicate.

        Args:
            request: RebalancingRequest instance.
        """
        # Deduplication check
        existing_port_ids = {r.portfolio_id for r in self.queue}
        if request.portfolio_id in existing_port_ids:
            logger.debug(f"Skipping duplicate rebalancing request for portfolio {request.portfolio_id}")
            return
        self.queue.append(request)

    def sort_by_priority(self) -> List[RebalancingRequest]:
        """Sort queue entries by priority score descending.

        Returns:
            Sorted list of RebalancingRequest entries.
        """
        self.queue.sort(key=lambda x: x.priority_score, reverse=True)
        return self.queue

    def validate_queue(self) -> bool:
        """Validate queue entries for completeness and deduplication.

        Returns:
            True if all queue validation checks pass.

        Raises:
            ValidationError: If any queue entry is invalid.
        """
        seen_pids = set()
        for req in self.queue:
            if req.portfolio_id in seen_pids:
                raise ValidationError(f"Duplicate portfolio ID in queue: {req.portfolio_id}")
            seen_pids.add(req.portfolio_id)

            if not req.portfolio_id or not req.client_id:
                raise ValidationError("Queue request missing portfolio_id or client_id")

            if req.priority_score < 0.0 or req.priority_score > 1.0:
                raise ValidationError(f"Invalid priority score {req.priority_score} in request {req.request_id}")

        return True

    def to_dataframe(self) -> pd.DataFrame:
        """Convert queue entries to tabular pandas DataFrame.

        Returns:
            DataFrame representation of the rebalancing queue.
        """
        rows = [r.model_dump() for r in self.queue]
        df = pd.DataFrame(rows)
        if not df.empty and "all_triggers" in df.columns:
            df["all_triggers"] = df["all_triggers"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            df["drift_summary_json"] = df["drift_summary"].apply(lambda x: str(x))
        return df
