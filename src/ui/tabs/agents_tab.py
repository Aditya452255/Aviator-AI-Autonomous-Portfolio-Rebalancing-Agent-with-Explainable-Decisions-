"""Multi-Agent Tab implementation displaying workflow topology and agent consensus packages."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.portfolio_table import build_portfolio_data_table


def render_agents_tab(dashboard_service: DashboardService) -> None:
    """Render the Multi-Agent Intelligence tab contents in Gradio."""
    df_agents = dashboard_service.load_agents_data()

    gr.Markdown("### 🤖 Multi-Agent Decision Intelligence Topology")
    gr.Markdown(
        "```\n"
        "Portfolio Arrives -> Portfolio Analyst -> Risk Manager -> Tax Specialist -> Compliance Officer -> Explanation Writer -> Orchestrator -> Final Decision Package\n"
        "```"
    )

    gr.Markdown("### 📋 Agent Decision Packages & Consensus Ratings")
    build_portfolio_data_table(df_agents)
