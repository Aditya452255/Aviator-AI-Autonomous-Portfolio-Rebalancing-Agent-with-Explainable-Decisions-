"""Resource Monitor tracking CPU, memory, and disk usage via psutil."""

from typing import Dict
import psutil


class ResourceMonitor:
    """Enterprise Resource Monitor tracking hardware resource usage."""

    def get_resource_usage(self) -> Dict[str, float]:
        """Fetch current hardware resource statistics.

        Returns:
            Dictionary of resource usage percentages and memory MBs.
        """
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": mem.percent,
            "memory_used_mb": round(mem.used / (1024 * 1024), 2),
            "memory_total_mb": round(mem.total / (1024 * 1024), 2),
        }
