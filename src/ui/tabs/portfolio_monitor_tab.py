"""Portfolio Analysis Tab implementation for asset allocation breakdown, drift analysis, and risk findings."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_portfolio_monitor_tab(dashboard_service: DashboardService) -> None:
    """Render Portfolio Analysis tab contents in Gradio."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    details = dashboard_service.get_portfolio_details(portfolio_ids[0])
    analysis = dashboard_service.get_portfolio_analysis(portfolio_ids[0])

    with gr.Row():
        port_selector = gr.Dropdown(
            choices=portfolio_ids,
            value=portfolio_ids[0],
            label="📁 Selected Portfolio Account",
            info="Inspect asset class allocation drift & risk findings",
        )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Asset Allocation Breakdown: Current vs Target vs Proposed")
            alloc_chart = gr.Plot(
                value=dashboard_service.create_allocation_comparison_chart(
                    details["current_allocation"], details["target_allocation"], details["proposed_allocation"]
                )
            )

        with gr.Column(scale=1):
            gr.Markdown("### 📋 Asset Class Allocation & Drift Table")
            drift_table_comp = gr.Dataframe(value=analysis["drift_table"], interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📈 Asset Drift Cards")
            gr.HTML(
                value="""
                <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="flex: 1; background: #991b1b; padding: 12px; border-radius: 8px; color: #fca5a5; text-align: center;">
                        <strong style="font-size: 0.85rem; text-transform: uppercase;">OVERWEIGHT ASSET</strong>
                        <div style="font-size: 1.3rem; font-weight: 700; margin-top: 4px;">Equity: +6.8%</div>
                    </div>
                    <div style="flex: 1; background: #1e3a8a; padding: 12px; border-radius: 8px; color: #93c5fd; text-align: center;">
                        <strong style="font-size: 0.85rem; text-transform: uppercase;">UNDERWEIGHT ASSET</strong>
                        <div style="font-size: 1.3rem; font-weight: 700; margin-top: 4px;">Fixed Income: -6.8%</div>
                    </div>
                </div>
                """
            )

        with gr.Column(scale=1):
            gr.Markdown("### ⚠️ Risk Findings & Diagnosis")
            risk_text = gr.Markdown("\n".join(analysis["risk_findings"]))

    def update_analysis_view(p_id: str):
        det = dashboard_service.get_portfolio_details(p_id)
        an = dashboard_service.get_portfolio_analysis(p_id)
        fig = dashboard_service.create_allocation_comparison_chart(det["current_allocation"], det["target_allocation"], det["proposed_allocation"])
        return fig, an["drift_table"], "\n".join(an["risk_findings"])

    port_selector.change(
        fn=update_analysis_view,
        inputs=[port_selector],
        outputs=[alloc_chart, drift_table_comp, risk_text],
    )
