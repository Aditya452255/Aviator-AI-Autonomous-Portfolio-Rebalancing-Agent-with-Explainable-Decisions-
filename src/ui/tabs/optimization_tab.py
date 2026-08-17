"""Optimization Tab implementation displaying convex optimization and cost breakdown."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.portfolio_table import build_portfolio_data_table


def render_optimization_tab(dashboard_service: DashboardService) -> None:
    """Render the Optimization tab contents in Gradio."""
    df_opt = dashboard_service.load_optimization_data()

    gr.Markdown("### ⚡ Convex Portfolio Optimization Results")
    build_portfolio_data_table(df_opt)

    gr.Markdown("### 📐 Constraint & Cost Summary")
    gr.Markdown(
        "- **Constraint Enforcement**: Sector Limits (max 30%), Single Asset Max (15%), Cash Reserve (min 2%)\n"
        "- **Primary Solver**: CVXPY ECOS (Fallback: SciPy SLSQP)\n"
        "- **Tax Loss Harvesting**: STCG/LTCG matching active\n"
    )
