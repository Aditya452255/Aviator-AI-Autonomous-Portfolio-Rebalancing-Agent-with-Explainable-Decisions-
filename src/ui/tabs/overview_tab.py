"""Executive Dashboard Tab implementation providing clear portfolio status and plain-English narrative."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_overview_tab(dashboard_service: DashboardService) -> None:
    """Render Executive Dashboard tab."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    details = dashboard_service.get_portfolio_details(portfolio_ids[0])

    with gr.Row():
        with gr.Column(scale=1):
            portfolio_selector = gr.Dropdown(
                choices=portfolio_ids,
                value=portfolio_ids[0],
                label="📁 Select Investor Portfolio Account",
                info="Selecting a portfolio updates all 8 tabs across the system",
            )

    with gr.Row():
        status_banner = gr.HTML(
            value=f"""
            <div style="background: #0f172a; padding: 20px; border-radius: 10px; border: 2px solid {details['status_color']}; text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 800; color: {details['status_color']};">
                    🚨 {details['rebalancing_status']}
                </div>
                <div style="font-size: 1.1rem; color: #f8fafc; margin-top: 8px; font-weight: 600;">
                    Current Portfolio Drift: <span style="color: #f59e0b;">{details['current_drift_pct']}</span> &nbsp;|&nbsp; 
                    Allowed Drift: <span style="color: #60a5fa;">{details['allowed_drift']}</span> &nbsp;&nbsp;
                    <span style="background: #334155; padding: 2px 8px; border-radius: 6px; font-size: 0.9rem;">({details['current_drift_pct']} &gt; {details['allowed_drift']})</span>
                </div>
            </div>
            """
        )

    with gr.Row():
        val_card = gr.Textbox(value=details["portfolio_value_formatted"], label="Total Portfolio Value", interactive=False)
        client_card = gr.Textbox(value=details["client_name"], label="Investor Account Profile", interactive=False)
        risk_card = gr.Textbox(value=details["risk_profile"], label="Target Risk Profile", interactive=False)
        drift_card = gr.Textbox(value=details["current_drift_pct"], label="Current Portfolio Drift", interactive=False)
        thresh_card = gr.Textbox(value=details["allowed_drift"], label="Allowed Drift", interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Plain-English Portfolio Condition Summary")
            narrative_box = gr.Textbox(
                value=details["narrative"],
                lines=3,
                label="Condition Assessment",
                interactive=False,
            )
            gr.Markdown("### 💡 Recommended System Action")
            action_box = gr.Textbox(
                value=details["recommended_action"],
                lines=2,
                label="Calculated Trade Directive",
                interactive=False,
            )

        with gr.Column(scale=1):
            gr.Markdown("### 📊 Current vs Target Allocation Breakdown")
            donut_chart = gr.Plot(value=dashboard_service.create_allocation_donut_chart(details["current_allocation"], details["target_allocation"]))

    def update_portfolio_view(port_id: str):
        det = dashboard_service.get_portfolio_details(port_id)
        banner_html = f"""
        <div style="background: #0f172a; padding: 20px; border-radius: 10px; border: 2px solid {det['status_color']}; text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 800; color: {det['status_color']};">
                🚨 {det['rebalancing_status']}
            </div>
            <div style="font-size: 1.1rem; color: #f8fafc; margin-top: 8px; font-weight: 600;">
                Current Portfolio Drift: <span style="color: #f59e0b;">{det['current_drift_pct']}</span> &nbsp;|&nbsp; 
                Allowed Drift: <span style="color: #60a5fa;">{det['allowed_drift']}</span> &nbsp;&nbsp;
                <span style="background: #334155; padding: 2px 8px; border-radius: 6px; font-size: 0.9rem;">({det['current_drift_pct']} &gt; {det['allowed_drift']})</span>
            </div>
        </div>
        """
        fig = dashboard_service.create_allocation_donut_chart(det["current_allocation"], det["target_allocation"])
        return (
            det["portfolio_value_formatted"],
            det["client_name"],
            det["risk_profile"],
            det["current_drift_pct"],
            det["allowed_drift"],
            banner_html,
            det["narrative"],
            det["recommended_action"],
            fig,
        )

    portfolio_selector.change(
        fn=update_portfolio_view,
        inputs=[portfolio_selector],
        outputs=[val_card, client_card, risk_card, drift_card, thresh_card, status_banner, narrative_box, action_box, donut_chart],
    )
