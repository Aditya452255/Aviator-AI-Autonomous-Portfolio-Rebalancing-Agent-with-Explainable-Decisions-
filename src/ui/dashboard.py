"""Dashboard Assembly building and mounting the story-driven Gradio app interface for Aviator AI."""

import time
import gradio as gr

from src.services.dashboard_service import DashboardService
from src.ui.layout import build_header
from src.ui.navigation import TAB_TITLES
from src.ui.tabs.agents_tab import render_agents_tab
from src.ui.tabs.backtesting_tab import render_backtesting_tab
from src.ui.tabs.explainability_tab import render_explainability_tab
from src.ui.tabs.governance_tab import render_governance_tab
from src.ui.tabs.optimization_tab import render_optimization_tab
from src.ui.tabs.overview_tab import render_overview_tab
from src.ui.tabs.portfolio_monitor_tab import render_portfolio_monitor_tab
from src.ui.tabs.system_health_tab import render_system_health_tab
from src.ui.theme import CUSTOM_CSS


def create_dashboard_app(dashboard_service: DashboardService = None) -> gr.Blocks:
    """Build and return the complete Gradio Blocks application.

    Args:
        dashboard_service: Optional DashboardService instance.

    Returns:
        gr.Blocks application object.
    """
    service = dashboard_service or DashboardService()

    with gr.Blocks(title="Aviator AI — Autonomous Portfolio Rebalancing Agent (Final Year Project)", css=CUSTOM_CSS) as app:
        build_header()

        with gr.Row():
            with gr.Column(scale=3):
                demo_status = gr.HTML(
                    value="""
                    <div style="background: rgba(30, 41, 59, 0.6); padding: 12px 18px; border-radius: 8px; border: 1px solid #334155; color: #cbd5e1; font-size: 0.9rem;">
                        💡 <strong>Guided Presentation Demo</strong>: Click <strong>RUN DEMO PORTFOLIO</strong> to execute a live end-to-end multi-phase simulation cycle (Drift ➔ Risk ➔ Optimization ➔ Agents ➔ XAI ➔ Governance ➔ Backtest).
                    </div>
                    """
                )
            with gr.Column(scale=1):
                run_demo_btn = gr.Button("🚀 RUN DEMO PORTFOLIO", variant="primary", elem_classes=["demo-btn"])

        def on_run_demo():
            res = service.run_guided_demo(num_portfolios=10, trading_days=30)
            msg = (
                f"<div style='background: #065f46; padding: 12px 18px; border-radius: 8px; border: 1px solid #34d399; color: #ecfdf5; font-weight: 600; font-size: 0.95rem;'>"
                f"✅ Demo Completed Successfully in {res['duration_sec']} seconds! "
                f"Processed {res['portfolios_processed']} portfolios across all 7 core backend phases. Explore story tabs below."
                f"</div>"
            )
            return msg

        run_demo_btn.click(fn=on_run_demo, inputs=[], outputs=[demo_status])

        with gr.Tabs():
            with gr.Tab(TAB_TITLES["EXECUTIVE"]):
                render_overview_tab(service)

            with gr.Tab(TAB_TITLES["ANALYSIS"]):
                render_portfolio_monitor_tab(service)

            with gr.Tab(TAB_TITLES["REBALANCING"]):
                render_optimization_tab(service)

            with gr.Tab(TAB_TITLES["COUNCIL"]):
                render_agents_tab(service)

            with gr.Tab(TAB_TITLES["EXPLAINABILITY"]):
                render_explainability_tab(service)

            with gr.Tab(TAB_TITLES["GOVERNANCE"]):
                render_governance_tab(service)

            with gr.Tab(TAB_TITLES["BACKTESTING"]):
                render_backtesting_tab(service)

            with gr.Tab(TAB_TITLES["VALIDATION"]):
                render_system_health_tab(service)

    return app
