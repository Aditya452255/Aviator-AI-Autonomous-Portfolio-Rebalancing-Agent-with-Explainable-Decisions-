"""Overview Tab implementation for executive status and KPI summary."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.metric_cards import build_kpi_card
from src.ui.components.performance_chart import build_performance_comparison_chart


def render_overview_tab(dashboard_service: DashboardService) -> None:
    """Render the Executive Overview tab contents in Gradio."""
    data = dashboard_service.load_overview_data()

    with gr.Row():
        build_kpi_card("Portfolios Governed", str(data["total_portfolios"]), "50,000 Total Account Target")
        build_kpi_card("Approval Pass Rate", data["approval_rate"], "Policy Compliant")
        build_kpi_card("Advisor Override Rate", data["override_rate"], "Low Advisor Interventions")
        build_kpi_card("Kill Switch Status", "OFF" if not data["kill_switch_active"] else "ACTIVE", "System Nominal")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📈 Cumulative Performance & Rebalancing Alpha")
            build_performance_comparison_chart()
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ System Metrics Summary")
            gr.Markdown(
                f"- **Optimization Success Rate**: {data['optimization_success_rate']}\n"
                f"- **Mean Agent Consensus**: {data['mean_consensus']}\n"
                f"- **Escalation Rate**: {data['escalation_rate']}\n"
                f"- **Active Risk Models**: CVXPY ECOS + SciPy SLSQP\n"
                f"- **Explainability Engines**: TreeSHAP + LIME Tabular\n"
            )
