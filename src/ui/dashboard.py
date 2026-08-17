"""Dashboard Assembly building and mounting the 10-tab Gradio app interface."""

import gradio as gr

from src.services.dashboard_service import DashboardService
from src.ui.layout import build_header
from src.ui.navigation import TAB_TITLES
from src.ui.tabs.agents_tab import render_agents_tab
from src.ui.tabs.analytics_tab import render_analytics_tab
from src.ui.tabs.backtesting_tab import render_backtesting_tab
from src.ui.tabs.explainability_tab import render_explainability_tab
from src.ui.tabs.governance_tab import render_governance_tab
from src.ui.tabs.optimization_tab import render_optimization_tab
from src.ui.tabs.overview_tab import render_overview_tab
from src.ui.tabs.portfolio_monitor_tab import render_portfolio_monitor_tab
from src.ui.tabs.system_health_tab import render_system_health_tab
from src.ui.tabs.trade_execution_tab import render_trade_execution_tab
from src.ui.theme import CUSTOM_CSS


def create_dashboard_app(dashboard_service: DashboardService = None) -> gr.Blocks:
    """Build and return the complete Gradio Blocks application.

    Args:
        dashboard_service: Optional DashboardService instance.

    Returns:
        gr.Blocks application object.
    """
    service = dashboard_service or DashboardService()

    with gr.Blocks(title="Aviator AI — Enterprise Operations Dashboard", css=CUSTOM_CSS) as app:
        build_header()

        with gr.Tabs():
            with gr.Tab(TAB_TITLES["OVERVIEW"]):
                render_overview_tab(service)

            with gr.Tab(TAB_TITLES["PORTFOLIO_MONITOR"]):
                render_portfolio_monitor_tab(service)

            with gr.Tab(TAB_TITLES["OPTIMIZATION"]):
                render_optimization_tab(service)

            with gr.Tab(TAB_TITLES["TRADE_EXECUTION"]):
                render_trade_execution_tab(service)

            with gr.Tab(TAB_TITLES["MULTI_AGENT"]):
                render_agents_tab(service)

            with gr.Tab(TAB_TITLES["EXPLAINABILITY"]):
                render_explainability_tab(service)

            with gr.Tab(TAB_TITLES["GOVERNANCE"]):
                render_governance_tab(service)

            with gr.Tab(TAB_TITLES["BACKTESTING"]):
                render_backtesting_tab(service)

            with gr.Tab(TAB_TITLES["ANALYTICS"]):
                render_analytics_tab(service)

            with gr.Tab(TAB_TITLES["SYSTEM_HEALTH"]):
                render_system_health_tab(service)

    return app
