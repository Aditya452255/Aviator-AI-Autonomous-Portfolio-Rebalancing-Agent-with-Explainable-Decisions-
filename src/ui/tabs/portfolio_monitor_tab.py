"""Portfolio Monitor Tab implementation for real-time drift search and allocation breakdown."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.allocation_chart import build_allocation_chart
from src.ui.components.portfolio_table import build_portfolio_data_table


def render_portfolio_monitor_tab(dashboard_service: DashboardService) -> None:
    """Render the Portfolio Monitor tab contents in Gradio."""
    df_port = dashboard_service.load_portfolio_data()

    gr.Markdown("### 🔍 Portfolio Drift & Allocation Monitor")
    with gr.Row():
        search_bar = gr.Textbox(placeholder="Search by Portfolio ID or Risk Category...", label="Portfolio Search")

    with gr.Row():
        with gr.Column(scale=2):
            table = build_portfolio_data_table(df_port)
        with gr.Column(scale=1):
            build_allocation_chart()
