"""System Monitoring Loop updating Prometheus metrics and tracking resources."""

from typing import Dict, Optional
import psutil
from src.observability.metrics import PrometheusMetricsManager


class SystemMonitoringLoop:
    """Enterprise System Monitoring Loop."""

    def __init__(self, metrics_manager: Optional[PrometheusMetricsManager] = None) -> None:
        self.metrics = metrics_manager or PrometheusMetricsManager()

    def collect_metrics_snapshot(self) -> Dict[str, float]:
        """Collect snapshot of system resources and update Prometheus gauges.

        Returns:
            Dictionary of metrics.
        """
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        self.metrics.update_system_gauges(cpu_pct=cpu, memory_pct=mem, avg_drift=0.052)
        return {"cpu_percent": cpu, "memory_percent": mem}
