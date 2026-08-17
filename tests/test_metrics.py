"""Unit tests for PrometheusMetricsManager, ProductionService, and AlertEngine."""

from pathlib import Path
import pytest
from src.observability.alerts import SystemAlertEngine
from src.observability.metrics import PrometheusMetricsManager
from src.services.production_service import ProductionService


def test_prometheus_metrics_and_alerts() -> None:
    """Test Prometheus metrics counters, gauges, and alert generation."""
    mgr = PrometheusMetricsManager()
    mgr.record_portfolio_evaluated(5)
    mgr.record_optimization("OPTIMAL")
    mgr.update_system_gauges(50.0, 60.0, 0.04)

    payload = mgr.export_prometheus_metrics()
    assert b"aviator_ai_portfolios_governed_total" in payload

    alerts_engine = SystemAlertEngine()
    active_alerts = alerts_engine.evaluate_resource_alerts(cpu_pct=95.0, memory_pct=92.0, kill_switch_active=True)
    assert len(active_alerts) == 3


def test_production_service_cycle(tmp_path: Path) -> None:
    """Test full Phase 9 ProductionService health cycle and file exports."""
    service = ProductionService()
    service.output_dir = tmp_path

    reports = service.run_production_health_cycle(save_exports=True)

    assert "health_status" in reports
    assert (tmp_path / "system_metrics.json").exists()
    assert (tmp_path / "performance_report.json").exists()
    assert (tmp_path / "security_report.json").exists()
    assert (tmp_path / "health_status.json").exists()
    assert (tmp_path / "observability_metrics.csv").exists()
