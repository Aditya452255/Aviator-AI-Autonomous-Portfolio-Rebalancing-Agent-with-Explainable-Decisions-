"""Rebalancing & Optimization Tab implementation showing recommended trade execution pipeline and constraints."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_optimization_tab(dashboard_service: DashboardService) -> None:
    """Render Rebalancing & Optimization tab contents."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    details = dashboard_service.get_portfolio_details(portfolio_ids[0])
    reb = dashboard_service.get_rebalancing_decision(portfolio_ids[0])

    with gr.Row():
        port_selector = gr.Dropdown(
            choices=portfolio_ids,
            value=portfolio_ids[0],
            label="📁 Selected Portfolio Account",
            info="Inspect proposed target allocation weights & calculated trade recommendations",
        )

    with gr.Row():
        pipeline_html = gr.HTML(
            value="""
            <div style="background: #0f172a; padding: 14px 20px; border-radius: 10px; border: 1px solid #334155; text-align: center; font-weight: 600; color: #38bdf8;">
                REBALANCING PIPELINE: 
                <span style="color: #f59e0b;">1. Drift Detected (6.8%)</span> ➔ 
                <span style="color: #60a5fa;">2. Risk Analyzed (VaR Exceeded)</span> ➔ 
                <span style="color: #a78bfa;">3. Convex Optimization Solved</span> ➔ 
                <span style="color: #34d399;">4. Recommended Trades Calculated</span>
            </div>
            """
        )

    with gr.Row():
        gr.Markdown("### 🛒 What should Aviator change? — Recommended Trade Orders")

    with gr.Row():
        trades_df_comp = gr.Dataframe(value=reb["trades_table"], interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Target Allocation Adjustments")
            chart_comp = gr.Plot(
                value=dashboard_service.create_allocation_comparison_chart(
                    details["current_allocation"], details["target_allocation"], reb["proposed_allocation"]
                )
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎯 Optimization Objective & Constraints")
            obj_box = gr.Textbox(value=reb["optimization_objective"], label="Optimization Objective", interactive=False)
            constraints_box = gr.Markdown("\n".join([f"• {c}" for c in reb["constraints"]]))

            with gr.Accordion("Technical Details ▼", open=False):
                tech_details = reb["technical_details"]
                gr.Markdown(
                    f"- **Portfolio ID**: `{tech_details['Internal Portfolio ID']}`\n"
                    f"- **Solver Algorithm**: `{tech_details['Solver Engine']}`\n"
                    f"- **Execution Time**: `{tech_details['Execution Time']}`\n"
                    f"- **Primal/Dual Feasibility**: `{tech_details['Primal/Dual Feasibility']}`\n"
                    f"- **Estimated Tax Impact**: `{tech_details['Estimated Tax Impact']}`\n"
                    f"- **Solver Status**: `{reb['solver_status']}`\n"
                )

    def update_optimization_view(p_id: str):
        det = dashboard_service.get_portfolio_details(p_id)
        re_data = dashboard_service.get_rebalancing_decision(p_id)
        fig = dashboard_service.create_allocation_comparison_chart(det["current_allocation"], det["target_allocation"], re_data["proposed_allocation"])
        cons_text = "\n".join([f"• {c}" for c in re_data["constraints"]])
        return re_data["trades_table"], fig, re_data["optimization_objective"], cons_text

    port_selector.change(
        fn=update_optimization_view,
        inputs=[port_selector],
        outputs=[trades_df_comp, chart_comp, obj_box, constraints_box],
    )
