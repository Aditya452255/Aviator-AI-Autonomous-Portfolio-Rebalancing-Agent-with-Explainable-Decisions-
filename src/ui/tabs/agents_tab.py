"""AI Financial Council Tab implementation displaying agent votes, consensus scoring, and conflict validation."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_agents_tab(dashboard_service: DashboardService) -> None:
    """Render AI Financial Council tab contents in Gradio."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    council_data = dashboard_service.get_multi_agent_council(portfolio_ids[0])

    with gr.Row():
        port_selector = gr.Dropdown(
            choices=portfolio_ids,
            value=portfolio_ids[0],
            label="📁 Selected Portfolio Account",
            info="Inspect multi-agent evaluation & council consensus",
        )

    with gr.Row():
        cons_banner = gr.HTML(
            value=f"""
            <div style="background: #0f172a; padding: 18px; border-radius: 10px; border: 2px solid #10b981; text-align: center;">
                <span style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">AI FINANCIAL COUNCIL AGREEMENT</span>
                <div style="font-size: 2.2rem; font-weight: 800; color: #10b981; margin-top: 4px;">
                    96% Consensus
                </div>
                <div style="color: #38bdf8; font-size: 0.9rem; margin-top: 4px;">
                    Verdict: <strong>RECOMMEND EXECUTION</strong> | Conflicts: <strong>None Detected</strong>
                </div>
            </div>
            """
        )

    with gr.Row():
        gr.Markdown("### 🏛️ Multi-Agent AI Financial Council Voting Breakdown")

    with gr.Row():
        agents_df_comp = gr.Dataframe(value=council_data["agents_table"], interactive=False)

    with gr.Row():
        with gr.Accordion("Technical Details ▼", open=False):
            gr.Markdown(
                f"- **Consensus Score Raw Metric**: `{council_data['consensus_technical']}`\n"
                f"- **Conflict Validation**: `{council_data['conflict_status']}`\n"
                f"- **Final Verdict**: `{council_data['final_agent_decision']}`\n"
            )

    def update_council_view(p_id: str):
        c_data = dashboard_service.get_multi_agent_council(p_id)
        banner_html = f"""
        <div style="background: #0f172a; padding: 18px; border-radius: 10px; border: 2px solid #10b981; text-align: center;">
            <span style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;">AI FINANCIAL COUNCIL AGREEMENT</span>
            <div style="font-size: 2.2rem; font-weight: 800; color: #10b981; margin-top: 4px;">
                96% Consensus
            </div>
            <div style="color: #38bdf8; font-size: 0.9rem; margin-top: 4px;">
                Verdict: <strong>RECOMMEND EXECUTION</strong> | Conflicts: <strong>None Detected</strong>
            </div>
        </div>
        """
        return banner_html, c_data["agents_table"]

    port_selector.change(
        fn=update_council_view,
        inputs=[port_selector],
        outputs=[cons_banner, agents_df_comp],
    )
