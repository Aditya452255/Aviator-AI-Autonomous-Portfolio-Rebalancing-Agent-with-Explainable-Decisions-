"""Analytics Tab implementation displaying portfolio distribution and risk heatmaps."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.risk_chart import build_risk_distribution_chart


def render_analytics_tab(dashboard_service: DashboardService) -> None:
    """Render the Portfolio Analytics tab contents in Gradio."""
    gr.Markdown("### 📊 Enterprise Portfolio Risk & Sector Analytics")
    with gr.Row():
        with gr.Column():
            build_risk_distribution_chart()
        with gr.Column():
            gr.Markdown("#### 🗺️ Sector & Asset Class Exposure Summary")
            gr.Markdown(
                "- **Financial Services**: 28.5%\n"
                "- **Technology & IT**: 22.1%\n"
                "- **Consumer Goods**: 15.4%\n"
                "- **Energy & Power**: 12.0%\n"
                "- **Healthcare**: 11.2%\n"
                "- **Fixed Income & Cash**: 10.8%\n"
            )
