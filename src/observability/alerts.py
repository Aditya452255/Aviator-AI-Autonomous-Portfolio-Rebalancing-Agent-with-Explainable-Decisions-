"""System Alert Engine generating operational alerts for high CPU, memory, or kill switch events."""

from typing import Dict, List, Optional
from src.core.logger import get_logger

logger = get_logger(__name__)


class SystemAlertEngine:
    """Enterprise System Alert Engine."""

    def __init__(self) -> None:
        self.active_alerts: List[Dict[str, str]] = []

    def evaluate_resource_alerts(self, cpu_pct: float, memory_pct: float, kill_switch_active: bool = False) -> List[Dict[str, str]]:
        """Evaluate resource metrics and generate active alerts.

        Args:
            cpu_pct: CPU percentage.
            memory_pct: Memory percentage.
            kill_switch_active: True if Kill Switch active.

        Returns:
            List of generated alert dicts.
        """
        alerts = []
        if cpu_pct >= 90.0:
            alerts.append({"alert_type": "HIGH_CPU_USAGE", "severity": "WARNING", "message": f"CPU usage ({cpu_pct:.1f}%) exceeds 90% threshold."})
        if memory_pct >= 90.0:
            alerts.append({"alert_type": "HIGH_MEMORY_USAGE", "severity": "WARNING", "message": f"Memory usage ({memory_pct:.1f}%) exceeds 90% threshold."})
        if kill_switch_active:
            alerts.append({"alert_type": "KILL_SWITCH_ACTIVE", "severity": "CRITICAL", "message": "Enterprise Kill Switch is currently active!"})

        for a in alerts:
            logger.warning(f"ALERT GENERATED [{a['alert_type']}] | Severity: {a['severity']} | {a['message']}")

        self.active_alerts.extend(alerts)
        return alerts
