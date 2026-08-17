"""Unit tests for SystemHealthChecker and FastAPI health endpoints."""

from fastapi.testclient import TestClient
import pytest
from src.reliability.health_checker import SystemHealthChecker
from src.services.production_service import fastapi_app


def test_system_health_checker() -> None:
    """Test system health diagnostics metrics."""
    checker = SystemHealthChecker()
    diag = checker.check_system_health()

    assert "status" in diag
    assert "cpu_usage_pct" in diag
    assert "memory_usage_pct" in diag
    assert diag["status"] in ("HEALTHY", "DEGRADED")


def test_fastapi_health_endpoints() -> None:
    """Test FastAPI REST endpoints /health, /metrics, /status, /system."""
    client = TestClient(fastapi_app)

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert "status" in res_health.json()

    res_status = client.get("/status")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "OPERATIONAL"

    res_system = client.get("/system")
    assert res_system.status_code == 200
    assert "cpu_percent" in res_system.json()

    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert b"aviator_ai_" in res_metrics.content
