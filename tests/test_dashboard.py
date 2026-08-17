"""Unit tests for DashboardService and Gradio dashboard assembly."""

import gradio as gr
import pytest
from src.services.dashboard_service import DashboardService
from src.ui.dashboard import create_dashboard_app


def test_dashboard_service_data_loading() -> None:
    """Test loading data structures in DashboardService."""
    service = DashboardService()

    overview = service.load_overview_data()
    assert isinstance(overview, dict)
    assert "total_portfolios" in overview

    df_port = service.load_portfolio_data()
    assert not df_port.empty

    df_opt = service.load_optimization_data()
    assert not df_opt.empty

    df_trades = service.load_trade_execution_data()
    assert not df_trades.empty

    df_agents = service.load_agents_data()
    assert not df_agents.empty

    df_feat = service.load_explainability_data()
    assert not df_feat.empty

    df_app, df_ovr, df_aud = service.load_governance_data()
    assert df_app is not None

    df_strat, df_bench = service.load_backtesting_data()
    assert df_strat is not None


def test_create_dashboard_app() -> None:
    """Test creating Gradio Blocks application."""
    app = create_dashboard_app()
    assert isinstance(app, gr.Blocks)
