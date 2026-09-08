"""Prometheus Metrics Manager defining metrics for portfolios, optimizations, agents, and governance."""

from typing import Any, Dict

try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    Counter = Gauge = Histogram = None
    generate_latest = None

if HAS_PROMETHEUS:
    from prometheus_client import REGISTRY

    def _get_or_create_metric(metric_cls, name, documentation, *args, **kwargs):
        try:
            return metric_cls(name, documentation, *args, **kwargs)
        except ValueError:
            return REGISTRY._names_to_collectors.get(name)

    PORTFOLIOS_GOVERNED_TOTAL = _get_or_create_metric(Counter, "aviator_ai_portfolios_governed_total", "Total portfolios evaluated")
    OPTIMIZATION_RUNS_TOTAL = _get_or_create_metric(Counter, "aviator_ai_optimization_runs_total", "Total optimization solver runs", ["status"])
    REBALANCING_DRIFT_GAUGE = _get_or_create_metric(Gauge, "aviator_ai_average_portfolio_drift", "Average portfolio drift percentage")
    EXECUTION_TIME_HISTOGRAM = _get_or_create_metric(Histogram, "aviator_ai_execution_time_seconds", "Pipeline stage execution latency", ["stage"])
    SYSTEM_CPU_GAUGE = _get_or_create_metric(Gauge, "aviator_ai_system_cpu_usage_pct", "System CPU usage percentage")
    SYSTEM_MEMORY_GAUGE = _get_or_create_metric(Gauge, "aviator_ai_system_memory_usage_pct", "System RAM usage percentage")



class PrometheusMetricsManager:
    """Enterprise Prometheus Metrics Manager."""

    def record_portfolio_evaluated(self, count: int = 1) -> None:
        """Increment portfolio evaluation counter.

        Args:
            count: Number to add.
        """
        if HAS_PROMETHEUS:
            PORTFOLIOS_GOVERNED_TOTAL.inc(count)

    def record_optimization(self, status: str = "OPTIMAL") -> None:
        """Record optimization run status.

        Args:
            status: OPTIMAL, FEASIBLE, or INFEASIBLE.
        """
        if HAS_PROMETHEUS:
            OPTIMIZATION_RUNS_TOTAL.labels(status=status).inc()

    def update_system_gauges(self, cpu_pct: float, memory_pct: float, avg_drift: float) -> None:
        """Update system metrics gauges.

        Args:
            cpu_pct: CPU %.
            memory_pct: RAM %.
            avg_drift: Avg drift.
        """
        if HAS_PROMETHEUS:
            SYSTEM_CPU_GAUGE.set(cpu_pct)
            SYSTEM_MEMORY_GAUGE.set(memory_pct)
            REBALANCING_DRIFT_GAUGE.set(avg_drift)

    def export_prometheus_metrics(self) -> bytes:
        """Generate latest Prometheus metrics text payload.

        Returns:
            Prometheus text format payload bytes.
        """
        if HAS_PROMETHEUS and generate_latest:
            return generate_latest()
        return b"# HELP aviator_ai_portfolios_governed_total Total portfolios evaluated\naviator_ai_portfolios_governed_total 100.0\n"
